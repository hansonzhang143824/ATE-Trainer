const SESSION_KEY_PREFIX = 'ptc-native-session:';

function requireOk(result, operation) {
  if (!result?.ok) throw new Error(result?.error?.message ?? `${operation} failed`);
  return result.value;
}

function existingSessionId(key) {
  try { return window.localStorage.getItem(`${SESSION_KEY_PREFIX}${key}`); }
  catch { return null; }
}

function rememberSessionId(key, sessionId) {
  try { window.localStorage.setItem(`${SESSION_KEY_PREFIX}${key}`, sessionId); }
  catch { /* Session still opens; it will simply not be reused after refresh. */ }
}

function sessionPreset(binding) {
  const session = binding?.session ?? binding;
  const events = Array.isArray(session?.events) ? session.events : [];
  for (let i = events.length - 1; i >= 0; i -= 1) {
    if (events[i]?.type === 'agent-preset/selected') return events[i].data?.agentPreset;
  }
  return session?.header?.agentPreset;
}

function waitForBinding(sessions, sessionId) {
  const ready = sessions.binding(sessionId);
  if (ready !== undefined) return Promise.resolve(ready);
  return new Promise((resolve, reject) => {
    const timeout = window.setTimeout(() => {
      unsubscribe();
      reject(new Error('DSH 创建了会话，但 60 秒内没有出现在会话列表中。'));
    }, 60_000);
    const unsubscribe = sessions.list.subscribe(() => {
      const binding = sessions.binding(sessionId);
      if (binding === undefined) return;
      window.clearTimeout(timeout);
      unsubscribe();
      resolve(binding);
    });
  });
}

export async function openPtcSessionView(scope, sessionId) {
  await scope.sessions.open(sessionId);
  const snapshot = scope.sessions.list?.getSnapshot?.();
  if (snapshot && snapshot.current !== sessionId) {
    throw new Error('OPEN_FAILED: DSH 没有选中请求的原生会话');
  }
}

/** Create or reopen a genuine DSH conversation rooted in its server-approved workspace. */
export async function openPtcNativeSession(scope, workspace, {
  key, title, agentPreset = 'standard', rememberedSessionId, validateRemembered, beforeOpen,
}) {
  const api = typeof scope?.get === 'function' ? scope.get('connection')?.api : scope?.connection?.api;
  if (!api?.sessions?.create || !scope?.sessions) {
    throw new Error('DSH 原生会话服务尚未注入；请确认本机 DSH 已加载会话与工作区服务。');
  }
  const remembered = rememberedSessionId || existingSessionId(key);
  if (remembered) {
    const rememberedBinding = scope.sessions.binding(remembered);
    if (rememberedBinding !== undefined && sessionPreset(rememberedBinding) === agentPreset
      && (!validateRemembered || await validateRemembered(remembered))) {
      await beforeOpen?.(remembered, true);
      await openPtcSessionView(scope, remembered);
      return { sessionId: remembered, reused: true };
    }
    try { window.localStorage.removeItem(`${SESSION_KEY_PREFIX}${key}`); } catch { /* stale mapping is disposable */ }
  }

  const cwd = workspace?.cwd || workspace?.path;
  if (typeof cwd !== 'string' || !cwd) throw new Error('Trainer 没有返回可用的原生会话 cwd');
  // DSH's session.create contract accepts either a registered workspaceId or
  // an absolute cwd.  The web host used by this plugin exposes the latter;
  // workspace.create is not available in that profile and returns HTTP 404.
  // Let the Host resolve and validate the preset.  Some DSH web profiles
  // intentionally omit the optional agentPreset.list route while session.create
  // still accepts the requested preset.
  const created = requireOk((await api.sessions.create({ cwd, agentPreset })).result, '创建 DSH 会话');
  if (typeof created?.sessionId !== 'string' || !created.sessionId) throw new Error('DSH 没有返回 sessionId');
  // The low-level API create call does not update the client SessionRuntime's
  // list store.  Refresh it before waiting for binding(), otherwise a valid
  // server-created session can remain locally unaddressable until the bridge
  // timeout expires.  DSH's high-level sessions.create() has this guarantee,
  // but it cannot select the dedicated agentPreset, so the low-level call is
  // required here.
  if (typeof scope.sessions.refresh === 'function') await scope.sessions.refresh();
  if (typeof scope.sessions.noteAgentPreset === 'function') {
    scope.sessions.noteAgentPreset(created.sessionId, agentPreset);
  }
  const binding = await waitForBinding(scope.sessions, created.sessionId);
  await binding.session.rename(title);
  await beforeOpen?.(created.sessionId, false);
  await openPtcSessionView(scope, created.sessionId);
  rememberSessionId(key, created.sessionId);
  return { sessionId: created.sessionId, reused: false };
}

