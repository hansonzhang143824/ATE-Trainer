// Trainer API v1. Independent of the legacy SMOKE_ONLY store.
export const TRAINER_UNBOUND_NOTICE = '当前原生会话未绑定框架目标，请选择左侧 Agent 或工作流。';

export function trainerRequestId() {
  return globalThis.crypto.randomUUID();
}

export function createTrainerApi({ fetchImpl = globalThis.fetch, baseUrl = '/api/ptc-control/trainer' } = {}) {
  return async (operation, args = {}, { signal } = {}) => {
    const response = await fetchImpl(`${baseUrl}/${operation}`, {
      method: 'POST', credentials: 'same-origin', signal,
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify(args)
    });
    const body = await response.json();
    if (!response.ok || body?.ok !== true) {
      const error = new Error(body?.error?.message ?? `Trainer HTTP ${response.status}`);
      error.code = body?.error?.code ?? 'TRANSPORT_ERROR';
      error.details = body?.error?.details;
      throw error;
    }
    return body.value;
  };
}

export function trainerTargetKey(target) {
  return JSON.stringify([target.projectId, target.targetKind, target.targetId]);
}

export function trainerControlState(run, action) {
  const control = run?.controls?.[action];
  return { allowed: control?.allowed === true, reason: control?.reason || (run ? '服务端未允许此操作' : '尚未选择运行') };
}

