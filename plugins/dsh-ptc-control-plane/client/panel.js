import { createElement, useEffect, useState, useSyncExternalStore } from "react";
import { DraftEditor } from "./draft-editor.js";
import { TrainingIssueEditor } from './issue-editor.js';
import { createTrainingRunRequest, executeTrainingRunRequest, executeBusinessTrainingRunRequest, stopTrainingRunRequest, executeTrainingPipelineRequest, executeBusinessPipelineRequest, controlTrainingPipelineRequest, controlBusinessPipelineRequest, executeFrameworkRehearsalRequest, controlFrameworkRehearsalRequest, recoverFrameworkRehearsalRequest, publishFrameworkReleaseRequest, executePublishedFrameworkRequest, controlPublishedFrameworkRequest, executeProfileSmokeRequest, stopProfileSmokeRequest, executeSimpleOrchestrationRequest, controlSimpleOrchestrationRequest, publishTrainingReleaseRequest, freezeTrainingReleaseRequest, activateTrainingReleaseRequest, executeTrainingReleaseRequest, controlTrainingReleaseRequest, parseTrainingTestItems, pipelineTrainingTarget, pipelineControlActions, formatTarget, createPtcSessionWorkspaceRequest, workflowTemplateRequest, workflowTemplateReleaseRequest } from "./state.js";
import { openPtcNativeSession, ptcSessionKey } from "./native-sessions.js";
import { workflowStatusSummary } from './workflow-status.js';

async function trainerPagePost(operation, input) {
  const response = await fetch(`/api/ptc-control/trainer/${operation}`, {
    method: 'POST', headers: { Accept: 'application/json', 'Content-Type': 'application/json' },
    credentials: 'same-origin', body: JSON.stringify(input),
  });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok || payload.ok === false) throw new Error(payload.error?.message ?? payload.detail ?? `Trainer ${operation} failed`);
  return payload.value ?? payload;
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
export function StatusRow({ label, value, testId }) {
  return createElement(
    "div",
    { className: "ptc-cp-row", "data-testid": testId ?? label, key: testId ?? label },
    createElement("span", { className: "ptc-cp-label", key: "label" }, label),
    createElement("span", { className: "ptc-cp-value", key: "value" }, value)
  );
}

const ARITHMETIC_PROFILES = ['ptc-dft-expert', 'ptc-schematic-expert', 'strategy-expert',
  'method-expert', 'rule-reviewer', 'ate-implementer', 'compile-diagnostician', 'evolution-expert'];

// The DSH shell.overlay slot does not supply a layout or plugin stylesheet.
// Keep this self-contained so an unloaded stylesheet cannot cover the chat UI.
const PANEL_CSS = String.raw`
.ptc-cp-host, .ptc-cp-host * { box-sizing: border-box; }
.ptc-cp-host .ptc-cp-panel {
  position: fixed; z-index: 2147483000; top: 18px; right: 16px;
  width: min(1480px, calc(100vw - 32px)); max-height: calc(100vh - 36px);
  overflow: auto; overscroll-behavior: contain; color: #233044;
  background: #fff; border: 1px solid #dfe4eb; border-radius: 12px;
  box-shadow: 0 12px 32px #24334a18; font: 13px/1.45 "Segoe UI", "Microsoft YaHei", sans-serif;
  overflow-wrap: anywhere;
}
.ptc-cp-host .ptc-cp-panel[open] {
  inset: 12px; width: calc(100vw - 24px); max-height: calc(100vh - 24px);
  border-radius: 12px;
}
.ptc-cp-host .ptc-cp-panel:not([open]) { width: max-content; max-width: calc(100vw - 32px); overflow: visible; }
.ptc-cp-host .ptc-cp-panel > summary {
  display: block; list-style: none; cursor: pointer; padding: 11px 15px;
  background: #fff; color: #233044; font-weight: 700; border-radius: 12px 12px 0 0;
}
.ptc-cp-host .ptc-cp-panel > summary::-webkit-details-marker { display: none; }
.ptc-cp-host .ptc-cp-panel[open] > summary {
  position: sticky; top: 0; z-index: 1; border-radius: 12px 12px 0 0;
  border-bottom: 1px solid #e5e9ef;
}
.ptc-cp-host .ptc-cp-panel > :not(summary) { margin-left: 14px; margin-right: 14px; }
.ptc-cp-host .ptc-cp-panel > .ptc-cp-header { margin-top: 14px; font-size: 17px; font-weight: 700; }
.ptc-cp-host .ptc-cp-bridge-actions { display:flex; align-items:center; gap:9px; margin-top:8px; margin-bottom:6px; }
.ptc-cp-host .ptc-cp-bridge-actions button { color:#285db7; border-color:#b8cbed; background:#f7faff; }
.ptc-cp-host .ptc-cp-bridge-actions .ptc-cp-open-white-trainer { display:inline-block; color:#285db7; border:1px solid #b8cbed; background:#f7faff; border-radius:7px; padding:7px 10px; cursor:pointer; text-decoration:none; white-space:normal; }
.ptc-cp-host .ptc-cp-bridge-actions .ptc-cp-open-white-trainer:hover { background:#edf4ff; color:#285db7; }
.ptc-cp-host .ptc-cp-bridge-actions span { font-size:11px; }
.ptc-cp-host .ptc-cp-panel > .ptc-cp-view { margin-bottom: 16px; }
.ptc-cp-host .ptc-cp-status { display: grid; gap: 5px; margin-top: 8px; margin-bottom: 12px; }
.ptc-cp-host .ptc-cp-row { display: flex; gap: 8px; justify-content: space-between; min-width: 0; }
.ptc-cp-host .ptc-cp-label { flex: 0 0 auto; color: #657186; }
.ptc-cp-host .ptc-cp-value { text-align: right; min-width: 0; overflow-wrap: anywhere; color: #233044; }
.ptc-cp-host .ptc-cp-tabs { display: flex; gap: 7px; margin-bottom: 12px; }
.ptc-cp-host .ptc-cp-panel button, .ptc-cp-host .ptc-cp-panel select,
.ptc-cp-host .ptc-cp-panel input, .ptc-cp-host .ptc-cp-panel textarea {
  max-width: 100%; font: inherit;
}
.ptc-cp-host .ptc-cp-panel button {
  border: 1px solid #d5dce6; background: #fff; color: #4e5d73;
  border-radius: 7px; padding: 7px 10px; cursor: pointer;
  white-space: normal; text-align: left;
}
.ptc-cp-host .ptc-cp-panel button:hover:not(:disabled) { background: #edf4ff; color: #285db7; }
.ptc-cp-host .ptc-cp-panel button:disabled { opacity: .48; cursor: not-allowed; }
.ptc-cp-host .ptc-cp-tab-active { background: #2d60c8 !important; border-color: #2d60c8 !important; color: #fff !important; font-weight: 600; }
.ptc-cp-host .ptc-cp-panel select, .ptc-cp-host .ptc-cp-panel input,
.ptc-cp-host .ptc-cp-panel textarea {
  min-width: 0; background: #fff; color: #233044;
  border: 1px solid #d5dce6; border-radius: 6px; padding: 6px;
}
.ptc-cp-host .ptc-cp-training-actions { display: grid; grid-template-columns: 1fr 1fr; gap: 7px; margin-bottom: 13px; }
.ptc-cp-host .ptc-cp-training-actions label { grid-column: 1 / -1; display: grid; gap: 3px; }
.ptc-cp-host .ptc-cp-training-actions label select { width: 100%; }
.ptc-cp-host .ptc-cp-smoke-controls {
  display: grid; gap: 7px; margin: 12px 0; padding: 12px;
  border: 1px solid #dfe5ec; border-radius: 10px; background: #f8faff;
}
.ptc-cp-host .ptc-cp-smoke-controls p { margin: 0 0 5px; }
.ptc-cp-host .ptc-cp-smoke-controls button { width: 100%; }
.ptc-cp-host .ptc-cp-run {
  margin: 10px 0; padding: 10px; background: #fbfcfe;
  border: 1px solid #e0e6ee; border-radius: 9px;
}
.ptc-cp-host .ptc-cp-run .ptc-cp-row { display: block; }
.ptc-cp-host .ptc-cp-run .ptc-cp-label { display: block; color: #526581; font-weight: 700; }
.ptc-cp-host .ptc-cp-run .ptc-cp-value { display: block; text-align: left; }
.ptc-cp-host .ptc-cp-panel details:not(.ptc-cp-panel) { margin: 10px 0; padding: 7px; border: 1px solid #e1e7ef; border-radius: 7px; }
.ptc-cp-host .ptc-cp-panel pre { white-space: pre-wrap; overflow-wrap: anywhere; }
.ptc-cp-host .ptc-cp-error { color: #ffb9b9; margin: 7px 0; }
.ptc-cp-host .ptc-cp-notice { color: #187344; margin: 9px 0; }
.ptc-cp-host .ptc-cp-workbench { min-width: 0; }
.ptc-cp-host .ptc-cp-mode-tabs, .ptc-cp-host .ptc-cp-subtabs { display:flex; flex-wrap:wrap; gap:7px; margin:10px 0; }
.ptc-cp-host .ptc-cp-layout { display:grid; grid-template-columns:minmax(190px,232px) minmax(0,1fr) minmax(260px,350px); gap:18px; align-items:start; }
.ptc-cp-host .ptc-cp-roster { display:grid; align-content:start; gap:4px; max-height:62vh; overflow:auto; padding:8px 0; }
.ptc-cp-host .ptc-cp-roster button { width:100%; text-align:left; }
.ptc-cp-host .ptc-cp-roster-column { min-width:0; padding:4px 8px 10px 0; border-right:1px solid #e5e9ef; }
.ptc-cp-host .ptc-cp-side-title { padding:0 12px 8px; color:#93a0b3; font-size:10px; letter-spacing:1.35px; text-transform:uppercase; font-weight:700; }
.ptc-cp-host .ptc-cp-side-group { margin-top:20px; }
.ptc-cp-host .ptc-cp-side-title-with-count { display:flex; justify-content:space-between; align-items:center; }
.ptc-cp-host .ptc-cp-side-count { padding:2px 7px; border-radius:99px; background:#e8f0fc; color:#4d73b3; font-size:10px; letter-spacing:0; }
.ptc-cp-host .ptc-cp-side-nav { display:flex; align-items:center; width:100%; min-width:0; gap:7px; }
.ptc-cp-host .ptc-cp-side-nav .ptc-cp-side-symbol { flex:0 0 auto; color:#70819a; font-size:14px; }
.ptc-cp-host .ptc-cp-side-nav .ptc-cp-side-label { min-width:0; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
.ptc-cp-host .ptc-cp-workspace-main { min-width:0; }
.ptc-cp-host .ptc-cp-agent-status { display:flex; align-items:center; gap:8px; padding:8px; border:1px solid #dfe5ec; border-radius:8px; margin:5px 0; background:#fff; }
.ptc-cp-host .ptc-cp-agent-status span:first-child { flex:1; }
.ptc-cp-host .ptc-cp-stage-status { margin:8px 0; padding:9px; background:#f7f9fc; border:1px solid #e3e8ef; border-radius:8px; }
.ptc-cp-host .ptc-cp-stage-status ol { margin:7px 0; padding-left:22px; }
.ptc-cp-host .ptc-cp-stage-status li { padding:3px 0; }
.ptc-cp-host .ptc-cp-workflow-select { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:5px 10px; margin:10px 0; }
.ptc-cp-host .ptc-cp-workflow-select label { display:flex; gap:7px; align-items:center; }
.ptc-cp-host .ptc-cp-session-card, .ptc-cp-host .ptc-cp-publish-card { padding:12px; border:1px solid #dfe5ec; border-radius:10px; background:#fff; margin:10px 0; }
.ptc-cp-host .ptc-cp-resource-panel { margin:9px 0; padding:10px; border:1px solid #e3e8ef; border-radius:8px; background:#f7f9fc; }
.ptc-cp-host .ptc-cp-inspector { min-width:0; padding:4px 0 10px 16px; border-left:1px solid #e5e9ef; }
.ptc-cp-host .ptc-cp-inspector h3 { margin:0 0 4px; font-size:15px; }
.ptc-cp-host .ptc-cp-inspector-sub { margin:0 0 12px; color:#7b8799; font-size:12px; }
.ptc-cp-host .ptc-cp-inspector-card { padding:12px; border:1px solid #dfe5ed; border-radius:9px; background:#fff; margin-bottom:11px; }
.ptc-cp-host .ptc-cp-lock-note { padding:8px 9px; border-radius:7px; background:#f3f5f8; color:#718096; font-size:11px; margin-bottom:11px; }
.ptc-cp-host .ptc-cp-inspector-list { margin:8px 0 0; padding-left:17px; color:#52627a; font-size:11px; }
.ptc-cp-host .ptc-cp-resource-group { margin:9px 0; }
.ptc-cp-host .ptc-cp-resource-group h4 { margin:5px 0; }
.ptc-cp-host .ptc-cp-resource-group ul { margin:4px 0; padding-left:20px; }
.ptc-cp-host .ptc-cp-resource-group li { display:flex; gap:8px; justify-content:space-between; padding:3px 5px; border-radius:4px; }
.ptc-cp-host .ptc-cp-resource-used { color:#187344; background:#eaf8ef; }
.ptc-cp-host .ptc-cp-resource-unused { color:#718096; }
.ptc-cp-host .ptc-cp-resource-badge { flex:0 0 auto; color:#7b8799; font-size:11px; }
.ptc-cp-host .ptc-cp-resource-used .ptc-cp-resource-badge { color:#187344; font-weight:700; }
@media (max-width: 600px) {
  .ptc-cp-host .ptc-cp-panel { top: 8px; right: 8px; width: calc(100vw - 16px); max-height: calc(100vh - 16px); }
  .ptc-cp-host .ptc-cp-panel[open] { inset: 4px; width: calc(100vw - 8px); max-height: calc(100vh - 8px); }
  .ptc-cp-host .ptc-cp-training-actions { grid-template-columns: 1fr; }
  .ptc-cp-host .ptc-cp-workbench { min-width:0; width:calc(100vw - 32px); }
  .ptc-cp-host .ptc-cp-layout { grid-template-columns:1fr; }
  .ptc-cp-host .ptc-cp-roster-column, .ptc-cp-host .ptc-cp-inspector { border:0; padding:0; }
  .ptc-cp-host .ptc-cp-roster { grid-template-columns:repeat(2,minmax(0,1fr)); max-height:28vh; }
}
`;