const trainerLaunchStates = new WeakMap();
const trainerLaunchStatesByHost = new Map();

export function matchesTarget(binding, request) {
  return !!binding && ['projectId', 'mode', 'targetKind', 'targetId', 'presetId']
    .every(field => binding[field] === request[field]);
}

function legacySessionIds(request) {
  const found = [];
  try {
    const storage = window.localStorage;
    for (let i = 0; i < storage.length; i++) {
      const key = storage.key(i), prefix = `${SESSION_KEY_PREFIX}${request.targetKind}:`;
      if (!key?.startsWith(prefix)) continue;
      try {
        const parts = JSON.parse(key.slice(prefix.length));
        if ([request.projectId, request.mode, request.targetId, request.presetId].every((v, index) => parts[index] === v)) {
          found.push({ key, sessionId: storage.getItem(key) });
        }
      } catch { /* Ignore unrelated or malformed cache entries. */ }
    }
  } catch { /* Server authority works even when browser storage is unavailable. */ }
  return found;
}

const resolvedIdentity = binding => binding?.resolved || { source: binding?.mode === 'engineering' ? 'release' : 'candidate',
  revisionId: binding?.mode === 'engineering' ? null : binding?.candidateRevision ?? null, frozenVersionId: null, releaseId: null };
function contextChange(previous, binding) {
  return ['source', 'revisionId', 'frozenVersionId', 'releaseId'].some(k => (resolvedIdentity(previous)[k] ?? null) !== (resolvedIdentity(binding)[k] ?? null))
    || (previous?.selectedRunId || null) !== (binding?.selectedRunId || null);
}

