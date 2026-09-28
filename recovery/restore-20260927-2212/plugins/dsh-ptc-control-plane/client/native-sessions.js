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
export async function openPtcNativeSession(scope, workspace, { key, title }) {
  const api = typeof scope?.get === 'function' ? scope.get('connection')?.api : scope?.connection?.api;
  if (!api?.agentPresets?.list || !api?.sessions?.create || !scope?.sessions || !scope?.workspaces) {
    throw new Error('DSH 原生会话服务尚未注入；请确认本机 DSH 已加载会话与工作区服务。');
  }
  const remembered = existingSessionId(key);
  if (remembered && scope.sessions.binding(remembered) !== undefined) {
    scope.sessions.open(remembered);
    return { sessionId: remembered, reused: true };
  }

  const target = await scope.workspaces.create({ path: workspace.path });
  if (!target || typeof target.workspaceId !== 'string' || !target.workspaceId) {
    throw new Error('DSH 没有为会话工作区返回 workspaceId');
  }
  const roster = requireOk((await api.agentPresets.list({})).result, '读取 DSH Agent 预设');
  const presets = Array.isArray(roster?.presets) ? roster.presets : [];
  const preset = presets.find(item => !item.broken && item.id === 'standard')
    ?? presets.find(item => !item.broken && item.id === 'code')
    ?? presets.find(item => !item.broken && item.isDefault);
  if (!preset) throw new Error('DSH 没有可用的 standard/code Agent 预设');
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
