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
      reject(new Error('DSH 创建了会话，但 10 秒内没有出现在会话列表中。'));
    }, 10_000);
    const unsubscribe = sessions.list.subscribe(() => {
      const binding = sessions.binding(sessionId);
      if (binding === undefined) return;
      window.clearTimeout(timeout);
      unsubscribe();
      resolve(binding);
    });
  });
}

/** Create or reopen a genuine DSH conversation rooted in its server-approved workspace. */
export async function openPtcNativeSession(scope, workspace, { key, title, agentPreset = 'standard' }) {
  const api = typeof scope?.get === 'function' ? scope.get('connection')?.api : scope?.connection?.api;
  if (!api?.agentPresets?.list || !api?.sessions?.create || !scope?.sessions || !scope?.workspaces) {
    throw new Error('DSH 原生会话服务尚未注入；请确认本机 DSH 已加载会话与工作区服务。');
  }
  const remembered = existingSessionId(key);
  if (remembered) {
    const rememberedBinding = scope.sessions.binding(remembered);
    if (rememberedBinding !== undefined && sessionPreset(rememberedBinding) === agentPreset) {
      scope.sessions.open(remembered);
      return { sessionId: remembered, reused: true };
    }
    try { window.localStorage.removeItem(`${SESSION_KEY_PREFIX}${key}`); } catch { /* stale mapping is disposable */ }
  }

  const target = await scope.workspaces.create({ path: workspace.path });
  if (!target || typeof target.workspaceId !== 'string' || !target.workspaceId) {
    throw new Error('DSH 没有为会话工作区返回 workspaceId');
  }
  const roster = requireOk((await api.agentPresets.list({})).result, '读取 DSH Agent 预设');
  const presets = Array.isArray(roster?.presets) ? roster.presets : [];
  const preset = presets.find(item => !item.broken && item.id === agentPreset)
    ?? (agentPreset === 'standard' ? presets.find(item => !item.broken && item.id === 'code') : null)
    ?? (agentPreset === 'standard' ? presets.find(item => !item.broken && item.isDefault) : null);
  if (!preset) throw new Error(`DSH 没有可用的 ${agentPreset} Agent 预设；不会回退到普通会话。`);
  const created = requireOk((await api.sessions.create({ workspaceId: target.workspaceId, agentPreset: preset.id })).result, '创建 DSH 会话');
  if (typeof created?.sessionId !== 'string' || !created.sessionId) throw new Error('DSH 没有返回 sessionId');
  const binding = await waitForBinding(scope.sessions, created.sessionId);
  await binding.session.rename(title);
  rememberSessionId(key, created.sessionId);
  scope.sessions.open(created.sessionId);
  return { sessionId: created.sessionId, reused: false };
}

export function ptcSessionKey(mode, identity = '') {
  if (!['agent', 'workflow', 'publish', 'engineering'].includes(mode)) throw new Error('unsupported PTC session mode');
  return `${mode}:${identity}`;
}