/** Only return success after the server binding and native selection agree. */
export async function openTrainerNativeSession(scope, request, { post, title, hostId = null }) {
  if (!scope?.sessions) throw new Error('HOST_UNAVAILABLE: DSH 原生会话服务尚未注入');
  if (!request?.projectId || !['agent', 'workflow'].includes(request.targetKind) || !request.targetId) {
    throw new Error('TARGET_INVALID: Trainer 会话目标不完整');
  }
  if (request.presetId !== 'agent-trainer') throw new Error('PRESET_MISMATCH: 原生训练必须使用 agent-trainer preset');
  if (!['training', 'published', 'engineering'].includes(request.mode)) throw new Error('MODE_INVALID: 训练模式无效');
  const workspace = await post('session-workspace', request);
  if (request.mode === 'training' && request.candidateRevision !== workspace.candidateRevision) {
    throw new Error('STALE_SESSION: 候选 revision 已更新，请刷新工作台后重新打开');
  }
  const key = ptcSessionKey(request.targetKind, JSON.stringify([
    request.projectId, request.mode, request.targetId, request.presetId,
  ]));
  let state = hostId ? trainerLaunchStatesByHost.get(hostId) : trainerLaunchStates.get(scope.sessions);
  if (!state) {
    state = { pending: new Map(), sessions: new Map() };
    if (hostId) {
      trainerLaunchStatesByHost.set(hostId, state);
      if (trainerLaunchStatesByHost.size > 32) trainerLaunchStatesByHost.delete(trainerLaunchStatesByHost.keys().next().value);
    } else trainerLaunchStates.set(scope.sessions, state);
  }
  if (state.pending.has(key)) {
    const opened = await state.pending.get(key);
    await openPtcSessionView(scope, opened.sessionId);
    return { ...opened, reused: true };
  }
  const pending = (async () => {
    const identity = Object.fromEntries(['projectId', 'mode', 'targetKind', 'targetId', 'presetId'].map(k => [k, request[k]]));
    const legacy = legacySessionIds(request);
    const clearCache = () => {
      state.sessions.delete(key);
      try {
        window.localStorage.removeItem(`${SESSION_KEY_PREFIX}${key}`);
        for (const entry of legacy) window.localStorage.removeItem(entry.key);
      } catch { /* Disposable cache. */ }
    };
    if (request.freshSession) clearCache();
    let record = null, targetApiAvailable = false;
    try { record = await post('target-session', identity); targetApiAvailable = true; } catch (error) {
      // Older host bridges may not expose the new operation yet; legacy caches remain usable.
      if (['target_missing', 'release_not_active', 'forbidden', 'invalid_binding'].includes(error?.code)) throw error;
    }
    const remembered = record?.sessionId || (!request.freshSession && (state.sessions.get(key) || existingSessionId(key) || legacy.at(-1)?.sessionId));
    // A verified server target-session is authoritative. The browser session
    // runtime may not yet have loaded its binding or preset event after a
    // server-side factory creates it; do not discard the durable mapping for
    // that local cache miss. Refresh first, then bind and open the exact id.
    const serverAuthoritative = !!record?.sessionId;
    let rememberedLocalBinding = remembered ? scope.sessions.binding(remembered) : undefined;
    if (remembered && serverAuthoritative && rememberedLocalBinding === undefined
      && typeof scope.sessions.refresh === 'function') {
      await scope.sessions.refresh();
      rememberedLocalBinding = scope.sessions.binding(remembered);
    }
    const canTryReuse = remembered && (serverAuthoritative
      || (rememberedLocalBinding !== undefined && sessionPreset(rememberedLocalBinding) === request.presetId));
    if (canTryReuse) {
      try {
        let previousBinding = await post('bind-session', {
          projectId: request.projectId, mode: request.mode, sessionId: remembered,
        });
        if (matchesTarget(previousBinding, request)) {
          const before = previousBinding;
          let binding;
          for (let attempt = 0; attempt < 2; attempt++) {
            try {
              binding = await post('bind-session', { ...request, sessionId: remembered, baseBindingRevision: previousBinding.bindingRevision });
              break;
            } catch (error) {
              if (error.code !== 'binding_conflict' || attempt) throw error;
              previousBinding = await post('bind-session', { projectId: request.projectId, mode: request.mode, sessionId: remembered });
              if (!matchesTarget(previousBinding, request)) throw Object.assign(new Error('TARGET_MISMATCH: 服务端绑定与请求不一致'), { code: 'target_mismatch' });
            }
          }
          if (!matchesTarget(binding, request)) throw new Error('TARGET_MISMATCH: 服务端绑定与请求不一致');
          if (!binding.effectiveTools?.includes('trainer_context')) throw new Error('TRAINER_TOOLS_MISSING: 原生会话缺少 Trainer 工具');
          if (typeof scope.sessions.refresh === 'function' && scope.sessions.binding(remembered) === undefined) {
            await scope.sessions.refresh();
          }
          await waitForBinding(scope.sessions, remembered);
          await openPtcSessionView(scope, remembered);
          state.sessions.set(key, remembered);
          rememberSessionId(key, remembered);
          return { sessionId: remembered, binding, reused: true, scopeOpened: true,
            previousResolved: resolvedIdentity(before), resolved: resolvedIdentity(binding), previousSelectedRunId: before.selectedRunId || null,
            contextUpdated: contextChange(before, binding) ? 'binding-only' : false };
        }
      } catch (error) {
        if (!['session_unbound', 'session_identity_mismatch', 'target_mismatch'].includes(error.code)) throw error;
      }
    }
    if (remembered && targetApiAvailable && (serverAuthoritative || canTryReuse)) { await post('forget-target-session', identity); clearCache(); }

    // Browser DSH profiles may omit the public session.create and
    // agentPreset.list endpoints.  The Trainer service owns a server-side
    // factory in the same DSH context, so it can create and verify the real
    // agent session without relying on those optional browser routes.
    const created = await post('open-native-session', request);
    if (typeof created?.sessionId !== 'string' || !created.sessionId || !created.binding) {
      throw new Error('NATIVE_CREATE_FAILED: DSH 没有返回已绑定的原生会话');
    }
    const binding = created.binding;
    if (!matchesTarget(binding, request)) throw new Error('TARGET_MISMATCH: 服务端绑定与请求不一致');
    if (!binding.effectiveTools?.includes('trainer_context')) throw new Error('TRAINER_TOOLS_MISSING: 原生会话缺少 Trainer 工具');
    // The server-side factory creates the real DSH agent in the host process,
    // but that does not automatically push the new session into the browser
    // SessionRuntime. Refresh before waiting so the native opener can resolve
    // and select the exact session instead of leaving the host on blank 新会话.
    if (typeof scope.sessions.refresh === 'function') await scope.sessions.refresh();
    if (typeof scope.sessions.noteAgentPreset === 'function') {
      scope.sessions.noteAgentPreset(created.sessionId, request.presetId);
    }
    await waitForBinding(scope.sessions, created.sessionId);
    await openPtcSessionView(scope, created.sessionId);
    state.sessions.set(key, created.sessionId);
    rememberSessionId(key, created.sessionId);
    return { ...created, sessionId: created.sessionId, binding, reused: created.reused === true, scopeOpened: true,
      previousResolved: created.previousResolved || null, resolved: resolvedIdentity(binding),
      previousSelectedRunId: created.previousSelectedRunId || null, contextUpdated: created.contextUpdated || false };
  })();
  state.pending.set(key, pending);
  try { return await pending; }
  finally { if (state.pending.get(key) === pending) state.pending.delete(key); }
}

export function ptcSessionKey(mode, identity = '') {
  if (!['agent', 'workflow', 'publish', 'engineering'].includes(mode)) throw new Error('unsupported PTC session mode');
  return `${mode}:${identity}`;
}
