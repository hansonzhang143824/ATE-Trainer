window.__ModuleLoader__.load({
	id: "dsh-ptc-control-plane",
	factory: (require) => {
		var module = { exports: {} };
		var exports = module.exports;
		Object.defineProperty(exports, Symbol.toStringTag, { value: "Module" });
		const { createElement, useEffect, useState, useSyncExternalStore } = require("react");
		/**
		 * PTC control-plane client: shared read-only state store.
		 *
		 * Same-origin endpoint (registered by the plugin's lib/index.js):
		 *   GET /api/ptc-control/state
		 *
		 * Server contract (lib/control-state.js buildControlState, schemaVersion 1):
		 * {
		 *   "schemaVersion": 1,
		 *   "identity": "unbound",
		 *   "activeRelease": { "releaseId": string|null, "manifestDigest": string|null, "activatedAt": string|null } | null,
		 *   "trainingRuns": [ { "runId": string, "mode": string, "status": string, "target": Target|null, "updatedAt": string } ],
		 *   "delivery": { "batchId": string, "state": string|null, "releaseId": string|null, "executionScope": string|null, "updatedAt": string } | null,
		 *   "profiles": [ { "profileId": string, "publishedVersion": string|null, "manifestDigest": string|null, "draftVerdict": string|null } ],
		 *   "migration": { "legacyConsoleAbandoned": boolean, "legacyMode": string|null, "legacyModeAuthoritative": boolean }
		 * }
		 *
		 * Target (from the run's state.json) is an object or null:
		 *   { "kind": "profile", "profileId": string }
		 *   { "kind": "pipeline", "fromStage": string, "toStage": string, "stages": string[] }
		 * The client preserves the object and renders it as the profileId or the
		 * stage range (see formatTarget).
		 *
		 * The store follows the React useSyncExternalStore contract so the panel can
		 * subscribe without extra state plumbing. It never mutates host state.
		 */
		
		const STATE_URL = "/api/ptc-control/state";
		const CREATE_TRAINING_URL = "/api/ptc-control/training-runs";
		const EXECUTE_TRAINING_URL = "/api/ptc-control/training-runs/execute";
		const STOP_TRAINING_URL = "/api/ptc-control/training-runs/stop";
		const EXECUTE_PIPELINE_URL = "/api/ptc-control/training-pipelines/execute";
		const CONTROL_PIPELINE_URL = "/api/ptc-control/training-pipelines/control";
		const DEFAULT_POLL_MS = 5000;
		const SUPPORTED_SCHEMA_VERSION = 1;
		
		async function createTrainingRunRequest(target, options = {}) {
		  const url = options.url ?? CREATE_TRAINING_URL;
		  const fetchImpl = options.fetchImpl ?? fetch;
		  const response = await fetchImpl(url, {
		    method: "POST",
		    headers: { Accept: "application/json", "Content-Type": "application/json" },
		    credentials: "same-origin",
		    body: JSON.stringify({ target })
		  });
		  const body = await response.json().catch(() => ({}));
		  if (!response.ok) {
		    throw new Error(body.detail ?? body.error ?? `POST ${url} failed with HTTP ${response.status}`);
		  }
		  return body;
		}
		
		async function executeTrainingRunRequest(runId, testItems, options = {}) {
		  const url = options.url ?? EXECUTE_TRAINING_URL;
		  const fetchImpl = options.fetchImpl ?? fetch;
		  const response = await fetchImpl(url, {
		    method: "POST",
		    headers: { Accept: "application/json", "Content-Type": "application/json" },
		    credentials: "same-origin",
		    body: JSON.stringify({ runId, testItems })
		  });
		  const body = await response.json().catch(() => ({}));
		  if (!response.ok) {
		    throw new Error(body.detail ?? body.error ?? `POST ${url} failed with HTTP ${response.status}`);
		  }
		  return body;
		}
		
		async function stopTrainingRunRequest(runId, options = {}) {
		  const response = await (options.fetchImpl ?? fetch)(options.url ?? STOP_TRAINING_URL, {
		    method: "POST", headers: { Accept: "application/json", "Content-Type": "application/json" },
		    credentials: "same-origin", body: JSON.stringify({ runId })
		  });
		  const body = await response.json().catch(() => ({}));
		  if (!response.ok) throw new Error(body.detail ?? body.error ?? `HTTP ${response.status}`);
		  return body;
		}
		
		function executeTrainingPipelineRequest(runId, testItems, options = {}) {
		  return executeTrainingRunRequest(runId, testItems, { ...options, url: options.url ?? EXECUTE_PIPELINE_URL });
		}
		
		async function controlTrainingPipelineRequest(runId, action, options = {}) {
		  if (!['pause', 'resume', 'stop'].includes(action)) throw new Error('不支持的流程控制操作');
		  const url = options.url ?? CONTROL_PIPELINE_URL;
		  const response = await (options.fetchImpl ?? fetch)(url, {
		    method: 'POST', headers: { Accept: 'application/json', 'Content-Type': 'application/json' },
		    credentials: 'same-origin', body: JSON.stringify({ runId, action }),
		  });
		  const body = await response.json().catch(() => ({}));
		  if (!response.ok) throw new Error(body.detail ?? body.error ?? `POST ${url} failed with HTTP ${response.status}`);
		  return body;
		}
		
		function parseTrainingTestItems(value) {
		  const items = typeof value === 'string' ? value.trim().toUpperCase().split(/[,，、\s]+/).filter(Boolean) : [];
		  if (!items.length || items.some(item => !/^TM[0-9]+$/.test(item))) throw new Error('请输入 TM 编号列表，例如 TM109,TM110；不支持范围或自由文本');
		  return [...new Set(items)];
		}
		
		function pipelineTrainingTarget(stages, fromStage, toStage) {
		  const start = stages.indexOf(fromStage);
		  const end = stages.indexOf(toStage);
		  if (start < 0 || end < start) throw new Error('请选择有效的流程起止阶段');
		  return { kind: 'pipeline', fromStage, toStage };
		}
		
		function pipelineControlActions(status) {
		  if (['preparing', 'running', 'dispatching'].includes(status)) return ['pause', 'stop'];
		  if (status === 'pausing') return ['stop'];
		  if (status === 'paused') return ['resume', 'stop'];
		  return [];
		}
		
		function normalizePipeline(raw) {
		  if (raw === null || typeof raw !== 'object' || Array.isArray(raw)) return null;
		  return {
		    runId: optionalText(raw.runId), status: text(raw.status, 'unknown'), reason: optionalText(raw.reason),
		    updatedAt: optionalText(raw.updatedAt), pauseRequested: raw.pauseRequested === true,
		    stages: (Array.isArray(raw.stages) ? raw.stages : []).filter(stage => stage && typeof stage === 'object').map(stage => ({
		      stage: text(stage.stage), status: text(stage.status, 'unknown'),
		      reason: optionalText(stage.reason),
		      gateResult: stage.gateResult && typeof stage.gateResult === 'object' ? stage.gateResult : null,
		    })),
		  };
		}
		
		/** Coerce an unknown value into a display-safe string. */
		function text(value, fallback = "—") {
		  return typeof value === "string" && value.trim() !== "" ? value : fallback;
		}
		
		/** Pass through a nullable string field without inventing data. */
		function optionalText(value) {
		  return typeof value === "string" && value.trim() !== "" ? value : null;
		}
		
		/** Normalize one training-run record with defaults (runId/mode/status/target/updatedAt). */
		function normalizeRun(raw) {
		  const record = raw !== null && typeof raw === "object" ? raw : {};
		  return {
		    runId: text(record.runId, "unnamed-run"),
		    mode: text(record.mode, "training"),
		    status: text(record.status, "unknown"),
		    target: normalizeTarget(record.target),
		    testItems: Array.isArray(record.testItems) ? record.testItems.filter((item) => typeof item === "string") : [],
		    outcome: record.outcome !== null && typeof record.outcome === "object" ? record.outcome : null,
		    error: optionalText(record.error),
		    artifactRoot: optionalText(record.artifactRoot),
		    lifecycle: record.lifecycle !== null && typeof record.lifecycle === "object" ? record.lifecycle : null,
		    pipeline: normalizePipeline(record.pipeline),
		    updatedAt: text(record.updatedAt, "—")
		  };
		}
		
		/**
		 * Normalize a training-run target: a profile or pipeline object, or null.
		 * Keeps the object shape so views can render profileId or stage ranges.
		 */
		function normalizeTarget(raw) {
		  if (raw === null || raw === undefined) return null;
		  if (typeof raw === "string") {
		    return raw.trim() !== "" ? raw : null;
		  }
		  if (typeof raw !== "object") return null;
		  if (raw.kind === "profile") {
		    return { kind: "profile", profileId: optionalText(raw.profileId) };
		  }
		  if (raw.kind === "pipeline") {
		    const stages = Array.isArray(raw.stages)
		      ? raw.stages.filter((stage) => typeof stage === "string" && stage.trim() !== "")
		      : [];
		    return {
		      kind: "pipeline",
		      fromStage: optionalText(raw.fromStage),
		      toStage: optionalText(raw.toStage),
		      stages
		    };
		  }
		  return { kind: "unknown" };
		}
		
		/**
		 * Human-readable label for a normalized target: profileId for a profile
		 * target, a stage range (or stage list) for a pipeline target; null when
		 * there is nothing to show.
		 */
		function formatTarget(target) {
		  if (target === null || target === undefined) return null;
		  if (typeof target === "string") return target;
		  if (target.kind === "profile") return target.profileId;
		  if (target.kind === "pipeline") {
		    if (target.stages.length > 0) return target.stages.join("→");
		    if (target.fromStage !== null && target.toStage !== null) {
		      return `${target.fromStage}→${target.toStage}`;
		    }
		    return target.fromStage ?? target.toStage ?? null;
		  }
		  return null;
		}
		
		/** Normalize one expert-profile record (profileId/publishedVersion/manifestDigest/draftVerdict). */
		function normalizeProfile(raw) {
		  const record = raw !== null && typeof raw === "object" ? raw : {};
		  return {
		    profileId: text(record.profileId, "unnamed-profile"),
		    publishedVersion: optionalText(record.publishedVersion),
		    manifestDigest: optionalText(record.manifestDigest),
		    draftVerdict: optionalText(record.draftVerdict)
		  };
		}
		
		/**
		 * Normalize the delivery record: a single object or null.
		 * Never fabricates a delivery when the server reports none.
		 */
		function normalizeDelivery(raw) {
		  if (raw === null || typeof raw !== "object") return null;
		  return {
		    batchId: text(raw.batchId, "unnamed-batch"),
		    state: optionalText(raw.state),
		    releaseId: optionalText(raw.releaseId),
		    executionScope: optionalText(raw.executionScope),
		    updatedAt: text(raw.updatedAt, "—")
		  };
		}
		
		/** Normalize the active release record: a single object or null. */
		function normalizeActiveRelease(raw) {
		  if (raw === null || typeof raw !== "object") return null;
		  return {
		    releaseId: optionalText(raw.releaseId),
		    manifestDigest: optionalText(raw.manifestDigest),
		    activatedAt: optionalText(raw.activatedAt)
		  };
		}
		
		/** Normalize the migration block; tolerate an absent block. */
		function normalizeMigration(raw) {
		  const record = raw !== null && typeof raw === "object" ? raw : {};
		  return {
		    legacyConsoleAbandoned: record.legacyConsoleAbandoned === true,
		    legacyMode: optionalText(record.legacyMode),
		    legacyModeAuthoritative: record.legacyModeAuthoritative === true
		  };
		}
		
		/** Normalize the whole /api/ptc-control/state payload; never throws. */
		function normalizeState(raw) {
		  const body = raw !== null && typeof raw === "object" ? raw : {};
		  const trainingRuns = Array.isArray(body.trainingRuns) ? body.trainingRuns : [];
		  const profiles = Array.isArray(body.profiles) ? body.profiles : [];
		  return {
		    schemaVersion:
		      typeof body.schemaVersion === "number" ? body.schemaVersion : null,
		    identity: text(body.identity, "unbound"),
		    activeRelease: normalizeActiveRelease(body.activeRelease),
		    trainingRuns: trainingRuns.map(normalizeRun),
		    delivery: normalizeDelivery(body.delivery),
		    profiles: profiles.map(normalizeProfile),
		    pipelineStages: Array.isArray(body.pipelineStages) ? body.pipelineStages.filter(stage => typeof stage === 'string' && stage !== 'COMPLETE') : [],
		    migration: normalizeMigration(body.migration)
		  };
		}
		
		/**
		 * Create the shared read-only state store.
		 *
		 * @param {object} [options]
		 * @param {string} [options.url]        State endpoint, same-origin.
		 * @param {number} [options.pollMs]     Poll cadence while started.
		 * @param {typeof fetch} [options.fetchImpl] Injectable fetch for tests.
		 * @returns {{ subscribe, getSnapshot, getRevision, getLastError, refresh, start, stop }}
		 */
		function createPtcStateStore(options = {}) {
		  const url = options.url ?? STATE_URL;
		  const pollMs = options.pollMs ?? DEFAULT_POLL_MS;
		  const fetchImpl = options.fetchImpl ?? fetch;
		  const listeners = new Set();
		  let snapshot = normalizeState(null);
		  let lastError = null;
		  let started = false;
		  let timer = null;
		  let inFlight = false;
		  let revision = 0;
		
		  function publish() {
		    revision += 1;
		    for (const listener of listeners) listener();
		  }
		
		  async function refresh() {
		    if (inFlight) return;
		    inFlight = true;
		    try {
		      const response = await fetchImpl(url, {
		        method: "GET",
		        headers: { Accept: "application/json" },
		        credentials: "same-origin"
		      });
		      if (!response.ok) {
		        throw new Error(`GET ${url} failed with HTTP ${response.status}`);
		      }
		      const body = await response.json();
		      const next = normalizeState(body);
		      lastError = null;
		      const changed = JSON.stringify(next) !== JSON.stringify(snapshot);
		      snapshot = next;
		      if (changed) publish();
		    } catch (error) {
		      lastError = error instanceof Error ? error.message : String(error);
		      publish();
		    } finally {
		      inFlight = false;
		    }
		  }
		
		  function subscribe(listener) {
		    listeners.add(listener);
		    return () => {
		      listeners.delete(listener);
		    };
		  }
		
		  function getSnapshot() {
		    return snapshot;
		  }
		
		  function getLastError() {
		    return lastError;
		  }
		
		  function getRevision() {
		    return revision;
		  }
		
		  function start() {
		    if (started) return;
		    started = true;
		    void refresh();
		    timer = setInterval(() => {
		      void refresh();
		    }, pollMs);
		  }
		
		  function stop() {
		    if (timer !== null) {
		      clearInterval(timer);
		      timer = null;
		    }
		    started = false;
		  }
		
		  return { subscribe, getSnapshot, getRevision, getLastError, refresh, start, stop };
		}
		
		const h = createElement;
		
		async function draftRequest(action, input) {
		  const response = await fetch(`/api/ptc-control/training-drafts/${action}`, {
		    method: 'POST', credentials: 'same-origin',
		    headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
		    body: JSON.stringify(input),
		  });
		  const body = await response.json().catch(() => ({}));
		  if (!response.ok) throw new Error(body.detail ?? body.error ?? `HTTP ${response.status}`);
		  return body;
		}
		
		/** Only mounted in the training view; immutable run snapshots never change. */
		function DraftEditor({ profileId }) {
		  const [file, setFile] = useState('instructions.md');
		  const [loaded, setLoaded] = useState(null);
		  const [content, setContent] = useState('');
		  const [busy, setBusy] = useState(false);
		  const [notice, setNotice] = useState('');
		  useEffect(() => { setLoaded(null); setContent(''); setNotice(''); }, [profileId, file]);
		  const read = async () => {
		    setBusy(true); setNotice('');
		    try {
		      const value = await draftRequest('read', { profileId, file });
		      setLoaded(value); setContent(value.content);
		    } catch (error) { setNotice(String(error.message ?? error)); }
		    finally { setBusy(false); }
		  };
		  const save = async () => {
		    if (!loaded || loaded.profileId !== profileId || loaded.file !== file) return;
		    setBusy(true); setNotice('');
		    try {
		      const result = await draftRequest('save', { mode: 'training', profileId, file, content, expectedSha256: loaded.sha256 });
		      setLoaded({ ...loaded, content, sha256: result.sha256 });
		      setNotice(result.changed ? `草稿已保存；历史记录 ${result.historyId}。需新建训练复测，已有运行和发布快照不变。` : '内容未变化，无需保存。');
		    } catch (error) { setNotice(String(error.message ?? error)); }
		    finally { setBusy(false); }
		  };
		  return h('details', { className: 'ptc-cp-draft' },
		    h('summary', null, '训练草稿编辑'),
		    h('p', null, '这里只修改候选专家。保存不会修改已启动训练，也不会自动发布。'),
		    h('select', { 'aria-label': '草稿文件', value: file, disabled: busy, onChange: event => setFile(event.target.value) },
		      ...['instructions.md', 'profile.yaml', 'output-contract.schema.json'].map(name => h('option', { key: name, value: name }, name))),
		    h('button', { type: 'button', disabled: busy || !profileId, onClick: () => void read() }, '读取草稿'),
		    loaded ? h('div', null,
		      h('div', null, `SHA-256：${loaded.sha256}`),
		      h('textarea', { 'aria-label': '专家草稿内容', value: content, disabled: busy, rows: 18,
		        style: { width: '100%', fontFamily: 'monospace' }, onChange: event => setContent(event.target.value) }),
		      h('button', { type: 'button', disabled: busy || content === loaded.content, onClick: () => void save() }, '保存训练草稿')) : null,
		    notice ? h('p', { role: 'status' }, notice) : null);
		}
		
		/**
		 * PTC control-plane client: read-only panel components.
		 *
		 * Pure React via createElement (no JSX): the module must stay runnable as
		 * plain ESM source until the package entry bundles it. The panel renders the
		 * four mandatory read-only status items (identity, activeRelease, training
		 * runs, delivery) and reserves the Training / ATE PTC Runtime views as
		 * separate components so later phases can extend them without touching the
		 * shell wiring.
		 */
		
		/** Compact `label: value` status row. */
		function StatusRow({ label, value, testId }) {
		  return createElement(
		    "div",
		    { className: "ptc-cp-row", "data-testid": testId ?? label, key: testId ?? label },
		    createElement("span", { className: "ptc-cp-label", key: "label" }, label),
		    createElement("span", { className: "ptc-cp-value", key: "value" }, value)
		  );
		}
		
		/** Reserved Training view (PTC Training identity): trainingRuns list. */
		function TrainingView({ state, store, t }) {
		  const runs = state.trainingRuns;
		  const [selectedProfile, setSelectedProfile] = useState(state.profiles.some(p => p.profileId === 'ptc-dft-expert') ? 'ptc-dft-expert' : state.profiles[0]?.profileId ?? "");
		  const [busy, setBusy] = useState(false);
		  const [notice, setNotice] = useState(null);
		  const [testItem, setTestItem] = useState("TM109");
		  const stages = state.pipelineStages ?? [];
		  const [fromStage, setFromStage] = useState('');
		  const [toStage, setToStage] = useState('');
		  const selectedFrom = fromStage || stages[0] || '';
		  const selectedTo = toStage || stages.at(-1) || '';
		  let testItems = [];
		  try { testItems = parseTrainingTestItems(testItem); } catch { /* Invalid input keeps execution disabled. */ }
		  const rangeValid = stages.indexOf(selectedFrom) >= 0 && stages.indexOf(selectedTo) >= stages.indexOf(selectedFrom);
		
		  useEffect(() => {
		    if (selectedProfile === "" && state.profiles[0]?.profileId) {
		      setSelectedProfile(state.profiles.some(p => p.profileId === 'ptc-dft-expert') ? 'ptc-dft-expert' : state.profiles[0].profileId);
		    }
		  }, [selectedProfile, state.profiles]);
		
		  const createRun = async (target) => {
		    setBusy(true);
		    setNotice(null);
		    try {
		      const result = await createTrainingRunRequest(target);
		      await store.refresh();
		      let execution = null;
		      if (target.kind === "profile" && target.profileId === "ptc-dft-expert") {
		        execution = await executeTrainingRunRequest(result.runId, [testItem.trim().toUpperCase()]);
		      } else if (target.kind === 'pipeline') {
		        execution = await executeTrainingPipelineRequest(result.runId, parseTrainingTestItems(testItem));
		      }
		      await store.refresh();
		      const outcome = execution?.outcome?.mode ? ` · ${execution.outcome.mode}` : "";
		      const model = execution?.outcome?.modelDispatched === true
		        ? ` · ${t("training.modelDispatched")}`
		        : execution?.outcome?.modelDispatched === false ? ` · ${t("training.noModel")}` : "";
		      setNotice(`${t("training.created")}: ${result.runId}${outcome}${model}${target.kind === 'pipeline' ? ' · 流程训练请求已受理，请查看下方实时阶段；不代表已完成，不触发正式交付或发布。' : ''}`);
		    } catch (error) {
		      setNotice(`${t("training.createFailed")}: ${error instanceof Error ? error.message : String(error)}`);
		    } finally {
		      setBusy(false);
		    }
		  };
		  const stopRun = async (runId) => {
		    try {
		      await stopTrainingRunRequest(runId);
		      setNotice(`${runId}：已请求停止并撤销后续工具权限；子进程是否退出请看清理记录。`);
		      await store.refresh();
		    } catch (error) { setNotice(String(error.message ?? error)); }
		  };
		  const controlPipeline = async (runId, action) => {
		    setBusy(true);
		    try {
		      await controlTrainingPipelineRequest(runId, action);
		      setNotice(`${runId}：${action === 'pause' ? '已请求暂停，当前操作结束后暂停，不进入后续阶段。' : action === 'resume' ? '已请求继续训练。' : '已请求停止训练，退出结果请查看运行记录。'}`);
		      await store.refresh();
		    } catch (error) { setNotice(String(error.message ?? error)); }
		    finally { setBusy(false); }
		  };
		  return createElement(
		    "div",
		    { className: "ptc-cp-view ptc-cp-view-training", "data-testid": "ptc-cp-training-view" },
		    createElement(StatusRow, {
		      label: t("training.runs"),
		      value: String(runs.length),
		      testId: "ptc-cp-training-count"
		    }),
		    createElement(
		      "div",
		      { className: "ptc-cp-training-actions", "data-testid": "ptc-cp-training-actions", key: "actions" },
		      createElement(
		        "select",
		        {
		          value: selectedProfile,
		          disabled: busy || state.profiles.length === 0,
		          onChange: (event) => setSelectedProfile(event.target.value),
		          "aria-label": t("training.profile")
		        },
		        ...state.profiles.map((profile) => createElement(
		          "option", { value: profile.profileId, key: profile.profileId }, profile.profileId
		        ))
		      ),
		      createElement(
		        "input",
		        {
		          type: "text",
		          value: testItem,
		          disabled: busy,
		          onChange: (event) => setTestItem(event.target.value),
		          placeholder: "TM109,TM110",
		          "aria-label": t("training.testItem"),
		          "data-testid": "ptc-cp-training-tm"
		        }
		      ),
		      createElement(
		        "button",
		        {
		          type: "button",
		          disabled: busy || selectedProfile !== "ptc-dft-expert" || !/^TM[0-9]+$/i.test(testItem.trim()),
		          onClick: () => void createRun({ kind: "profile", profileId: selectedProfile }),
		          "data-testid": "ptc-cp-create-profile-training"
		        },
		        t("training.createProfile")
		      ),
		      createElement(
		        'label', null, '流程起始阶段 ',
		        createElement('select', {
		          value: selectedFrom, disabled: busy || !stages.length,
		          onChange: event => setFromStage(event.target.value), 'aria-label': '流程起始阶段',
		          'data-testid': 'ptc-cp-pipeline-from',
		        }, ...stages.map(stage => createElement('option', { key: stage, value: stage }, stage)))
		      ),
		      createElement(
		        'label', null, '流程结束阶段 ',
		        createElement('select', {
		          value: selectedTo, disabled: busy || !stages.length,
		          onChange: event => setToStage(event.target.value), 'aria-label': '流程结束阶段',
		          'data-testid': 'ptc-cp-pipeline-to',
		        }, ...stages.map(stage => createElement('option', { key: stage, value: stage, disabled: stages.indexOf(stage) < stages.indexOf(selectedFrom) }, stage)))
		      ),
		      createElement(
		        "button",
		        {
		          type: "button",
		          disabled: busy || !rangeValid || !testItems.length,
		          onClick: () => void createRun(pipelineTrainingTarget(stages, selectedFrom, selectedTo)),
		          "data-testid": "ptc-cp-create-pipeline-training"
		        },
		        '启动所选流程实验训练（不触发正式交付）'
		      ),
		      notice ? createElement("div", { className: "ptc-cp-notice", key: "notice" }, notice) : null
		    ),
		    createElement('p', null, '实验训练：默认 INPUT_SYNC 至 COMPILE；TM 列表以逗号分隔。只在本次训练目录生成产物，门禁失败即停，不触发正式交付、不发布。后段训练仍须满足已验证的前置条件；中断运行需人工核对回执，不会盲目重派。'),
		    !stages.length ? createElement('p', { className: 'ptc-cp-error' }, '阶段注册表尚未加载，流程入口暂不可用。') : null,
		    createElement(DraftEditor, { key: selectedProfile, profileId: selectedProfile }),
		    ...runs.map((run) => {
		      const targetLabel = formatTarget(run.target);
		      const itemLabel = run.testItems.length > 0 ? ` · ${run.testItems.join(",")}` : "";
		      const outcomeLabel = typeof run.outcome?.mode === "string" ? ` · ${run.outcome.mode}` : "";
		      const isPipeline = run.target?.kind === 'pipeline';
		      return createElement('div', { key: run.runId, className: 'ptc-cp-run' }, createElement(StatusRow, {
		        label: run.runId,
		        value: `${run.mode} · ${run.status}${targetLabel ? ` · ${targetLabel}` : ""}${itemLabel}${outcomeLabel}`,
		        testId: `ptc-cp-run-${run.runId}`
		      }),
		      run.artifactRoot ? createElement('div', null, `产物目录：${run.artifactRoot}`) : null,
		      (run.error || run.outcome?.reason) ? createElement('div', { className: 'ptc-cp-error' }, run.error || run.outcome.reason) : null,
		      isPipeline ? createElement('div', { 'data-testid': `ptc-cp-pipeline-${run.runId}` },
		        run.pipeline ? createElement('div', null,
		          createElement('div', null, `流程状态：${run.pipeline.status}`),
		          createElement('div', null, `当前阶段：${run.pipeline.stages.find(stage => stage.status !== 'completed')?.stage ?? (run.pipeline.status === 'completed' ? '已完成所选阶段' : '未知')}`),
		          run.pipeline.reason ? createElement('div', { className: 'ptc-cp-error' }, run.pipeline.reason) : null,
		          ...run.pipeline.stages.map(stage => createElement('details', { key: stage.stage },
		            createElement('summary', null, `${stage.stage} · ${stage.status}${stage.gateResult ? ` · 门禁 ${stage.gateResult.status ?? '未知'} (exit ${stage.gateResult.exitCode ?? '未知'})` : ' · 尚无门禁回执'}`),
		            stage.reason ? createElement('div', null, stage.reason) : null,
		            stage.gateResult ? createElement('pre', { style: { whiteSpace: 'pre-wrap' } }, JSON.stringify(stage.gateResult, null, 2)) : null)))
		          : createElement('div', null, '尚无流程进度文件；请等待准备结果，未据此认定派发或完成。'),
		        (run.status === 'interrupted' || run.pipeline?.status === 'interrupted')
		          ? createElement('p', { className: 'ptc-cp-error' }, '运行已中断：需人工核对专家回执与门禁记录，禁止盲目重派；此处不提供直接继续。')
		          : pipelineControlActions(run.status).map(action => createElement('button', {
		            key: action, type: 'button', disabled: busy, onClick: () => void controlPipeline(run.runId, action),
		            'aria-label': `${action} ${run.runId}`,
		          }, action === 'pause' ? '暂停流程训练' : action === 'resume' ? '继续流程训练' : '停止流程训练'))
		      ) : null,
		      !isPipeline && ['dispatching', 'running'].includes(run.status) ? createElement('button', {
		        type: 'button', onClick: () => void stopRun(run.runId), 'aria-label': `停止 ${run.runId}`
		      }, '停止训练') : null,
		      run.lifecycle ? createElement('details', null, createElement('summary', null, '执行与清理记录'),
		        createElement('pre', { style: { whiteSpace: 'pre-wrap' } }, JSON.stringify(run.lifecycle, null, 2))) : null);
		    })
		  );
		}
		
		/** Reserved ATE PTC Runtime view: latest delivery (single object or null). */
		function RuntimeView({ state, t }) {
		  const delivery = state.delivery;
		  return createElement(
		    "div",
		    { className: "ptc-cp-view ptc-cp-view-runtime", "data-testid": "ptc-cp-runtime-view" },
		    delivery === null
		      ? createElement(StatusRow, {
		          label: t("delivery.label"),
		          value: t("delivery.none"),
		          testId: "ptc-cp-delivery"
		        })
		      : createElement(
		          "div",
		          { className: "ptc-cp-delivery", "data-testid": "ptc-cp-delivery", key: "delivery" },
		          createElement(StatusRow, { label: t("delivery.batchId"), value: delivery.batchId, testId: "ptc-cp-delivery-batch" }),
		          createElement(StatusRow, { label: t("delivery.state"), value: delivery.state ?? "—", testId: "ptc-cp-delivery-state" }),
		          createElement(StatusRow, { label: t("delivery.releaseId"), value: delivery.releaseId ?? "—", testId: "ptc-cp-delivery-release" }),
		          createElement(StatusRow, { label: t("delivery.scope"), value: delivery.executionScope ?? "—", testId: "ptc-cp-delivery-scope" }),
		          createElement(StatusRow, { label: t("delivery.updatedAt"), value: delivery.updatedAt, testId: "ptc-cp-delivery-updated" })
		        )
		  );
		}
		
		/**
		 * Top-level read-only panel. Read-only by design: no write actions until a
		 * later phase wires them through an explicit control API.
		 */
		function PtcControlPanel({ store, t, onNavigate }) {
		  useSyncExternalStore(store.subscribe, store.getRevision, store.getRevision);
		  const state = store.getSnapshot();
		  const error = store.getLastError();
		  const [view, setView] = useState("training");
		
		  useEffect(() => {
		    store.start();
		    return () => store.stop();
		  }, [store]);
		
		  const switchTo = (next) => {
		    setView(next);
		    if (typeof onNavigate === "function") onNavigate(next);
		  };
		
		  const tabButton = (id, label) =>
		    createElement(
		      "button",
		      {
		        key: id,
		        type: "button",
		        className: view === id ? "ptc-cp-tab ptc-cp-tab-active" : "ptc-cp-tab",
		        "data-testid": `ptc-cp-tab-${id}`,
		        onClick: () => switchTo(id)
		      },
		      label
		    );
		
		  const release = state.activeRelease;
		
		  return createElement(
		    "div",
		    { className: "ptc-cp-panel", "data-testid": "ptc-cp-panel" },
		    createElement("div", { className: "ptc-cp-header", key: "header" }, t("panel.title")),
		    createElement(
		      "div",
		      { className: "ptc-cp-status", key: "status" },
		      createElement(StatusRow, { label: t("status.identity"), value: state.identity, testId: "ptc-cp-identity" }),
		      createElement(StatusRow, {
		        label: t("status.activeRelease"),
		        value: release
		          ? `${release.releaseId ?? "—"} (${release.manifestDigest ?? "—"})`
		          : t("status.noRelease"),
		        testId: "ptc-cp-active-release"
		      }),
		      createElement(StatusRow, {
		        label: t("status.trainingRuns"),
		        value: String(state.trainingRuns.length),
		        testId: "ptc-cp-training-runs"
		      }),
		      createElement(StatusRow, {
		        label: t("status.delivery"),
		        value: state.delivery === null ? t("delivery.none") : state.delivery.batchId,
		        testId: "ptc-cp-delivery-summary"
		      })
		    ),
		    createElement(
		      "div",
		      { className: "ptc-cp-tabs", key: "tabs" },
		      tabButton("training", t("view.training")),
		      tabButton("runtime", t("view.runtime"))
		    ),
		    view === "training"
		      ? createElement(TrainingView, { state, store, t, key: "training" })
		      : createElement(RuntimeView, { state, t, key: "runtime" }),
		    error
		      ? createElement(
		          "div",
		          { className: "ptc-cp-error", "data-testid": "ptc-cp-error", key: "error" },
		          `${t("status.error")}: ${error}`
		        )
		      : null
		  );
		}
		
		/**
		 * PTC control-plane client entry.
		 *
		 * Follows the DSH client-plugin module contract used by
		 * @nanmicoder/dsh-agent-teams: the bundled module exposes
		 *
		 *   exports.inject = [service names]
		 *   exports.apply  = (ctx) => { register slots / locale / effects }
		 *
		 * and the host loads it via window.__ModuleLoader__.load({ id, factory }).
		 * The package entry (owned by the integrator) re-exports these and declares
		 * the matching `dsh.client.inject` host packages in package.json.
		 *
		 * This skeleton only READS state from GET /api/ptc-control/state (see
		 * lib/control-state.js for the schemaVersion 1 contract) and mounts a
		 * read-only panel through the native client slot registry. It performs no
		 * writes and registers no commands.
		 */
		
		/** Locale namespace for this plugin. */
		const PTC_CONTROL_PLANE_LOCALE_NAMESPACE = "ptc-control-plane";
		
		/** Locale dictionaries (zh / en), mirroring the agent-teams pattern. */
		const localeDictionaries = {
		  zh: {
		    "panel.title": "PTC 控制面",
		    "status.identity": "当前身份",
		    "status.activeRelease": "活动 Release",
		    "status.trainingRuns": "训练运行",
		    "status.delivery": "正式交付",
		    "status.noRelease": "无活动 Release",
		    "status.error": "状态读取失败",
		    "view.training": "PTC Training",
		    "view.runtime": "ATE PTC Runtime",
		    "training.runs": "训练运行",
		    "training.profile": "选择专家",
		    "training.testItem": "测试项",
		    "training.createProfile": "创建单专家训练",
		    "training.createPipeline": "创建全流程训练",
		    "training.created": "已创建隔离训练运行",
		    "training.createFailed": "创建失败",
		    "training.noModel": "未派发模型",
		    "training.modelDispatched": "已派发训练专家",
		    "delivery.label": "正式交付",
		    "delivery.none": "暂无正式交付批次",
		    "delivery.batchId": "批次",
		    "delivery.state": "阶段",
		    "delivery.releaseId": "Release",
		    "delivery.scope": "执行范围",
		    "delivery.updatedAt": "更新时间"
		  },
		  en: {
		    "panel.title": "PTC Control Plane",
		    "status.identity": "Identity",
		    "status.activeRelease": "Active release",
		    "status.trainingRuns": "Training runs",
		    "status.delivery": "Delivery",
		    "status.noRelease": "No active release",
		    "status.error": "Failed to read state",
		    "view.training": "PTC Training",
		    "view.runtime": "ATE PTC Runtime",
		    "training.runs": "Training runs",
		    "training.profile": "Select expert",
		    "training.testItem": "Test item",
		    "training.createProfile": "Create profile training",
		    "training.createPipeline": "Create pipeline training",
		    "training.created": "Isolated training run created",
		    "training.createFailed": "Creation failed",
		    "training.noModel": "No model dispatched",
		    "training.modelDispatched": "Training expert dispatched",
		    "delivery.label": "Delivery",
		    "delivery.none": "No delivery batch yet",
		    "delivery.batchId": "Batch",
		    "delivery.state": "Stage",
		    "delivery.releaseId": "Release",
		    "delivery.scope": "Scope",
		    "delivery.updatedAt": "Updated"
		  }
		};
		
		/** Required host client services: slot registry and locale. */
		const inject = ["slots", "locale"];
		
		/** Slot mount point proven to exist in the current DSH web client. */
		const SHELL_SLOT_NAME = "shell.overlay";
		const PANEL_SLOT_ID = "ptc-control-plane";
		
		/**
		 * Install the plugin into a DSH client context.
		 *
		 * @param {{ slots: object, locale: object, effect: Function }} ctx
		 */
		function apply(ctx) {
		  ctx.effect(
		    () => ctx.locale.register(PTC_CONTROL_PLANE_LOCALE_NAMESPACE, localeDictionaries),
		    "ptc-control-plane: dictionaries"
		  );
		
		  const store = createPtcStateStore();
		
		  const Panel = ({ t }) =>
		    createElement(PtcControlPanel, { store, t });
		
		  // Native slot injection: the host places the panel in its overlay region.
		  ctx.slots.inject(SHELL_SLOT_NAME, () =>
		    ctx.slots.register(
		      {
		        name: SHELL_SLOT_NAME,
		        id: PANEL_SLOT_ID,
		        order: 90,
		        label: "PTC control plane",
		        locale: PTC_CONTROL_PLANE_LOCALE_NAMESPACE
		      },
		      Panel
		    )
		  );
		}
		exports.apply = apply;
		exports.inject = inject;
		return module.exports;
	}
});
