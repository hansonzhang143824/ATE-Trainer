export function trainerNativeKey(target, presetId, mode) {
  return `trainer-native-v2:${JSON.stringify([target.projectId, presetId, mode, target.targetKind, target.targetId, 1])}`;
}

export function trainerPreset(targetKind, mode, trainer = false) {
  return mode === 'engineering' || mode === 'published' ? 'framework-observer'
    : trainer || targetKind === 'workflow' ? 'agent-trainer' : 'framework-expert';
}

function trainerSessionListError(snapshot) {
  const error = snapshot?.listError;
  if (error === null || error === undefined) {
    return snapshot?.listState === 'error' ? new Error('DSH 会话列表同步失败：宿主未提供错误详情') : null;
  }
  if (error instanceof Error) return error;
  const wrapped = new Error(`DSH 会话列表同步失败：${error.message ?? String(error)}`);
  if (error.code !== undefined) wrapped.code = error.code;
  if (error.details !== undefined) wrapped.details = error.details;
  return wrapped;
}

function trainerSessionListTimeout(snapshot, timeoutMs) {
  const phase = snapshot?.phase ?? 'unknown';
  const listState = snapshot?.listState ?? 'unknown';
  const error = snapshot?.listError;
  const detail = error?.message ?? (error === undefined || error === null ? '' : String(error));
  return new Error(`DSH 会话列表同步超时（${timeoutMs}ms，phase=${phase}, listState=${listState}${detail ? `, listError=${detail}` : ''}），请重试恢复`);
}

function isUnknownNativeSession(error) {
  const code = String(error?.code ?? '').toLowerCase();
  const message = String(error?.message ?? error ?? '').toLowerCase();
  return ['session_unknown', 'session_not_found', 'unknown_session', 'not_found'].includes(code)
    || /unknown session|session .*not found|session .*does not exist/.test(message);
}

function nativeSessionKnown(snapshot, sessionId) {
  if (!snapshot || !sessionId) return false;
  if (snapshot.byId && Object.prototype.hasOwnProperty.call(snapshot.byId, sessionId)) return true;
  if (Array.isArray(snapshot.sessions) && snapshot.sessions.some(item => (item?.sessionId ?? item?.id) === sessionId)) return true;
  if (Array.isArray(snapshot.items) && snapshot.items.some(item => (item?.sessionId ?? item?.id) === sessionId)) return true;
  return false;
}

/**
 * Ask the host to refresh its public session index before waiting on it. The
 * refresh method is optional because older DSH hosts only expose the
 * subscribe/getSnapshot list surface. A failed refresh is surfaced so the
 * caller can retry; no ready snapshot is manufactured here.
 */
async function refreshTrainerSessionList(sessions, signal) {
  const refresh = sessions?.refresh;
  if (typeof refresh !== 'function') return;
  if (signal?.aborted) throw new DOMException('会话选择已更新', 'AbortError');
  await refresh.call(sessions);
  if (signal?.aborted) throw new DOMException('会话选择已更新', 'AbortError');
}

// The public session list is a sidebar projection, not the authority used to
// create or bind a trainer session. A cold DSH host can leave this refresh in
// `pending` while the dedicated session APIs are already usable. Give a
// refresh a small budget so a fast refresh can repair the list, but do not
// serialize first-session creation behind an indefinitely pending index.
async function refreshTrainerSessionListWithBudget(sessions, signal, timeoutMs = 1000) {
  if (typeof sessions?.refresh !== 'function') return;
  const refresh = refreshTrainerSessionList(sessions, signal);
  let timer;
  const timeout = new Promise(resolve => {
    timer = setTimeout(() => resolve('timeout'), timeoutMs);
  });
  const result = await Promise.race([
    refresh.then(() => 'ready'),
    timeout
  ]);
  clearTimeout(timer);
  if (result === 'timeout') refresh.catch(() => {});
}

/**
 * Creating a session and publishing it into the host's sidebar index are
 * separate operations.  The server binding is authoritative, but the host
 * selector rejects an id until the public index knows it.  Retry only this
 * presentation step; never create a second session or drop the binding.
 */