function latestRun(runs, predicate) {
  // The run ID contains its creation timestamp. Directory mtime can change
  // later as evidence is inspected or amended, so it is not a source age.
  return [...runs].filter(predicate).sort((a, b) => String(b.runId).localeCompare(String(a.runId)))[0] ?? null;
}

function smokeSources(runs) {
  const profileRunIds = {};
  for (const profileId of ARITHMETIC_PROFILES) {
    const found = latestRun(runs, run => run.purpose === 'smoke-training'
      && run.target?.kind === 'profile' && run.target.profileId === profileId);
    // A newer pending/failed trial must not silently fall back to an older
    // successful snapshot when composing a new whole-team run.
    if (found?.status === 'completed' && found.outcome?.mode === 'SMOKE_ONLY'
        && found.outcome?.smokePassed === true && found.outcome?.businessGatePassed === false) {
      profileRunIds[profileId] = found.runId;
    }
  }
  const newestPipeline = latestRun(runs, run => run.purpose === 'smoke-training'
    && run.target?.kind === 'pipeline' && run.target.toStage === 'COMPILE');
  const pipeline = newestPipeline?.status === 'completed'
    && newestPipeline.outcome?.mode === 'SMOKE_ONLY' && newestPipeline.outcome?.smokePassed === true
    && newestPipeline.outcome?.businessGatePassed === false ? newestPipeline : null;
  const pipelineProfileRunIds = {};
  for (const value of Object.values(pipeline?.simpleOrchestration?.profileBindings ?? {})) {
    if (ARITHMETIC_PROFILES.includes(value?.profileId)
        && typeof value?.profileVersion === 'string' && value.profileVersion.startsWith('draft-')) {
      pipelineProfileRunIds[value.profileId] = value.profileVersion.slice('draft-'.length);
    }
  }
  return { profileRunIds, pipelineRunId: pipeline?.runId ?? null,
    pipelineProfileRunIds };
}

export function SmokeTrainingControls({ state, store, showProfiles = true, showWorkflow = true, showPublish = true }) {
  const [busy, setBusy] = useState(false);
  const [notice, setNotice] = useState(null);
  const sources = smokeSources(state.trainingRuns);
  const missing = ARITHMETIC_PROFILES.filter(id => !sources.profileRunIds[id]);
  const act = async (work, success) => {
    setBusy(true); setNotice(null);
    try { const result = await work(); await store.refresh(); setNotice(`${success}${result?.runId ? ` · ${result.runId}` : ''}`); }
    catch (error) { setNotice(`操作未完成：${error?.message ?? error}`); }
    finally { setBusy(false); }
  };
  return createElement('div', { className: 'ptc-cp-smoke-controls', 'data-testid': 'ptc-cp-smoke-controls' },
    createElement('p', null, '最小训练闭环：八位专家（含 DFT、原理图）分别真实派发相同的 1+2 JSON 算术任务；仅验证派发与回执。不读取私有业务材料、不生成业务产物、不运行业务门禁。以下全为 SMOKE_ONLY，业务门禁未通过。'),
    ...(showProfiles ? ARITHMETIC_PROFILES.map(profileId => createElement('button', {
      key: profileId, type: 'button', disabled: busy || !state.profiles.some(profile => profile.profileId === profileId),
      'data-testid': `ptc-cp-smoke-profile-${profileId}`,
      onClick: () => void act(async () => {
        const created = await createTrainingRunRequest({ kind: 'profile', profileId }, { purpose: 'smoke-training' });
        await executeProfileSmokeRequest(created.runId);
        return created;
      }, `${profileId} 算术训练已受理；等待数字 3 回执，非业务通过`),
    }, `单独训练 ${profileId}（1+2 JSON）`)) : []),
    showWorkflow ? createElement('div', null, missing.length
      ? `整体 smoke 尚缺：${missing.join('、')}`
      : '八个单专家算术回执已齐，可开始整体编排 smoke。') : null,
    showWorkflow ? createElement('button', { type: 'button', disabled: busy || missing.length > 0,
      'data-testid': 'ptc-cp-start-simple-orchestration',
      onClick: () => void act(async () => {
        const created = await createTrainingRunRequest({ kind: 'pipeline', fromStage: 'INPUT_SYNC', toStage: 'COMPILE' },
          { purpose: 'smoke-training' });
        await executeSimpleOrchestrationRequest(created.runId, sources.profileRunIds);
        return created;
      }, 'TM109 全流程 smoke 已受理；阶段只验证控制链路，业务门禁未通过'),
    }, '运行八专家整链 1+2 SMOKE_ONLY') : null,
    showPublish ? createElement('button', { type: 'button', disabled: busy || !sources.pipelineRunId
      || ARITHMETIC_PROFILES.some(id => !sources.pipelineProfileRunIds[id]),
      'data-testid': 'ptc-cp-publish-training-release',
      onClick: () => void act(() => publishTrainingReleaseRequest(sources.pipelineProfileRunIds, sources.pipelineRunId),
      '已发布冻结 smoke 版本；不是业务交付版本'),
    }, '发布已冻结的八专家 SMOKE_ONLY 版本（非业务）') : null,
    notice ? createElement('div', { className: 'ptc-cp-notice' }, notice) : null);
}