export function createTrainerStore({ api = createTrainerApi(), projectId = 'synthetic-lab', pollMs = 5000 } = {}) {
  const listeners = new Set();
  let state = { enabled: false, surfaceVisible: false, projectId, mode: 'training', target: null, project: null, binding: null,
    selectedRunId: null, run: null, runs: [], nextRunsCursor: null, events: [], eventsCursor: 0, assets: null, releases: [], frozenVersions: [],
    loading: false, busy: false, error: null, readError: null, notice: '', detailsVisible: true };
  let generation = 0;
  let controller = null;
  let timer = null;
  let disposed = false;
  let reading = false;
  const uncertainRequests = new Map();
  const update = patch => {
    if (disposed) return;
    state = { ...state, ...patch };
    listeners.forEach(listener => listener());
  };
  function invalidate() {
    generation += 1;
    controller?.abort();
    controller = null;
    reading = false;
  }
  async function refresh() {
    if (disposed || !state.enabled || reading) return;
    const epoch = generation;
    const selected = state;
    const pending = new AbortController();
    controller = pending;
    reading = true;
    update({ loading: true });
    try {
      const identity = { projectId, ...selected.target, mode: selected.mode };
      // The project context intentionally returns only workflow summaries. Load the
      // selected workflow definition separately so the workbench can display its
      // real step count and labels instead of falling back to a fabricated count.
      // Asset loading is supplemental: a missing/invalid asset must not hide an
      // otherwise valid project context or run history.
      const workflowAssetPath = selected.target?.targetKind === 'workflow'
        ? `workflows/${selected.target.targetId}.json` : null;
      const workflowTestPath = selected.target?.targetKind === 'workflow'
        ? `tests/${selected.target.targetId}.json` : null;
      const targetAssetsPromise = workflowAssetPath
        ? api('assets', { projectId, paths: [workflowAssetPath] }, { signal: pending.signal })
          .then(value => ({ value }), error => ({ error }))
        : Promise.resolve({ value: null });
      // Test inputs are optional metadata. Read them separately so a workflow
      // without a test fixture still loads and remains runnable with explicit
      // user input instead of failing the whole candidate asset read.
      const workflowTestsPromise = workflowTestPath
        ? api('assets', { projectId, paths: [workflowTestPath] }, { signal: pending.signal })
          .then(value => ({ value }), error => ({ error }))
        : Promise.resolve({ value: null });
      const [context, history, detail, eventPage, liveBinding, targetAssetsResult, workflowTestsResult] = await Promise.all([
        api('context', identity, { signal: pending.signal }),
        api('runs', { projectId }, { signal: pending.signal }),
        selected.selectedRunId ? api('runs', { projectId, runId: selected.selectedRunId }, { signal: pending.signal }) : null,
        selected.selectedRunId ? api('events', { projectId, runId: selected.selectedRunId, cursor: selected.eventsCursor }, { signal: pending.signal }) : null,
        selected.binding ? api('bind-session', { projectId, sessionId: selected.binding.sessionId }, { signal: pending.signal }) : null,
        targetAssetsPromise,
        workflowTestsPromise
      ]);
      if (epoch !== generation || disposed) return;
      if (liveBinding) {
        if (liveBinding.sessionId !== selected.binding.sessionId || liveBinding.presetId !== selected.binding.presetId || liveBinding.mode !== selected.mode || trainerTargetKey(liveBinding) !== trainerTargetKey(selected.target)) throw new Error('会话恢复身份不匹配');
        if (liveBinding.selectedRunId !== selected.selectedRunId) {
          select(selected.target, selected.mode, liveBinding.selectedRunId ?? null);
          update({ binding: liveBinding });
          return;
        }
      }
      const run = detail?.run ?? detail;
      if (run && (run.runId !== selected.selectedRunId || run.projectId !== projectId)) throw new Error('运行响应身份不匹配');
      if (eventPage?.runId && eventPage.runId !== selected.selectedRunId) throw new Error('事件响应身份不匹配');
      const runs = [...new Map([...(history.runs ?? []), ...state.runs].map(item => [item.runId, item])).values()];
      // New page values take precedence; preserve already loaded older history.
      for (const item of history.runs ?? []) { const index = runs.findIndex(run => run.runId === item.runId); runs[index] = item; }
      const events = [...new Map([...selected.events, ...(eventPage?.events ?? [])].map(item => [item.seq, item])).values()].slice(-1000);
      const workflowAssets = targetAssetsResult?.value ?? null;
      const workflowTests = workflowTestsResult?.value ?? null;
      const targetAssets = workflowAssets || workflowTests
        ? { ...(workflowAssets ?? {}), files: { ...(workflowAssets?.files ?? {}), ...(workflowTests?.files ?? {}) } }
        : null;
      let project = context.project ?? context;
      if (workflowAssetPath && targetAssets?.files?.[workflowAssetPath]) {
        try {
          const definition = JSON.parse(targetAssets.files[workflowAssetPath]);
          if (Array.isArray(definition.steps)) {
            project = { ...project, workflows: (project.workflows ?? []).map(item =>
              item.workflowId === selected.target.targetId ? { ...item, ...definition, steps: definition.steps } : item) };
          }
        } catch { /* the editor will expose malformed candidate content */ }
      }
      const assetReadError = targetAssetsResult?.error?.message;
      update({ project, ...(workflowAssetPath ? { assets: targetAssets } : {}), frozenVersions: (context.frozenVersions ?? []).map(version => ({ projectId, ...version })), ...(liveBinding ? { binding: liveBinding } : {}), runs, nextRunsCursor: history.nextCursor == null ? null : runs.length, run,
        events, eventsCursor: eventPage?.cursor ?? selected.eventsCursor, loading: false, readError: assetReadError ?? null });
    } catch (error) {
      if (epoch === generation && !disposed && error.name !== 'AbortError') update({ loading: false, readError: error.message });
    } finally {
      if (epoch === generation) { reading = false; controller = null; }
    }
  }
  function select(target, mode = state.mode, selectedRunId = null) {
    invalidate();
    update({ target, mode, selectedRunId, binding: null, run: null, events: [], eventsCursor: 0, assets: null, error: null, readError: null,
      ...(target && state.target && trainerTargetKey(target) === trainerTargetKey(state.target) ? {} : { frozenVersion: null }) });
    void refresh();
  }
  async function perform(operation, args = {}, { mutation = true } = {}) {
    if (state.busy) throw new Error('上一操作尚未完成');
    const epoch = generation;
    const input = { projectId, ...state.target, mode: state.mode, ...args };
    const retryKey = JSON.stringify([operation, input]);
    const requestId = mutation ? args.requestId ?? uncertainRequests.get(retryKey) ?? trainerRequestId() : null;
    if (mutation) uncertainRequests.set(retryKey, requestId);
    update({ busy: true, error: null, notice: '' });
    try {
      const result = await api(operation, { ...input, ...(mutation ? { requestId } : {}) });
      uncertainRequests.delete(retryKey);
      if (epoch === generation) {
        if (operation === 'assets') update({ assets: result });
        if (operation === 'releases') update({ releases: result.releases ?? result });
        if (operation === 'freeze') update({ frozenVersion: result,
          frozenVersions: [...state.frozenVersions.filter(item => item.frozenVersionId !== result.frozenVersionId), { ...input, ...result }] });
        update({ notice: operation === 'run' ? `已受理运行 ${result.runId}，以运行终态为准` : '操作已完成' });
      }
      return result;
    } catch (error) {
      if (epoch === generation) update({ error: `${error.code ? `${error.code}：` : ''}${error.message}` });
      throw error;
    } finally {
      update({ busy: false });
      if (epoch === generation) void refresh();
    }
  }
  return {
    api, getSnapshot: () => state,
    subscribe(listener) { listeners.add(listener); return () => listeners.delete(listener); },
    refresh, select, perform, update,
    async loadMoreRuns() {
      if (state.nextRunsCursor == null || state.busy) return;
      const epoch = generation;
      const page = await perform('runs', { cursor: state.nextRunsCursor }, { mutation: false });
      if (epoch === generation) update({ runs: [...new Map([...state.runs, ...(page.runs ?? [])].map(item => [item.runId, item])).values()], nextRunsCursor: page.nextCursor });
    },
    enable(enabled = true) {
      invalidate(); update({ enabled, surfaceVisible: enabled, loading: false });
      if (timer !== null) clearInterval(timer);
      timer = enabled ? setInterval(() => { void refresh(); }, pollMs) : null;
      if (enabled) void refresh();
    },
    setBinding(binding) {
      if (binding?.projectId !== projectId || !state.target || trainerTargetKey(binding) !== trainerTargetKey(state.target) || binding.mode !== state.mode) return false;
      update({ binding, ...(state.notice === TRAINER_UNBOUND_NOTICE ? { notice: '' } : {}) }); return true;
    },
    dispose() { invalidate(); if (timer !== null) clearInterval(timer); disposed = true; listeners.clear(); uncertainRequests.clear(); }
  };
}