async function openTrainerSession(services, sessionId, signal) {
  try {
    services.sessions.open(sessionId);
    return;
  } catch (error) {
    if (!isUnknownNativeSession(error)) throw error;
  }
  await refreshTrainerSessionList(services.sessions, signal).catch(() => {});
  // The host can accept the create RPC before its public list snapshot is
  // ready. Retry the actual open operation itself; waiting only on the list
  // can deadlock when that presentation index remains `pending`.
  const deadline = Date.now() + 15000;
  let lastError;
  while (Date.now() < deadline) {
    if (signal?.aborted) throw new DOMException('会话选择已更新', 'AbortError');
    try {
      services.sessions.open(sessionId);
      return;
    } catch (error) {
      lastError = error;
      if (!isUnknownNativeSession(error)) throw error;
    }
    await new Promise((resolve, reject) => {
      const abort = () => { clearTimeout(timer); reject(new DOMException('会话选择已更新', 'AbortError')); };
      const done = () => { signal?.removeEventListener('abort', abort); resolve(); };
      const timer = setTimeout(done, 250);
      signal?.addEventListener('abort', abort, { once: true });
    });
  }
  throw lastError ?? new Error(`DSH 会话 ${sessionId} 在 15 秒内不可打开`);
}

export function waitTrainerSession(sessions, predicate, { signal, timeoutMs = 10000 } = {}) {
  if (signal?.aborted) return Promise.reject(new DOMException('会话选择已更新', 'AbortError'));
  const initial = sessions.list.getSnapshot();
  const initialError = trainerSessionListError(initial);
  if (initialError) return Promise.reject(initialError);
  if (predicate(initial)) return Promise.resolve();
  return new Promise((resolve, reject) => {
    let unsubscribe = () => {};
    const cleanup = () => { clearTimeout(timer); unsubscribe(); signal?.removeEventListener('abort', abort); };
    const abort = () => { cleanup(); reject(new DOMException('会话选择已更新', 'AbortError')); };
    const timer = setTimeout(() => {
      const snapshot = sessions.list.getSnapshot();
      cleanup();
      reject(trainerSessionListTimeout(snapshot, timeoutMs));
    }, timeoutMs);
    const check = () => {
      const snapshot = sessions.list.getSnapshot();
      const error = trainerSessionListError(snapshot);
      if (error) { cleanup(); reject(error); return true; }
      if (predicate(snapshot)) { cleanup(); resolve(); return true; }
      return false;
    };
    unsubscribe = sessions.list.subscribe(check);
    signal?.addEventListener('abort', abort, { once: true });
    check();
  });
}