/** Reserved Training view (PTC Training identity): trainingRuns list. */
export function TrainingView({ state, store, t }) {
  const runs = state.trainingRuns;
  const [selectedProfile, setSelectedProfile] = useState(state.profiles.some(p => p.profileId === 'ptc-dft-expert') ? 'ptc-dft-expert' : state.profiles[0]?.profileId ?? "");
  const [busy, setBusy] = useState(false);
  const [notice, setNotice] = useState(null);
  const [testItem, setTestItem] = useState("TM109");
  const [trainingModelChoice, setTrainingModelChoice] = useState('default');
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

  const createRun = async (target, purpose = 'business-training') => {
    setBusy(true);
    setNotice(null);
    try {
      const result = await createTrainingRunRequest(target, { purpose });
      await store.refresh();
      let execution = null;
      if (target.kind === "profile" && target.profileId === "ptc-dft-expert") {
        execution = await executeTrainingRunRequest(result.runId, [testItem.trim().toUpperCase()]);
      } else if (target.kind === 'pipeline') {
        execution = purpose === 'framework-rehearsal'
          ? await executeFrameworkRehearsalRequest(result.runId, parseTrainingTestItems(testItem))
          : await executeTrainingPipelineRequest(result.runId, parseTrainingTestItems(testItem),
            { modelChoice: purpose === 'schematic-statistic-only' ? 'default' : trainingModelChoice });
      }
      await store.refresh();
      const outcome = execution?.outcome?.mode ? ` · ${execution.outcome.mode}` : "";
      const model = execution?.outcome?.modelDispatched === true
        ? ` · ${t("training.modelDispatched")}`
        : execution?.outcome?.modelDispatched === false ? ` · ${t("training.noModel")}` : "";
      setNotice(`${t("training.created")}: ${result.runId}${outcome}${model}${purpose === 'schematic-statistic-only' ? ' · 已受理仅生成 Component-Statistic；不派模型、不执行阶段门禁、不发布。' : purpose === 'framework-rehearsal' ? ' · 框架流程演练已受理；使用独立门禁，不代表真实业务门禁通过。' : target.kind === 'pipeline' ? ' · 流程训练请求已受理，请查看下方实时阶段；不代表已完成，不触发正式交付或发布。' : ''}`);
    } catch (error) {
      setNotice(`${t("training.createFailed")}: ${error instanceof Error ? error.message : String(error)}`);
    } finally {
      setBusy(false);
    }
  };
  const stopRun = async (runId) => {
    try {
      const run = runs.find(item => item.runId === runId);
      if (run?.purpose === 'smoke-training' && run.target?.kind === 'profile') await stopProfileSmokeRequest(runId);
      else await stopTrainingRunRequest(runId);
      setNotice(`${runId}：已请求停止并撤销后续工具权限；子进程是否退出请看清理记录。`);
      await store.refresh();
    } catch (error) { setNotice(String(error.message ?? error)); }
  };
  const controlPipeline = async (runId, action, purpose) => {
    setBusy(true);
    try {
      if (purpose === 'framework-rehearsal') await controlFrameworkRehearsalRequest(runId, action);
      else if (purpose === 'smoke-training') await controlSimpleOrchestrationRequest(runId, action);
      else await controlTrainingPipelineRequest(runId, action);
      setNotice(`${runId}：${action === 'pause' ? '已请求暂停，当前操作结束后暂停，不进入后续阶段。' : action === 'resume' ? '已请求继续训练。' : '已请求停止训练，退出结果请查看运行记录。'}`);
      await store.refresh();
    } catch (error) { setNotice(String(error.message ?? error)); }
    finally { setBusy(false); }
  };
  const publishFramework = async runId => {
    setBusy(true);
    try {
      const published = await publishFrameworkReleaseRequest(runId);
      setNotice(`${runId}：已发布非业务框架演练版本 ${published.releaseId}；不代表正式业务发布。`);
      await store.refresh();
    } catch (error) { setNotice(`框架演练发布失败：${error.message ?? error}`); }
    finally { setBusy(false); }
  };
  const recoverFramework = async runId => {
    setBusy(true);
    try {
      await recoverFrameworkRehearsalRequest(runId);
      setNotice(`${runId}：已请求显式核对持久化回执；无回执的在途阶段不会自动重派。`);
      await store.refresh();
    } catch (error) { setNotice(`演练恢复失败：${error.message ?? error}`); }
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
          disabled: true,
          "data-testid": "ptc-cp-create-profile-training"
        },
        '旧 DFT 业务训练入口已存档'
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
      createElement('label', null, '真实流程训练子专家模型 ',
        createElement('select', { value: trainingModelChoice, disabled: busy,
          onChange: event => setTrainingModelChoice(event.target.value),
          'aria-label': '真实流程训练子专家模型', 'data-testid': 'ptc-cp-pipeline-model' },
        createElement('option', { value: 'default' }, 'DSH 全局默认'),
        createElement('option', { value: 'deepseek-v4-flash' }, 'DeepSeek-V4-Flash'))),
      createElement(
        "button",
        {
          type: "button",
          disabled: true,
          onClick: () => void createRun(pipelineTrainingTarget(stages, selectedFrom, selectedTo)),
          "data-testid": "ptc-cp-create-pipeline-training"
        },
        '完整原理图流程已存档，暂不启动'
      ),
      createElement(
        'button',
        { type: 'button', disabled: true,
          'data-testid': 'ptc-cp-create-schematic-statistic-only' },
        '旧 Component-Statistic 脚本入口已存档'
      ),
      createElement(
        'button',
        {
          type: 'button',
          disabled: true,
          onClick: () => void createRun(pipelineTrainingTarget(stages, 'INPUT_SYNC', 'COMPILE'), 'framework-rehearsal'),
          'data-testid': 'ptc-cp-create-framework-rehearsal',
        },
        '全流程框架演练已存档，暂不启动'
      ),
      notice ? createElement("div", { className: "ptc-cp-notice", key: "notice" }, notice) : null
    ),
    createElement('p', null, '当前只开放下方八专家逐个算术训练与整体编排 SMOKE_ONLY。旧 DFT 业务训练、Component-Statistic 脚本和完整原理图流程均已存档，不参与本轮执行；smoke 不代表业务门禁通过。'),
    !stages.length ? createElement('p', { className: 'ptc-cp-error' }, '阶段注册表尚未加载，流程入口暂不可用。') : null,
    createElement(SmokeTrainingControls, { state, store }),
    createElement(DraftEditor, { key: selectedProfile, profileId: selectedProfile }),
    createElement(TrainingIssueEditor, { runs }),
    ...runs.map((run) => {
      const targetLabel = formatTarget(run.target);
      const itemLabel = run.testItems.length > 0 ? ` · ${run.testItems.join(",")}` : "";
      const outcomeLabel = typeof run.outcome?.mode === "string" ? ` · ${run.outcome.mode}` : "";
      const isPipeline = run.target?.kind === 'pipeline';
      const isRehearsal = run.purpose === 'framework-rehearsal';
      const isStatisticOnly = run.purpose === 'schematic-statistic-only';
      const isSmoke = run.purpose === 'smoke-training';
      return createElement('div', { key: run.runId, className: 'ptc-cp-run' }, createElement(StatusRow, {
        label: run.runId,
        value: `${isSmoke ? 'SMOKE_ONLY · 业务门禁未通过' : isRehearsal ? '框架演练' : isStatisticOnly ? '单项统计训练' : run.mode} · ${run.status}${targetLabel ? ` · ${targetLabel}` : ""}${itemLabel}${isPipeline && !isRehearsal && !isStatisticOnly && !isSmoke && run.modelChoice ? ` · 模型 ${run.modelChoice}` : ''}${outcomeLabel}${isRehearsal && run.status === 'completed' ? ' · 流程演练通过（非真实业务门禁）' : ''}`,
        testId: `ptc-cp-run-${run.runId}`
      }),
      run.artifactRoot ? createElement('div', null, `产物目录：${run.artifactRoot}`) : null,
      (run.error || run.outcome?.reason) ? createElement('div', { className: 'ptc-cp-error' }, run.error || run.outcome.reason) : null,
      isRehearsal && run.status === 'completed' ? createElement('button', {
        type: 'button', disabled: busy, onClick: () => void publishFramework(run.runId),
        'data-testid': `ptc-cp-publish-framework-${run.runId}`,
      }, '发布框架演练版本（非业务）') : null,
      isStatisticOnly && run.outcome?.report ? createElement('div', null,
        `仅统计产物：${run.outcome.report.outputPath} · SHA-256 ${run.outcome.report.outputSha256} · 阶段门禁未运行`) : null,
      isSmoke && isPipeline ? createElement('div', { 'data-testid': `ptc-cp-smoke-pipeline-${run.runId}` },
        run.simpleOrchestration ? createElement('div', null,
          createElement('div', null, `整体 smoke：${run.simpleOrchestration.status} · businessGatePassed=false`),
          run.simpleOrchestration.reason ? createElement('div', { className: 'ptc-cp-error' }, run.simpleOrchestration.reason) : null,
          ...(run.simpleOrchestration.stages ?? []).map(stage => createElement('div', { key: stage.stage },
            `${stage.stage} · ${stage.status} · SMOKE_ONLY`,
            ...(stage.tasks ?? []).map(task => createElement('div', { key: task.dispatchId },
              `${task.role} · ${task.status}${task.answer === 3 ? ' · JSON answer=3' : ''}`)))),
          ...(run.simpleOrchestration.auxiliaryTasks ?? []).map(task => createElement('div', { key: task.dispatchId },
            `辅助 ${task.role} · ${task.status}${task.answer === 3 ? ' · JSON answer=3' : ''}`)))
          : createElement('div', null, '等待整体 smoke 进度；尚未认定任何阶段完成。'),
        ...pipelineControlActions(run.status).map(action => createElement('button', {
          key: action, type: 'button', disabled: busy,
          onClick: () => void controlPipeline(run.runId, action, run.purpose),
          'aria-label': `${action} ${run.runId}`,
        }, action === 'pause' ? '暂停整体 smoke' : action === 'resume' ? '继续整体 smoke' : '停止整体 smoke'))
      ) : isPipeline && !isStatisticOnly ? createElement('div', { 'data-testid': `ptc-cp-pipeline-${run.runId}` },
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
          ? isRehearsal
            ? createElement('button', { type: 'button', disabled: busy,
              onClick: () => void recoverFramework(run.runId),
              'data-testid': `ptc-cp-recover-framework-${run.runId}` }, '核对回执并恢复框架演练')
            : createElement('p', { className: 'ptc-cp-error' }, '运行已中断：需人工核对专家回执与门禁记录，禁止盲目重派；此处不提供直接继续。')
          : pipelineControlActions(run.status).map(action => createElement('button', {
            key: action, type: 'button', disabled: busy, onClick: () => void controlPipeline(run.runId, action, run.purpose),
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
export function RuntimeView({ state, store, t }) {
  const delivery = state.delivery;
  const [busy, setBusy] = useState(false);
  const [notice, setNotice] = useState(null);
  const startPublished = async () => {
    setBusy(true);
    try {
      const result = await executePublishedFrameworkRequest();
      setNotice(`已从冻结版本 ${result.releaseId} 启动独立框架回放 ${result.runId}；不代表真实业务交付。`);
      await store.refresh();
    } catch (error) { setNotice(`发布模式启动失败：${error.message ?? error}`); }
    finally { setBusy(false); }
  };
  const controlPublished = async (runId, action) => {
    setBusy(true);
    try {
      await controlPublishedFrameworkRequest(runId, action);
      setNotice(`${runId}：已请求${action === 'pause' ? '暂停' : action === 'resume' ? '继续' : '停止'}。`);
      await store.refresh();
    } catch (error) { setNotice(`发布模式控制失败：${error.message ?? error}`); }
    finally { setBusy(false); }
  };
  const startPublishedSmoke = async () => {
    setBusy(true);
    try {
      const result = await executeTrainingReleaseRequest();
      setNotice(`已从八专家冻结算术 smoke 版本启动 TM109 发布态复跑 ${result.runId ?? ''}；业务门禁未通过。`);
      await store.refresh();
    } catch (error) { setNotice(`发布态 smoke 启动失败：${error.message ?? error}`); }
    finally { setBusy(false); }
  };
  const stopPublishedSmoke = async runId => {
    setBusy(true);
    try {
      await controlTrainingReleaseRequest(runId, 'stop');
      setNotice(`${runId}：已请求停止发布态 smoke；请查看终态确认。`);
      await store.refresh();
    } catch (error) { setNotice(`发布态 smoke 停止失败：${error.message ?? error}`); }
    finally { setBusy(false); }
  };
  return createElement(
    "div",
    { className: "ptc-cp-view ptc-cp-view-runtime", "data-testid": "ptc-cp-runtime-view" },
    createElement(StatusRow, { label: '活动八专家算术训练发布版本（SMOKE_ONLY；非业务）',
      value: state.activeTrainingRelease?.releaseId ?? '尚未发布',
      testId: 'ptc-cp-active-training-release' }),
    state.trainingReleaseError ? createElement('div', { className: 'ptc-cp-error' },
      `训练发布版本校验失败：${state.trainingReleaseError}`) : null,
    createElement('button', { type: 'button',
      disabled: busy || !state.activeTrainingRelease || !!state.trainingReleaseError,
      onClick: () => void startPublishedSmoke(), 'data-testid': 'ptc-cp-execute-training-release' },
    '从八专家冻结版本复跑 TM109 SMOKE_ONLY（业务门禁未通过）'),
    ...(state.publishedSmokeRuns ?? []).map(run => createElement('div', { key: run.runId, className: 'ptc-cp-run' },
      createElement(StatusRow, { label: run.runId ?? '未知运行',
        value: `${run.status} · ${run.releaseId ?? '无版本'} · SMOKE_ONLY · 业务门禁未通过` }),
      run.outcome?.reason ? createElement('div', { className: 'ptc-cp-error' }, run.outcome.reason) : null,
      ['running', 'preparing', 'dispatching', 'pausing', 'paused'].includes(run.status)
        ? createElement('button', { type: 'button', disabled: busy,
          onClick: () => void stopPublishedSmoke(run.runId),
          'data-testid': `ptc-cp-stop-training-release-${run.runId}` }, '停止发布态 smoke') : null)),
    createElement(StatusRow, { label: '框架演练发布版本（非业务）',
      value: state.activeFrameworkRelease?.releaseId ?? '尚未发布',
      testId: 'ptc-cp-framework-release' }),
    state.frameworkReleaseError ? createElement('div', { className: 'ptc-cp-error' },
      `框架发布完整性校验失败：${state.frameworkReleaseError}`) : null,
    createElement('button', { type: 'button', disabled: busy || !state.activeFrameworkRelease || !!state.frameworkReleaseError,
      onClick: () => void startPublished(), 'data-testid': 'ptc-cp-start-published-framework' },
    '从冻结版本执行框架回放（非业务）'),
    notice ? createElement('div', { className: 'ptc-cp-notice' }, notice) : null,
    ...state.publishedFrameworkRuns.map(run => createElement('div', { key: run.runId, className: 'ptc-cp-run' },
      createElement(StatusRow, { label: run.runId ?? '未知运行', value: `${run.status} · ${run.releaseId ?? '无版本'} · 冻结框架回放（非业务）` }),
      (run.reason || run.outcome?.reason) ? createElement('div', { className: 'ptc-cp-error' }, run.reason || run.outcome.reason) : null,
      ...(['running', 'preparing'].includes(run.status) ? ['pause', 'stop'] : run.status === 'paused' ? ['resume', 'stop'] : [])
        .map(action => createElement('button', { key: action, type: 'button', disabled: busy,
          onClick: () => void controlPublished(run.runId, action),
          'aria-label': `${action} ${run.runId}` },
        action === 'pause' ? '暂停发布框架回放' : action === 'resume' ? '继续发布框架回放' : '停止发布框架回放')),
      ...run.stages.map(stage => createElement('div', { key: stage.stage }, `${stage.stage} · ${stage.status}`)))),
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

const PROFILE_LABELS = Object.freeze({
  'ptc-dft-expert': 'DFT 专家', 'ptc-schematic-expert': '原理图专家',
  'strategy-expert': '策略专家', 'method-expert': '方法专家', 'rule-reviewer': '规则评审',
  'ate-implementer': 'ATE 实现', 'compile-diagnostician': '编译诊断', 'evolution-expert': '演进专家',
});

function latestSmokeRun(runs, predicate) {
  return [...runs].filter(predicate).sort((a, b) => String(b.runId).localeCompare(String(a.runId)))[0] ?? null;
}

const FROZEN_CANDIDATE_STORAGE_KEY = 'ptc-smoke-frozen-candidate';
const STAGED_WORKFLOW_TEMPLATE_KEY = 'ptc-staged-workflow-template-release';
function readFrozenCandidate() {
  try {
    const value = JSON.parse(window.localStorage.getItem(FROZEN_CANDIDATE_STORAGE_KEY) ?? 'null');
    return value && typeof value.releaseId === 'string' && typeof value.stagingId === 'string'
      && typeof value.bundleDigest === 'string' ? value : null;
  } catch { return null; }
}
function readStagedWorkflowTemplate() {
  try {
    const value = JSON.parse(window.localStorage.getItem(STAGED_WORKFLOW_TEMPLATE_KEY) ?? 'null');
    return value && typeof value.releaseId === 'string' && typeof value.manifestSha256 === 'string'
      ? value : null;
  } catch { return null; }
}

function WorkflowStatusBar({ state }) {
  const run = latestSmokeRun(state.trainingRuns, item => item.purpose === 'smoke-training'
    && item.target?.kind === 'pipeline');
  const orchestration = run?.simpleOrchestration;
  const stages = Array.isArray(orchestration?.stages) ? orchestration.stages : [];
  const summary = workflowStatusSummary(orchestration);
  return createElement('section', { className: 'ptc-cp-stage-status', 'data-testid': 'ptc-cp-workflow-status' },
    createElement('strong', null, '团队工作流执行状态'),
    createElement('div', null, run ? `${run.runId} · ${run.status} · ${orchestration?.scope === 'INPUT_SYNC_PILOT' ? '双专家 INPUT_SYNC 试点' : '八专家整链'} · SMOKE_ONLY · 业务门禁未通过` : '尚无烟测记录'),
    run ? createElement('div', { 'data-testid': 'ptc-cp-workflow-progress' },
      `已完成 ${summary.completed}/${summary.total} · 当前 ${summary.currentProfileId ?? '无'}${summary.currentStatus ? `（${summary.currentStatus}）` : ''}${summary.handoffFrom ? ` · 交接 ${summary.handoffFrom} → ${summary.currentProfileId}` : ''}`) : null,
    orchestration?.reason ? createElement('div', { className: 'ptc-cp-error' }, orchestration.reason) : null,
    stages.length ? createElement('ol', null, ...stages.map(stage => createElement('li', { key: stage.stage },
      `${stage.stage} · ${stage.status} · ${(stage.tasks ?? []).map(task =>
        `${task.profileId ?? task.role}: ${task.status}${typeof task.answer === 'number' ? ` / answer=${task.answer}` : ''}`
      ).join('；')}`))) : null,
    (orchestration?.auxiliaryTasks ?? []).map(task => createElement('div', { key: task.dispatchId },
      `附加角色 ${task.profileId ?? task.role} · ${task.status}${typeof task.answer === 'number' ? ` / answer=${task.answer}` : ''}`)),
    run?.outcome?.smokePassed === true ? createElement('div', { className: 'ptc-cp-notice' }, 'Captain 已确认本次所有数字 JSON 回执为 3；仅证明烟测控制链路，不代表业务通过。') : null);
}

function PublishedSmokeView({ state, store }) {
  const [busy, setBusy] = useState(false);
  const [notice, setNotice] = useState('');
  const [frozenCandidate, setFrozenCandidate] = useState(readFrozenCandidate);
  const execute = async () => {
    setBusy(true); setNotice('');
    try { const result = await executeTrainingReleaseRequest(); await store.refresh(); setNotice(`已从冻结版本启动发布态复跑 ${result.runId ?? ''}；业务门禁未通过。`); }
    catch (error) { setNotice(`发布态复跑失败：${error.message ?? error}`); }
    finally { setBusy(false); }
  };
  return createElement('div', { className: 'ptc-cp-publish-card', 'data-testid': 'ptc-cp-published-smoke' },
    createElement('h3', null, '发布态（冻结版本只读复跑）'),
    createElement(StatusRow, { label: '当前冻结版本', value: state.activeTrainingRelease?.releaseId ?? '未发布' }),
    state.trainingReleaseError ? createElement('div', { className: 'ptc-cp-error' }, state.trainingReleaseError) : null,
    createElement('button', { type: 'button', disabled: busy || !state.activeTrainingRelease || !!state.trainingReleaseError,
      onClick: () => void execute(), 'data-testid': 'ptc-cp-execute-training-release' }, '复跑冻结版本 1+2 SMOKE_ONLY'),
    notice ? createElement('div', { role: 'status', className: 'ptc-cp-notice' }, notice) : null,
    ...(state.publishedSmokeRuns ?? []).map(run => createElement('div', { key: run.runId, className: 'ptc-cp-run' },
      `${run.runId ?? '未知运行'} · ${run.status} · ${run.releaseId ?? '无版本'} · SMOKE_ONLY · 业务门禁未通过`)));
}

function BusinessResourceList({ title, items }) {
  return createElement('div', { className: 'ptc-cp-resource-group' },
    createElement('h4', null, title),
    items.length ? createElement('ul', null, ...items.map(item => createElement('li', {
      key: item.path, className: item.used ? 'ptc-cp-resource-used' : 'ptc-cp-resource-unused' },
      createElement('span', null, item.path), createElement('span', { className: 'ptc-cp-resource-badge' }, item.used ? '本次使用' : '已加载'))))
      : createElement('p', null, '暂无已加载项'));
}

function BusinessTrainingControls({ state, store }) {
  const [page, setPage] = useState('run');
  const [selectedAgentId, setSelectedAgentId] = useState('ptc-dft-expert');
  const [testItem, setTestItem] = useState('TM109');
  const [modelChoice, setModelChoice] = useState('default');
  const [busy, setBusy] = useState(false);
  const [notice, setNotice] = useState('');
  const businessRuns = (state.trainingRuns ?? []).filter(run => run.purpose === 'business-training');
  const latestDft = latestRun(businessRuns, run => run.target?.kind === 'profile'
    && run.target.profileId === 'ptc-dft-expert');
  const latestInputSync = latestRun(businessRuns, run => run.target?.kind === 'pipeline'
    && run.target.fromStage === 'INPUT_SYNC' && run.target.toStage === 'INPUT_SYNC');
  const items = (() => { try { return parseTrainingTestItems(testItem); } catch { return null; } })();
  const act = async work => {
    setBusy(true); setNotice('');
    try { const result = await work(); await store.refresh(); setNotice(`真实业务运行已受理${result?.runId ? ` · ${result.runId}` : ''}`); }
    catch (error) { setNotice(`业务运行未启动：${error?.message ?? error}`); }
    finally { setBusy(false); }
  };
  const launchDft = () => void act(async () => {
    if (!items) throw new Error('请输入有效的 TM 编号，例如 TM109');
    const created = await createTrainingRunRequest({ kind: 'profile', profileId: selectedAgentId }, { purpose: 'business-training' });
    return executeBusinessTrainingRunRequest(created.runId, items, { modelChoice });
  });
  const launchInputSync = () => void act(async () => {
    if (!items) throw new Error('请输入有效的 TM 编号，例如 TM109');
    const created = await createTrainingRunRequest({ kind: 'pipeline', fromStage: 'INPUT_SYNC', toStage: 'INPUT_SYNC',
      workflowId: 'tm109-input-sync', workflowRevision: 'business-v1', agentBindings: {
        'schematic-expert': { profileId: 'ptc-schematic-expert' },
        'dft-expert': { profileId: selectedAgentId },
      } }, { purpose: 'business-training' });
    return executeBusinessPipelineRequest(created.runId, items, { modelChoice });
  });
  const controlInputSync = action => void act(() => controlBusinessPipelineRequest(latestInputSync?.runId, action));
  const inputSyncControls = latestInputSync
    ? pipelineControlActions(latestInputSync.status).map(action => createElement('button', { key: action, type: 'button', disabled: busy,
      onClick: () => controlInputSync(action) }, action === 'pause' ? '暂停' : action === 'resume' ? '继续' : '停止'))
    : [];
  const inputSyncStatusText = latestInputSync
    ? ['INPUT_SYNC', latestInputSync.runId, latestInputSync.status,
      latestInputSync.outcome?.mode ?? '等待终态', latestInputSync.outcome?.stage ? `当前 ${latestInputSync.outcome.stage}` : null]
      .filter(Boolean).join(' · ')
    : '';
  const businessAgents = Array.isArray(state.businessAgents) ? state.businessAgents : [];
  const selectedAgent = businessAgents.find(agent => agent.profileId === selectedAgentId) ?? businessAgents[0] ?? null;
  const inputSyncStatus = latestInputSync ? createElement('div', { className: 'ptc-cp-stage-status', 'data-testid': 'ptc-cp-business-input-sync-status' },
    inputSyncStatusText,
    ...inputSyncControls) : null;
  const runChildren = [
    createElement('h3', null, '真实业务 Agent · 原理图专家 → DFT 专家 INPUT_SYNC'),
    createElement('p', null, '这里才会读取冻结到本次 Training_Materials/runs/<runId> 的业务材料：原理图先由固定 host 解析器生成七项产物，再由原理图 Agent 做只读语义审查；审查通过后才进入 DFT，由 DFT Agent 处理并做语义审查。结果只写本次训练运行目录，不发布业务版本。'),
    createElement('label', null, 'TM 编号 ', createElement('input', { value: testItem, disabled: busy,
      onChange: event => setTestItem(event.target.value), 'data-testid': 'ptc-cp-business-test-items' })),
    createElement('label', null, '业务 DFT Agent ', createElement('select', { value: selectedAgentId, disabled: busy,
      onChange: event => setSelectedAgentId(event.target.value), 'data-testid': 'ptc-cp-business-agent' },
      ...businessAgents.filter(agent => agent.kind === 'dft').map(agent => createElement('option', { key: agent.profileId, value: agent.profileId }, `${agent.displayName} · ${agent.profileId}`)))),
    createElement('label', null, '模型 ', createElement('select', { value: modelChoice, disabled: busy,
      onChange: event => setModelChoice(event.target.value), 'data-testid': 'ptc-cp-business-model' },
      createElement('option', { value: 'default' }, '默认模型'),
      createElement('option', { value: 'deepseek-v4-flash' }, 'DeepSeek V4 Flash'))),
    createElement('div', { className: 'ptc-cp-training-actions' },
      createElement('button', { type: 'button', disabled: busy || !items,
        onClick: launchDft, 'data-testid': 'ptc-cp-business-dft' }, '运行真实 DFT Agent'),
      createElement('button', { type: 'button', disabled: busy || !items,
        onClick: launchInputSync, 'data-testid': 'ptc-cp-business-input-sync' }, '运行真实 原理图 → DFT INPUT_SYNC')),
    latestDft ? createElement('div', { className: 'ptc-cp-stage-status', 'data-testid': 'ptc-cp-business-dft-status' },
      ['DFT', latestDft.runId, latestDft.status, latestDft.outcome?.mode ?? '等待终态', latestDft.outcome?.reason].filter(Boolean).join(' · ')) : null,
    inputSyncStatus,
    notice ? createElement('div', { className: 'ptc-cp-notice', role: 'status' }, notice) : null,
  ];
  const resourceTabs = createElement('div', { className: 'ptc-cp-subtabs', role: 'tablist' },
    createElement('button', { type: 'button', className: page === 'run' ? 'ptc-cp-tab-active' : '',
      onClick: () => setPage('run'), 'data-testid': 'ptc-cp-business-page-run' }, '运行记录'),
    createElement('button', { type: 'button', className: page === 'io' ? 'ptc-cp-tab-active' : '',
      onClick: () => setPage('io'), 'data-testid': 'ptc-cp-business-page-io' }, '输入 / 输出'),
    createElement('button', { type: 'button', className: page === 'resources' ? 'ptc-cp-tab-active' : '',
      onClick: () => setPage('resources'), 'data-testid': 'ptc-cp-business-page-resources' }, 'Skill / 脚本'));
  const agentPicker = selectedAgent ? createElement('label', { className: 'ptc-cp-business-agent-picker' }, '查看 Agent ',
    createElement('select', { value: selectedAgent.profileId, onChange: event => setSelectedAgentId(event.target.value) },
      ...businessAgents.map(agent => createElement('option', { key: agent.profileId, value: agent.profileId }, `${agent.displayName} · ${agent.profileId}`)))) : null;
  const resourcePanel = page === 'io' && selectedAgent
    ? createElement('div', { className: 'ptc-cp-resource-panel', 'data-testid': 'ptc-cp-business-io' },
      agentPicker, createElement('p', null, `最新业务运行：${selectedAgent.latestRunId ?? '尚未运行'} · ${selectedAgent.latestRunStatus ?? '无状态'}`),
      createElement(BusinessResourceList, { title: '输入材料', items: selectedAgent.inputs }),
      createElement(BusinessResourceList, { title: '输出材料', items: selectedAgent.outputs }))
    : page === 'resources' && selectedAgent
      ? createElement('div', { className: 'ptc-cp-resource-panel', 'data-testid': 'ptc-cp-business-resources' },
        agentPicker, createElement('p', null, '绿色“本次使用”表示最新业务运行已留下对应证据；其余条目是该 Agent 的完整加载清单。'),
        createElement(BusinessResourceList, { title: 'Skills / 规则', items: selectedAgent.skills }),
        createElement(BusinessResourceList, { title: '脚本', items: selectedAgent.scripts }))
      : page !== 'run' ? createElement('div', { className: 'ptc-cp-resource-panel' }, '尚未加载业务 Agent 清单；先启动一次 BUSINESS_ONLY 训练。') : null;
  const children = [
    createElement('h3', null, '真实业务 Agent · 原理图专家 → DFT 专家 INPUT_SYNC'),
    resourceTabs,
    resourcePanel,
    ...(page === 'run' ? runChildren : []),
  ];
  return createElement('section', { className: 'ptc-cp-session-card', 'data-testid': 'ptc-cp-business-training' }, ...children);
}

function PtcWorkbench({ state, store, sessionServices }) {
  const [mode, setMode] = useState('training');
  const [trainingMode, setTrainingMode] = useState('agent');
  const [selectedProfile, setSelectedProfile] = useState(ARITHMETIC_PROFILES[0]);
  const [workflowProfiles, setWorkflowProfiles] = useState(ARITHMETIC_PROFILES.slice(0, 2));
  const [templateName, setTemplateName] = useState('ATE PTC 工作流烟测模板');
  const [templateDraftSha, setTemplateDraftSha] = useState(null);
  const [frozenTemplateSha, setFrozenTemplateSha] = useState(null);
  const [savedTemplateSignature, setSavedTemplateSignature] = useState(null);
  const [frozenCandidate, setFrozenCandidate] = useState(readFrozenCandidate);
  const [stagedTemplateRelease, setStagedTemplateRelease] = useState(readStagedWorkflowTemplate);
  const [busy, setBusy] = useState(false);
  const [notice, setNotice] = useState('');
  const sources = smokeSources(state.trainingRuns);
  const templateSignature = JSON.stringify({ name: templateName.trim(), profileIds: workflowProfiles });
  const templateDirty = savedTemplateSignature !== templateSignature;
  const latestTemplateRun = (state.workflowTemplateRuns ?? []).find(item => item.templateId === 'ate-ptc') ?? null;
  const latestPublishedTemplateRun = (state.publishedWorkflowTemplateRuns ?? [])[0] ?? null;
  useEffect(() => {
    let mounted = true;
    void workflowTemplateRequest('read', { templateId: 'ate-ptc' }).then(result => {
      if (!mounted || !result.template) return;
      setTemplateName(result.template.name);
      setWorkflowProfiles(result.template.profileIds);
      setTemplateDraftSha(result.sha256);
      setFrozenTemplateSha(result.frozenSha256 ?? null);
      setSavedTemplateSignature(JSON.stringify({ name: result.template.name, profileIds: result.template.profileIds }));
    }).catch(() => {});
    return () => { mounted = false; };
  }, []);
  const selectedWorkflowIds = new Set(workflowProfiles);
  const pilotSelection = selectedWorkflowIds.size === 2
    && ARITHMETIC_PROFILES.slice(0, 2).every(id => selectedWorkflowIds.has(id));
  const fullSelection = selectedWorkflowIds.size === ARITHMETIC_PROFILES.length
    && ARITHMETIC_PROFILES.every(id => selectedWorkflowIds.has(id));
  const pilotPassed = !!latestSmokeRun(state.trainingRuns, item => item.purpose === 'smoke-training'
    && item.target?.kind === 'pipeline' && item.target.toStage === 'INPUT_SYNC'
    && item.status === 'completed' && item.outcome?.smokePassed === true
    && item.simpleOrchestration?.scope === 'INPUT_SYNC_PILOT');
  const selectedProfileRun = latestSmokeRun(state.trainingRuns, item => item.purpose === 'smoke-training'
    && item.target?.kind === 'profile' && item.target.profileId === selectedProfile);
  const run = async (action, doneText) => {
    setBusy(true); setNotice('');
    try { const result = await action(); await store.refresh(); setNotice(`${doneText}${result?.runId ? ` · ${result.runId}` : ''}`); }
    catch (error) { setNotice(`未完成：${error?.message ?? error}`); }
    finally { setBusy(false); }
  };
  const openSession = async (kind, identity, request, title) => {
    setBusy(true); setNotice('正在创建/打开 DSH 原生会话…');
    try {
      const workspace = await createPtcSessionWorkspaceRequest(request);
      await openPtcNativeSession(sessionServices, workspace, { key: ptcSessionKey(kind, identity), title });
      setNotice(`已打开 DSH 原生会话：${title}`);
      window.setTimeout(() => document.querySelector('[data-testid="ptc-cp-panel"]')?.removeAttribute('open'), 0);
    } catch (error) { setNotice(`会话未打开：${error?.message ?? error}`); }
    finally { setBusy(false); }
  };
  const freezeProfile = profileId => void run(async () => {
    const created = await createTrainingRunRequest({ kind: 'profile', profileId }, { purpose: 'smoke-training' });
    await executeProfileSmokeRequest(created.runId);
    return created;
  }, `${PROFILE_LABELS[profileId]}独立 1+2 验证已受理；请以运行终态为准（SMOKE_ONLY）`);
  const launchWorkflow = () => void run(async () => {
    if (!fullSelection) throw new Error('八专家整链须先勾选全部八位 Agent');
    const missing = ARITHMETIC_PROFILES.filter(id => !sources.profileRunIds[id]);
    if (missing.length) throw new Error(`先完成单 Agent 烟测：${missing.join('、')}`);
    const created = await createTrainingRunRequest({ kind: 'pipeline', fromStage: 'INPUT_SYNC', toStage: 'COMPILE' }, { purpose: 'smoke-training' });
    await executeSimpleOrchestrationRequest(created.runId, sources.profileRunIds);
    return created;
  }, '八专家整链 1+2 烟测已派发；业务门禁未通过');
  const launchPilot = () => void run(async () => {
    if (!pilotSelection) throw new Error('双专家试点须只勾选 DFT 与原理图专家');
    const pair = ARITHMETIC_PROFILES.slice(0, 2);
    const missing = pair.filter(id => !sources.profileRunIds[id]);
    if (missing.length) throw new Error(`先完成双专家单体烟测：${missing.join('、')}`);
    const created = await createTrainingRunRequest({ kind: 'pipeline', fromStage: 'INPUT_SYNC', toStage: 'INPUT_SYNC' }, { purpose: 'smoke-training' });
    await executeSimpleOrchestrationRequest(created.runId,
      Object.fromEntries(pair.map(id => [id, sources.profileRunIds[id]])), { pilot: true });
    return created;
  }, '双专家 INPUT_SYNC 顺序交接烟测已派发；业务门禁未通过');
  const freezeWorkflow = () => void run(async () => {
    if (!fullSelection) throw new Error('冻结整链须勾选全部八位 Agent');
    if (!sources.pipelineRunId || ARITHMETIC_PROFILES.some(id => !sources.pipelineProfileRunIds[id])) {
      throw new Error('须先完成八专家单体和整链烟测');
    }
    const candidate = await freezeTrainingReleaseRequest(sources.pipelineProfileRunIds, sources.pipelineRunId);
    window.localStorage.setItem(FROZEN_CANDIDATE_STORAGE_KEY, JSON.stringify(candidate));
    setFrozenCandidate(candidate);
    return candidate;
  }, '工作流版本已独立冻结，尚未发布');
  const saveTemplate = () => void run(async () => {
    const result = await workflowTemplateRequest('save', { expectedSha256: templateDraftSha,
      template: { templateId: 'ate-ptc', name: templateName, profileIds: workflowProfiles,
        instruction: '1+2等于几，把答案写在JSON里', expectedAnswer: 3 } });
    setTemplateDraftSha(result.sha256);
    setSavedTemplateSignature(templateSignature);
    setFrozenTemplateSha(null);
    return result;
  }, '已保存工作流候选；尚未冻结或发布');
  const freezeTemplate = () => void run(async () => {
    if (templateDirty || !templateDraftSha) throw new Error('先保存当前工作流候选');
    const result = await workflowTemplateRequest('freeze', { templateId: 'ate-ptc', sha256: templateDraftSha });
    setFrozenTemplateSha(result.versionSha256);
    return result;
  }, '已冻结工作流模板；尚未发布');
  const executeTemplate = () => void run(async () => {
    if (templateDirty || !frozenTemplateSha) throw new Error('先保存并冻结当前工作流模板');
    return workflowTemplateRequest('execute', { templateId: 'ate-ptc', versionSha256: frozenTemplateSha });
  }, '任意 Agent 工作流 1+2 烟测已派发');
  const controlTemplate = action => void run(() => workflowTemplateRequest('control',
    { runId: latestTemplateRun?.runId, action }), `工作流${action}请求已受理`);
  const stageTemplateRelease = () => void run(async () => {
    if (!latestTemplateRun || latestTemplateRun.status !== 'completed' || latestTemplateRun.smokePassed !== true) {
      throw new Error('先完成任意 Agent 模板的 1+2 烟测');
    }
    const staged = await workflowTemplateReleaseRequest('stage', { runId: latestTemplateRun.runId });
    window.localStorage.setItem(STAGED_WORKFLOW_TEMPLATE_KEY, JSON.stringify(staged));
    setStagedTemplateRelease(staged);
    return staged;
  }, '已冻结发布候选；尚未激活');
  const activateTemplateRelease = () => void run(async () => {
    if (!stagedTemplateRelease) throw new Error('没有待激活的工作流模板版本');
    const result = await workflowTemplateReleaseRequest('activate', {
      releaseId: stagedTemplateRelease.releaseId,
      manifestSha256: stagedTemplateRelease.manifestSha256,
    });
    window.localStorage.removeItem(STAGED_WORKFLOW_TEMPLATE_KEY);
    setStagedTemplateRelease(null);
    return result;
  }, '任意 Agent 工作流模板已发布激活');
  const executePublishedTemplate = () => void run(() =>
    workflowTemplateReleaseRequest('execute', {}), '冻结模板发布态新运行已派发');
  const controlPublishedTemplate = action => void run(() => workflowTemplateReleaseRequest('control',
    { runId: latestPublishedTemplateRun?.runId, action }), `发布态工作流${action}请求已受理`);
  const activateWorkflow = () => void run(async () => {
    if (!frozenCandidate?.stagingId) throw new Error('没有待发布的冻结版本');
    const active = await activateTrainingReleaseRequest(frozenCandidate.stagingId);
    window.localStorage.removeItem(FROZEN_CANDIDATE_STORAGE_KEY);
    setFrozenCandidate(null);
    return active;
  }, '已激活冻结版本');
  const modes = [['training', '训练模式'], ['publish', '发布模式'], ['engineering', '工程模式']];
  const button = (id, label, active, onClick, extra = {}) => createElement('button', { key: id, type: 'button',
    className: active ? 'ptc-cp-tab-active' : '', 'data-testid': `ptc-cp-mode-${id}`, onClick, ...extra }, label);
  const agentList = createElement('nav', { className: 'ptc-cp-roster', 'aria-label': 'Agent 列表', 'data-testid': 'ptc-cp-agent-roster' },
    ...ARITHMETIC_PROFILES.map(id => createElement('button', { key: id, type: 'button',
      disabled: busy || mode !== 'training', className: selectedProfile === id ? 'ptc-cp-tab-active' : '',
      'data-testid': `ptc-cp-agent-${id}`,
      onClick: () => { setSelectedProfile(id); void openSession('agent', id, { mode: 'agent', profileId: id }, `PTC Training · ${PROFILE_LABELS[id]}`); },
    }, `${PROFILE_LABELS[id]} · ${id}`)));
  let content;
  if (mode === 'training') {
    content = createElement('div', { className: 'ptc-cp-workbench' },
      createElement('div', { className: 'ptc-cp-layout' },
      createElement('aside', { className: 'ptc-cp-roster-column', 'data-testid': 'ptc-cp-agent-sidebar' },
        createElement('div', { className: 'ptc-cp-side-group' },
          createElement('div', { className: 'ptc-cp-side-title ptc-cp-side-title-with-count' },
            createElement('span', null, 'AGENTS'),
            createElement('span', { className: 'ptc-cp-side-count' }, String(ARITHMETIC_PROFILES.length))),
          agentList),
        createElement('div', { className: 'ptc-cp-side-group' },
          createElement('div', { className: 'ptc-cp-side-title ptc-cp-side-title-with-count' },
            createElement('span', null, '工作流'),
            createElement('span', { className: 'ptc-cp-side-count' }, '1')),
          createElement('button', { type: 'button', className: `ptc-cp-side-nav ${trainingMode === 'workflow' ? 'ptc-cp-tab-active' : ''}`,
            onClick: () => setTrainingMode('workflow'), 'data-testid': 'ptc-cp-workflow-sidebar' },
            createElement('span', { className: 'ptc-cp-side-symbol' }, '⌘'),
            createElement('span', { className: 'ptc-cp-side-label' }, templateName || 'ATE PTC 工作流')))),
      createElement('main', { className: 'ptc-cp-workspace-main' },
        createElement(BusinessTrainingControls, { state, store }),
        createElement('div', { className: 'ptc-cp-subtabs' },
          button('single', '单 Agent 训练', trainingMode === 'agent', () => setTrainingMode('agent')),
          button('workflow', 'Agent 工作流训练', trainingMode === 'workflow', () => setTrainingMode('workflow'))),
        trainingMode === 'agent' ? createElement('section', { className: 'ptc-cp-session-card', 'data-testid': 'ptc-cp-agent-training' },
          createElement('h3', null, `${PROFILE_LABELS[selectedProfile]} · 独立训练`),
          createElement('p', null, '点左侧专家立即打开其专属 DSH 会话；会话工作目录绑定该专家草稿目录。聊天中逐步讨论/修改，下面的“保存训练草稿”单独保存候选内容。'),
          createElement('button', { type: 'button', disabled: busy, onClick: () => void openSession('agent', selectedProfile,
            { mode: 'agent', profileId: selectedProfile }, `PTC Training · ${PROFILE_LABELS[selectedProfile]}`),
          'data-testid': 'ptc-cp-open-selected-agent' }, '打开独立 DSH 训练会话'),
          createElement('div', { className: 'ptc-cp-agent-status' }, createElement('span', null, '单 Agent 1+2 验证/冻结快照'),
            createElement('button', { type: 'button', disabled: busy, onClick: () => freezeProfile(selectedProfile),
              'data-testid': `ptc-cp-freeze-profile-${selectedProfile}` }, '冻结此版并验证')),
          selectedProfileRun ? createElement('div', { 'data-testid': 'ptc-cp-selected-profile-run' },
            `${selectedProfileRun.runId} · ${selectedProfileRun.status} · ${selectedProfileRun.outcome?.smokePassed === true ? '数字 JSON answer=3 已验证' : '等待新鲜回执/未通过'} · SMOKE_ONLY`) : null,
          createElement(DraftEditor, { key: selectedProfile, profileId: selectedProfile }),
          createElement('p', null, '冻结会新建一次 SMOKE_ONLY 训练并把本次 Agent 文件、哈希、模型数字 JSON 答案封存到不可变运行快照；它不发布业务版本。'))
          : createElement('section', { className: 'ptc-cp-session-card', 'data-testid': 'ptc-cp-workflow-training' },
            createElement('h3', null, '工作流协作训练'),
            createElement('p', null, '勾选并排序任意 Agent，可保存、冻结和执行独立的 1+2 工作流模板。下方原有的双专家试点与八专家整链按钮仍按 PTC 阶段注册表运行；它们和任意组合模板烟测是两条不同链路，均不代表真实业务门禁通过。会话中的建议须明确保存后才会成为候选。'),
            createElement('div', { className: 'ptc-cp-workflow-select' }, ...ARITHMETIC_PROFILES.map(id => createElement('label', { key: id },
              createElement('input', { type: 'checkbox', checked: workflowProfiles.includes(id), disabled: busy,
                onChange: event => setWorkflowProfiles(old => event.target.checked ? [...new Set([...old, id])] : old.filter(item => item !== id)) }),
              PROFILE_LABELS[id]))),
            createElement('div', { className: 'ptc-cp-session-card', 'data-testid': 'ptc-cp-generic-workflow-template' },
              createElement('h4', null, '任意 Agent 顺序工作流 · SMOKE_ONLY'),
              createElement('label', null, '模板名称 ', createElement('input', { value: templateName,
                onChange: event => setTemplateName(event.target.value), maxLength: 120,
                'data-testid': 'ptc-cp-template-name' })),
              createElement('ol', { 'data-testid': 'ptc-cp-template-order' }, ...workflowProfiles.map((id, index) =>
                createElement('li', { key: id }, `${index + 1}. ${PROFILE_LABELS[id] ?? id} `,
                  createElement('button', { type: 'button', disabled: busy || index === 0,
                    onClick: () => setWorkflowProfiles(old => { const next = [...old]; [next[index - 1], next[index]] = [next[index], next[index - 1]]; return next; }) }, '上移'),
                  createElement('button', { type: 'button', disabled: busy || index === workflowProfiles.length - 1,
                    onClick: () => setWorkflowProfiles(old => { const next = [...old]; [next[index + 1], next[index]] = [next[index], next[index + 1]]; return next; }) }, '下移')))),
              createElement('button', { type: 'button', disabled: busy || !workflowProfiles.length || !templateDirty,
                onClick: saveTemplate, 'data-testid': 'ptc-cp-save-workflow-template' }, '保存工作流草稿'),
              createElement('button', { type: 'button', disabled: busy || templateDirty || !templateDraftSha,
                onClick: freezeTemplate, 'data-testid': 'ptc-cp-freeze-workflow-template' }, '冻结工作流模板（不发布）'),
              createElement('button', { type: 'button', disabled: busy || templateDirty || !frozenTemplateSha,
                onClick: executeTemplate, 'data-testid': 'ptc-cp-execute-workflow-template' }, '执行所选 Agent 1+2 烟测'),
              createElement('div', null, `草稿 SHA-256：${templateDraftSha ?? '未保存'} · 冻结 SHA-256：${frozenTemplateSha ?? '未冻结'}`),
              latestTemplateRun ? createElement('div', { 'data-testid': 'ptc-cp-template-run-status' },
                `${latestTemplateRun.runId} · ${latestTemplateRun.status} · 已完成 ${latestTemplateRun.steps?.filter(step => step.status === 'completed').length ?? 0}/${latestTemplateRun.steps?.length ?? 0} · 当前 ${latestTemplateRun.currentProfileId ?? '无'}${latestTemplateRun.reason ? ` · ${latestTemplateRun.reason}` : ''}`) : null,
              latestTemplateRun?.steps?.length ? createElement('ol', { 'data-testid': 'ptc-cp-template-step-status' },
                ...latestTemplateRun.steps.map(step => createElement('li', { key: step.index },
                  `${PROFILE_LABELS[step.profileId] ?? step.profileId} · ${step.status}${step.answer === 3 ? ' · answer=3' : ''}${step.upstreamEvidenceSha256 ? ` · 上游 SHA-256 ${step.upstreamEvidenceSha256.slice(0, 12)}…` : ''}`))) : null,
              latestTemplateRun && ['running', 'paused'].includes(latestTemplateRun.status)
                ? createElement('div', null,
                  createElement('button', { type: 'button', disabled: busy || latestTemplateRun.status !== 'running',
                    onClick: () => controlTemplate('pause') }, '暂停'),
                  createElement('button', { type: 'button', disabled: busy || latestTemplateRun.status !== 'paused',
                    onClick: () => controlTemplate('resume') }, '继续'),
                  createElement('button', { type: 'button', disabled: busy || latestTemplateRun.status !== 'running',
                    onClick: () => controlTemplate('stop') }, '停止')) : null),
            createElement('button', { type: 'button', disabled: busy || !workflowProfiles.length,
              onClick: () => void openSession('workflow', `v2:${workflowProfiles.join(',')}`,
                { mode: 'workflow', profileIds: workflowProfiles }, `PTC Training · 工作流 · ${workflowProfiles.length} Agents`),
              'data-testid': 'ptc-cp-open-workflow-session' }, '打开工作流 DSH 会话'),
            createElement(WorkflowStatusBar, { state }),
            createElement('button', { type: 'button', disabled: busy || !pilotSelection || ARITHMETIC_PROFILES.slice(0, 2).some(id => !sources.profileRunIds[id]),
              onClick: launchPilot, 'data-testid': 'ptc-cp-start-input-sync-pilot' }, '执行双专家 INPUT_SYNC 交接烟测'),
            createElement('button', { type: 'button', disabled: busy || !fullSelection || !pilotPassed || ARITHMETIC_PROFILES.some(id => !sources.profileRunIds[id]),
              onClick: launchWorkflow, 'data-testid': 'ptc-cp-start-simple-orchestration' }, '执行八专家整链 1+2 烟测'),
            createElement('button', { type: 'button', disabled: busy || !fullSelection || !sources.pipelineRunId
              || ARITHMETIC_PROFILES.some(id => !sources.pipelineProfileRunIds[id]),
              onClick: freezeWorkflow, 'data-testid': 'ptc-cp-freeze-workflow' }, '冻结当前整链版本（不发布）'),
            frozenCandidate ? createElement('div', { className: 'ptc-cp-notice', 'data-testid': 'ptc-cp-frozen-candidate' },
              `已冻结待发布：${frozenCandidate.releaseId} · SHA-256 ${frozenCandidate.bundleDigest}`) : null,
            createElement('p', null, '通过标准：整链每个 child receipt 的 JSON answer 都是数字 3，Captain 验证通过；结果仅为 SMOKE_ONLY。'))),
      createElement('aside', { className: 'ptc-cp-inspector', 'data-testid': 'ptc-cp-agent-inspector' },
        createElement('h3', null, PROFILE_LABELS[selectedProfile] ?? selectedProfile),
        createElement('p', { className: 'ptc-cp-inspector-sub' }, 'Agent 配置与执行状态'),
        createElement('div', { className: 'ptc-cp-lock-note' }, '训练模式可编辑草稿；发布与工程模式使用冻结版本。'),
        createElement('div', { className: 'ptc-cp-inspector-card' },
          createElement(StatusRow, { label: 'Agent ID', value: selectedProfile }),
          createElement(StatusRow, { label: '工作流候选', value: `${workflowProfiles.length} 个` }),
          createElement(StatusRow, { label: '最新运行', value: selectedProfileRun?.status ?? '未运行' }),
          createElement('ul', { className: 'ptc-cp-inspector-list' },
            createElement('li', null, '输入：1+2 等于几'),
            createElement('li', null, '输出：JSON answer=3'),
            createElement('li', null, '范围：SMOKE_ONLY'))),
        selectedProfileRun ? createElement('div', { className: 'ptc-cp-inspector-card' },
          createElement('strong', null, '最近验收'),
          createElement('p', null, `${selectedProfileRun.runId} · ${selectedProfileRun.outcome?.smokePassed === true ? '通过' : selectedProfileRun.status}`)) : null),
        notice ? createElement('div', { className: 'ptc-cp-notice', role: 'status' }, notice) : null));
  } else if (mode === 'publish') {
    content = createElement('section', { className: 'ptc-cp-publish-card', 'data-testid': 'ptc-cp-publish-mode' },
      createElement('h3', null, '发布模式'),
      createElement('div', { className: 'ptc-cp-session-card', 'data-testid': 'ptc-cp-template-publish' },
        createElement('h4', null, '任意 Agent 工作流模板发布'),
        createElement('p', null, '仅发布完成 1+2 烟测的冻结模板及精确 Agent 回执绑定；真实业务门禁仍为 false。'),
        createElement('button', { type: 'button', disabled: busy || latestTemplateRun?.status !== 'completed'
          || latestTemplateRun?.smokePassed !== true, onClick: stageTemplateRelease,
          'data-testid': 'ptc-cp-stage-template-release' }, '冻结发布候选'),
        stagedTemplateRelease ? createElement('div', null,
          `待激活 ${stagedTemplateRelease.releaseId} · SHA-256 ${stagedTemplateRelease.manifestSha256}`,
          createElement('button', { type: 'button', disabled: busy, onClick: activateTemplateRelease,
            'data-testid': 'ptc-cp-activate-template-release' }, '发布/激活模板版本')) : null,
        createElement(StatusRow, { label: '当前模板发布版',
          value: state.activeWorkflowTemplateRelease?.releaseId ?? '未发布' })),
      createElement('p', null, '发布模式使用已冻结的八专家快照。当前后端发布动作会先复核快照完整性与全部 1+2 回执，再激活版本；没有业务产物或业务门禁。'),
      createElement('button', { type: 'button', disabled: busy,
        onClick: () => void openSession('publish', 'review', { mode: 'publish' }, 'PTC Publish · 冻结版本审核'),
        'data-testid': 'ptc-cp-open-publish-session' }, '打开隔离的发布审核 DSH 会话'),
      frozenCandidate ? createElement('div', { className: 'ptc-cp-agent-status' },
        createElement('span', null, `待发布冻结版本 ${frozenCandidate.releaseId} · ${frozenCandidate.bundleDigest}`),
        createElement('button', { type: 'button', disabled: busy, onClick: activateWorkflow,
          'data-testid': 'ptc-cp-activate-frozen-workflow' }, '发布/激活此冻结版本'))
        : createElement('p', null, '尚无待发布的冻结工作流版本。先在“训练模式 → Agent 工作流训练”完成整链并单独冻结，再回到此处发布。'),
      createElement(PublishedSmokeView, { state, store }));
  } else {
    const releaseId = state.activeWorkflowTemplateRelease?.releaseId ?? state.activeTrainingRelease?.releaseId;
    content = createElement('section', { className: 'ptc-cp-publish-card', 'data-testid': 'ptc-cp-engineering-mode' },
      createElement('h3', null, '工程模式'),
      createElement('p', null, '工程会话绑定当前已冻结版本的标识，并使用隔离目录；不会把已冻结 Agent/编排目录作为可写工作区。这里用于观察/沟通，不提供候选规则编辑入口。'),
      createElement(StatusRow, { label: '固定版本', value: releaseId ?? '尚无已冻结版本' }),
      createElement('div', { className: 'ptc-cp-session-card', 'data-testid': 'ptc-cp-template-engineering' },
        createElement('h4', null, '任意 Agent 工作流模板 · 发布态'),
        createElement(StatusRow, { label: '固定模板版本',
          value: state.activeWorkflowTemplateRelease?.releaseId ?? '未发布' }),
        state.workflowTemplateReleaseError ? createElement('div', { className: 'ptc-cp-error' },
          state.workflowTemplateReleaseError) : null,
        createElement('button', { type: 'button', disabled: busy || !state.activeWorkflowTemplateRelease,
          onClick: executePublishedTemplate, 'data-testid': 'ptc-cp-execute-published-template' },
        '从冻结模板新运行 1+2'),
        latestPublishedTemplateRun ? createElement('div', { 'data-testid': 'ptc-cp-published-template-status' },
          `${latestPublishedTemplateRun.runId} · ${latestPublishedTemplateRun.status} · 已完成 ${latestPublishedTemplateRun.steps?.filter(step => step.status === 'completed').length ?? 0}/${latestPublishedTemplateRun.steps?.length ?? 0} · 当前 ${latestPublishedTemplateRun.currentProfileId ?? '无'}${latestPublishedTemplateRun.reason ? ` · ${latestPublishedTemplateRun.reason}` : ''}`) : null,
        latestPublishedTemplateRun?.steps?.length ? createElement('ol', { 'data-testid': 'ptc-cp-published-template-steps' },
          ...latestPublishedTemplateRun.steps.map(step => createElement('li', { key: step.index },
            `${PROFILE_LABELS[step.profileId] ?? step.profileId} · ${step.status}${step.answer === 3 ? ' · answer=3' : ''}${step.upstreamEvidenceSha256 ? ` · 上游 SHA-256 ${step.upstreamEvidenceSha256.slice(0, 12)}…` : ''}`))) : null,
        latestPublishedTemplateRun && ['running', 'paused'].includes(latestPublishedTemplateRun.status)
          ? createElement('div', null,
            createElement('button', { type: 'button', disabled: busy || latestPublishedTemplateRun.status !== 'running',
              onClick: () => controlPublishedTemplate('pause') }, '暂停'),
            createElement('button', { type: 'button', disabled: busy || latestPublishedTemplateRun.status !== 'paused',
              onClick: () => controlPublishedTemplate('resume') }, '继续'),
            createElement('button', { type: 'button', disabled: busy || latestPublishedTemplateRun.status !== 'running',
              onClick: () => controlPublishedTemplate('stop') }, '停止')) : null),
      createElement('button', { type: 'button', disabled: busy || !releaseId,
        onClick: () => void openSession('engineering', releaseId, { mode: 'engineering', releaseId }, `PTC Engineering · ${releaseId}`),
        'data-testid': 'ptc-cp-open-engineering-session' }, '打开工程沟通 DSH 会话'),
      createElement(PublishedSmokeView, { state, store }));
  }
  return createElement('div', { className: 'ptc-cp-workbench', 'data-testid': 'ptc-cp-workbench' },
    createElement('div', { className: 'ptc-cp-mode-tabs', 'data-testid': 'ptc-cp-mode-tabs' },
      ...modes.map(([id, label]) => button(id, label, mode === id, () => setMode(id)))),
    createElement('div', { className: 'ptc-cp-status' },
      createElement(StatusRow, { label: '当前发布版', value: state.activeTrainingRelease?.releaseId ?? '无' }),
      createElement(StatusRow, { label: '训练运行', value: String(state.trainingRuns.length) }),
      createElement(StatusRow, { label: '烟测边界', value: '1+2 JSON / SMOKE_ONLY / 业务门禁未通过' })),
    content);
}

/** Native DSH workbench for agent training, workflow rehearsal and frozen replay. */
export function PtcControlPanel({ store, t, onNavigate, sessionServices }) {
  useSyncExternalStore(store.subscribe, store.getRevision, store.getRevision);
  const state = store.getSnapshot();
  const error = store.getLastError();
  const [view, setView] = useState("training");

  useEffect(() => {
    store.start();
    return () => store.stop();
  }, [store]);

  useEffect(() => {
    const trainerWorkbenchOrigins = new Set([
      window.location.origin,
      'http://127.0.0.1:8123',
      'http://localhost:8123',
    ]);
    const trainerStorageRequestPrefix = 'dsh-agent-trainer-bridge:request:';
    const trainerStorageResponsePrefix = 'dsh-agent-trainer-bridge:response:';
    const onWorkbenchMessage = async event => {
      const data = event?.data;
      // The formal white prototype is sometimes served by the local static
      // preview on :8123. Keep the same-origin check for normal DSH tabs, but
      // explicitly allow that trusted local origin for a window.opener bridge.
      if (!trainerWorkbenchOrigins.has(event.origin) || data?.type !== 'dsh-agent-trainer-open-session') return;
      const reply = payload => event.source?.postMessage({ type: 'dsh-agent-trainer-session-result', bridgeId: data.bridgeId, ...payload }, event.origin);
      try {
        if (!sessionServices) throw new Error('DSH 原生会话服务尚未注入，请从 DSH ATE Trainer 按钮打开白色工作台。');
        const request = data.request;
        if (!request || !['agent', 'workflow'].includes(request.targetKind) || typeof request.targetId !== 'string') throw new Error('Trainer 会话目标不完整');
        const workspace = await trainerPagePost('session-workspace', request);
        const title = data.title || `Agent Trainer · ${request.targetId}`;
        const opened = await openPtcNativeSession(sessionServices, { path: workspace.path || workspace.cwd }, {
          key: ptcSessionKey(request.targetKind, `trainer:${request.targetId}:${request.selectedRunId || 'none'}`), title, agentPreset: 'agent-trainer',
        });
        const binding = await trainerPagePost('bind-session', {
          ...request, sessionId: opened.sessionId, presetId: 'agent-trainer', selectedRunId: request.selectedRunId || null,
        });
        reply({ ok: true, sessionId: opened.sessionId, binding, title });
      } catch (error) {
        reply({ ok: false, error: error?.message ?? String(error) });
      }
    };
    window.addEventListener('message', onWorkbenchMessage);
    const channel = typeof BroadcastChannel === 'function' ? new BroadcastChannel('dsh-agent-trainer-bridge') : null;
    const onChannelMessage = event => onWorkbenchMessage({ origin: window.location.origin, data: event.data,
      source: { postMessage: payload => channel?.postMessage(payload) } });
    channel?.addEventListener('message', onChannelMessage);
    const onStorageMessage = event => {
      if (!event.key?.startsWith(trainerStorageRequestPrefix) || !event.newValue) return;
      let data;
      try { data = JSON.parse(event.newValue); } catch { return; }
      if (!data?.bridgeId || data.type !== 'dsh-agent-trainer-open-session') return;
      const responseKey = `${trainerStorageResponsePrefix}${data.bridgeId}`;
      const source = { postMessage: payload => {
        try { window.localStorage.setItem(responseKey, JSON.stringify(payload)); } catch { /* storage is best effort */ }
      } };
      void onWorkbenchMessage({ origin: window.location.origin, data, source });
    };
    window.addEventListener('storage', onStorageMessage);
    return () => {
      window.removeEventListener('message', onWorkbenchMessage);
      window.removeEventListener('storage', onStorageMessage);
      channel?.removeEventListener('message', onChannelMessage);
      channel?.close();
    };
  }, [sessionServices]);

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
    { className: "ptc-cp-host" },
    createElement("style", { type: "text/css" }, PANEL_CSS),
    createElement(
    "details",
    { className: "ptc-cp-panel", "data-testid": "ptc-cp-panel" },
    createElement("summary", null, "PTC 控制面 · 点击展开/收起"),
    createElement("div", { className: "ptc-cp-header", key: "header" }, t("panel.title")),
    createElement("div", { className: "ptc-cp-bridge-actions", key: "bridge" },
      createElement("a", { href: "/agent-trainer", target: "_blank", rel: "opener", className: "ptc-cp-open-white-trainer", "data-testid": "ptc-cp-open-white-trainer" }, "打开白色 Agent Trainer"),
      createElement("span", { className: "ptc-cp-label" }, "正式产品界面 / 唯一验收入口")),
    createElement(
      "div",
      { className: "ptc-cp-host-capability", key: "status" },
      "DSH 原生会话桥接已启用；训练、发布和工程操作请在白色 Agent Trainer 中完成。"
    ),
    error
      ? createElement(
          "div",
          { className: "ptc-cp-error", "data-testid": "ptc-cp-error", key: "error" },
          `${t("status.error")}: ${error}`
        )
      : null
    )
  );
}