// Storage is only a session-id hint. Every reuse must pass server verification.
export function createTrainerNavigator({ services, api, storage = globalThis.localStorage }) {
  let epoch = 0;
  let pending = null;
  const creating = new Map();
  const read = key => { try { return storage?.getItem(key); } catch { return null; } };
  const write = (key, id) => { try { storage?.setItem(key, id); } catch { /* server binding remains authoritative */ } };
  return {
    cancel() { epoch += 1; pending?.abort(); },
    async open({ target, mode = 'training', trainer = false, selectedRunId = null, title, _recovering = false }) {
      pending?.abort();
      const localEpoch = ++epoch;
      const signal = (pending = new AbortController()).signal;
      const current = () => {
        if (signal.aborted || localEpoch !== epoch) throw new DOMException('会话选择已更新', 'AbortError');
      };
      const connection = typeof services.get === 'function' ? services.get('connection') : services.connection;
      const rpc = connection?.api;
      let remoteSession;
      if (typeof services.get === 'function') {
        try { remoteSession = services.get('remote.session'); } catch { /* optional on older hosts */ }
      }
      if ((!rpc?.sessions?.create && !remoteSession?.create) || !services.sessions || !services.workspaces) throw new Error('DSH 原生会话服务尚未就绪');
      const presetId = trainerPreset(target.targetKind, mode, trainer);
      const key = trainerNativeKey(target, presetId, mode);
      const identity = { ...target, presetId, mode, selectedRunId };
      let sessionId = read(key);
      let sessionList = services.sessions.list.getSnapshot();
      let binding;
      // The public sidebar index is only a presentation surface. It can stay
      // pending or error while the dedicated session and trainer APIs remain
      // usable, so verify a remembered id directly through the server binding.
      // Refresh opportunistically, but never make navigation wait for it.
      if (sessionList.phase !== 'ready' && !sessionId && typeof services.sessions.refresh === 'function') {
        // A fast refresh still repairs the sidebar before creation. If the
        // host keeps the public index pending, continue with the authoritative
        // server binding and native create RPC instead of adding that delay to
        // the first open. openTrainerSession() separately retries publication
        // of the resulting session ID.
        await refreshTrainerSessionListWithBudget(services.sessions, signal);
      } else if (sessionList.phase !== 'ready') {
        void refreshTrainerSessionList(services.sessions, signal).catch(() => {});
      }
      if (!sessionId) {
        const sessionListError = trainerSessionListError(sessionList);
        if (sessionListError) throw sessionListError;
      }
      if (sessionId) {
        let existing;
        try { existing = await api('bind-session', { projectId: target.projectId, sessionId }, { signal }); }
        catch (error) { if (error.code !== 'session_unbound') throw error; }
        if (existing) {
          current();
          binding = await api('bind-session', { ...identity, sessionId, baseBindingRevision: existing.bindingRevision }, { signal });
          current();
        } else {
          // A session created by an earlier attempt can be valid but have no
          // trainer binding because the UI was waiting on the host index.
          try {
            binding = await api('bind-session', { ...identity, sessionId }, { signal });
            current();
          } catch (error) {
            if (!['session_unbound', 'session_identity_mismatch'].includes(error.code)) throw error;
            sessionId = null;
          }
        }
      }
      if (!binding) {
        const prepared = await api('bind-session', identity, { signal });
        current();
        if (!prepared.cwd) throw new Error('服务端未返回合成训练工作区');
        let creation = creating.get(key);
        if (!creation) {
          creation = (async () => {
            const workspace = await services.workspaces.create({ path: prepared.cwd });
            if (!workspace?.workspaceId) throw new Error('DSH 没有为会话工作区返回 workspaceId');
            if (remoteSession?.create) {
              const response = await remoteSession.create({ workspaceId: workspace.workspaceId, agentPreset: presetId });
              if (!response?.ok) throw new Error(response?.error?.message ?? '创建专用会话失败');
              return response.value?.sessionId;
            }
            const response = await rpc.sessions.create({ workspaceId: workspace.workspaceId, agentPreset: presetId });
            if (!response?.result?.ok) throw new Error(response?.result?.error?.message ?? '创建专用会话失败');
            return response.result.value?.sessionId;
          })();
          creating.set(key, creation);
          creation.catch(() => { if (creating.get(key) === creation) creating.delete(key); });
        }
        sessionId = await creation;
        if (!sessionId) throw new Error('DSH 未返回 sessionId');
        // Remember accepted creation even when navigation was superseded: retry restores, never duplicates.
        // The host may publish the new session to its sidebar index later (or keep
        // that index pending while no conversation is selected). Binding is a
        // server-side operation and must not wait for that presentation index.
        write(key, sessionId);
        current();
        creating.delete(key);
        binding = await api('bind-session', { ...identity, sessionId }, { signal });
        current();
        if (title) {
          const createdBinding = services.sessions.binding?.(sessionId);
          if (createdBinding?.session?.rename) await createdBinding.session.rename(title);
        }
      }
      current();
      if (binding.sessionId !== sessionId || binding.presetId !== presetId || binding.projectId !== target.projectId || binding.targetKind !== target.targetKind || binding.targetId !== target.targetId || binding.mode !== mode || binding.bindingSchemaVersion !== 1) {
        throw new Error('服务端会话绑定与当前目标不一致');
      }
      const selection = binding.nativeModelSelection;
      if (!selection?.provider || !selection?.model) throw new Error('服务端未提供专用会话模型配置');
      if (!rpc.sessions.selectModel || !rpc.sessions.models) throw new Error('DSH 会话模型选择 API 尚未就绪');
      const chosen = await rpc.sessions.selectModel({ sessionId, provider: selection.provider, model: selection.model,
        ...(selection.reasoningEffort === undefined ? {} : { reasoningEffort: selection.reasoningEffort }) }, signal);
      current();
      if (!chosen?.result?.ok) throw new Error(chosen?.result?.error?.message ?? '专用会话模型选择失败');
      const matches = model => model?.provider === selection.provider && model?.model === selection.model
        && (selection.reasoningEffort === undefined || model.reasoningEffort === selection.reasoningEffort);
      if (!matches(chosen.result.value?.selected)) throw new Error('DSH 返回的会话模型与服务端配置不一致');
      const confirmed = await rpc.sessions.models({ sessionId }, signal);
      current();
      if (!confirmed?.result?.ok) throw new Error(confirmed?.result?.error?.message ?? '无法复核专用会话模型');
      if (confirmed.result.value?.routable !== true || !matches(confirmed.result.value?.current)) throw new Error('专用会话模型未生效或提供方不可用');
      try {
        await openTrainerSession(services, sessionId, signal);
      } catch (error) {
        // localStorage is only a hint. A browser reload or host restart can
        // leave an id that no longer exists in the native session service.
        // Drop that hint and retry exactly once so the user can recover by
        // clicking the same button instead of seeing an opaque host error.
        if (!_recovering && isUnknownNativeSession(error) && read(key) === sessionId) {
          try { storage?.removeItem(key); } catch { /* binding remains server authoritative */ }
          return this.open({ target, mode, trainer, selectedRunId, title, _recovering: true });
        }
        throw error;
      }
      return binding;
    }
  };
}
