import { createElement, useEffect, useState, useSyncExternalStore } from 'react';
import { createTrainerStore, trainerControlState, TRAINER_UNBOUND_NOTICE } from './trainer-state.js';
import { createTrainerNavigator } from './trainer-native.js';
import { trainerNewAgentChanges, trainerNewWorkflowChanges, trainerAppendStep, trainerMoveStep, trainerFrozenVersionsFor, trainerFrozenVersionLabel, trainerStepVersion, trainerMatchingEvidence } from './trainer-assets.js';

export const TRAINER_STYLES = `
.trainer-ui{font:13px/1.5 system-ui,sans-serif;color:var(--dsw-alias-label-primary,#203029);box-sizing:border-box}
.trainer-ui *{box-sizing:border-box}.trainer-ui button,.trainer-ui select,.trainer-ui input,.trainer-ui textarea{font:inherit;color:inherit}
.trainer-ui button{cursor:pointer;border:1px solid #c9d7ce;background:var(--dsw-alias-button-elevated-fill,#fff);border-radius:7px;padding:6px 10px}
.trainer-ui button:disabled{opacity:.5;cursor:default}.trainer-ui button[aria-pressed=true],.trainer-ui .trainer-primary{background:#176b4e;color:white;border-color:#176b4e}
.trainer-ui input,.trainer-ui textarea,.trainer-ui select{border:1px solid #c9d7ce;background:var(--dsw-alias-button-elevated-fill,#fff);border-radius:6px;padding:7px;max-width:100%}
.trainer-nav{padding:12px;overflow:auto;height:100%;min-height:0}.trainer-ui h2{font-size:17px;margin:8px 0}.trainer-ui h3{font-size:13px;margin:15px 0 7px}.trainer-ui p{margin:7px 0}
.trainer-row{display:flex;gap:6px;align-items:center;flex-wrap:wrap}.trainer-stack{display:grid;gap:6px}.trainer-object{text-align:left;display:flex;justify-content:space-between;width:100%}
.trainer-meta{font-size:11px;opacity:.75;overflow-wrap:anywhere}.trainer-warning{padding:9px;background:#fff4d7;color:#684d15;border-radius:7px}.trainer-error{color:#a12626;white-space:pre-wrap;overflow-wrap:anywhere}
.trainer-details{height:100%;overflow:auto;padding:18px}.trainer-controls{position:sticky;bottom:0;padding:10px 0;background:var(--dsw-alias-button-elevated-fill,#fff);border-top:1px solid #d7e2db}
.trainer-ui pre{white-space:pre-wrap;overflow-wrap:anywhere;background:var(--dsw-alias-interactive-bg-hover,#f1f5f2);padding:10px;border-radius:6px;font-size:11px;max-height:300px;overflow:auto}
.trainer-step{border-left:3px solid #98bba8;padding:6px 10px;margin:8px 0}.trainer-modal-backdrop{position:fixed;inset:0;background:#15251f66;display:flex;align-items:center;justify-content:center;pointer-events:auto;z-index:2147483600}
.trainer-modal{background:var(--dsw-alias-button-elevated-fill,#fff);border:1px solid #bdd0c3;border-radius:12px;box-shadow:0 12px 50px #0003;width:min(980px,94vw);max-height:90vh;overflow:auto;padding:20px}
.trainer-modal textarea{width:100%;min-height:260px;font:12px/1.6 ui-monospace,monospace}.trainer-diff{display:grid;grid-template-columns:1fr 1fr;gap:12px}.trainer-diff>div{min-width:0}
.trainer-header{display:flex;align-items:center;gap:8px;max-width:600px}.trainer-header .trainer-meta{max-width:340px}.trainer-empty{padding:10px;border:1px dashed #a1bda9;border-radius:7px}
`;


export const TRAINER_SURFACE_STYLES = String.raw`
.trainer-surface,.trainer-surface *{box-sizing:border-box}.trainer-surface{position:fixed;inset:10px;z-index:2147483500;display:flex;flex-direction:column;overflow:hidden;background:#fff;color:#203040;border:1px solid #dfe6ee;border-radius:16px;box-shadow:0 18px 70px #10243a38;font:13px/1.5 system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI","Microsoft YaHei",sans-serif}.trainer-surface button,.trainer-surface textarea{font:inherit;color:inherit}.trainer-surface button{cursor:pointer;border:1px solid #dfe6ee;background:#fff;border-radius:8px;padding:7px 11px}.trainer-surface button:disabled{cursor:default;opacity:.5}.trainer-surface button[aria-pressed=true],.trainer-surface .trainer-surface-primary{background:#4169e1;border-color:#4169e1;color:#fff}.trainer-surface-top{height:62px;display:flex;align-items:center;gap:16px;padding:12px 18px;border-bottom:1px solid #e5eaf0;flex:0 0 auto}.trainer-surface-brand{display:flex;align-items:center;gap:8px;font-size:15px;white-space:nowrap}.trainer-surface-brand-mark{display:grid;place-items:center;width:32px;height:32px;border-radius:9px;background:#4169e1;color:#fff;font-weight:700;font-size:17px}.trainer-surface-project{color:#8492a6;border-left:1px solid #e1e6ed;padding-left:16px;font-size:13px}.trainer-surface-modes{display:flex;gap:3px;padding:3px;margin:auto;background:#f1f4f8;border-radius:10px}.trainer-surface-modes button{border:0;background:transparent;padding:7px 14px;border-radius:8px;color:#5c6878}.trainer-surface-modes button[aria-pressed=true]{background:#fff;color:#315cd5;box-shadow:0 1px 4px #243b5a25}.trainer-surface-demo{color:#6c7b8c;border:1px solid #dfe6ee;border-radius:8px;padding:6px 10px;white-space:nowrap}.trainer-surface-close{padding:6px 9px!important}.trainer-surface-shell{display:grid;grid-template-columns:188px minmax(0,1fr);min-height:0;flex:1}.trainer-surface-side{min-width:0;overflow:auto;background:#f7f9fb;border-right:1px solid #e5eaf0;padding:18px 10px;display:flex;flex-direction:column;gap:16px}.trainer-surface-side-group{display:grid;gap:2px}.trainer-surface-side-label{font-size:11px;letter-spacing:1px;color:#8794a5;padding:0 9px;margin-bottom:4px}.trainer-surface-nav{display:flex;align-items:center;gap:8px;width:100%;text-align:left;padding:8px 9px!important;border-color:transparent!important;background:transparent!important}.trainer-surface-nav:hover{background:#edf2f8!important}.trainer-surface-nav.selected{background:#e8efff!important;color:#315cd5}.trainer-surface-count{margin-left:auto;font-size:11px;color:#8794a5}.trainer-surface-side-foot{margin-top:auto;border-top:1px solid #e5eaf0;padding:13px 9px 0;color:#8794a5;font-size:11px}.trainer-surface-main{display:flex;flex-direction:column;min-width:0;min-height:0}.trainer-surface-heading{padding:20px 24px 14px;border-bottom:1px solid #e5eaf0;flex:0 0 auto}.trainer-surface-crumb{font-size:11px;color:#8492a6;margin-bottom:8px}.trainer-surface-heading-row{display:flex;align-items:flex-start;justify-content:space-between;gap:12px}.trainer-surface-heading h1{font-size:20px;margin:0;color:#1c2a3a}.trainer-surface-subline{font-size:12px;color:#8492a6;margin-top:6px}.trainer-surface-actions{display:flex;gap:7px}.trainer-surface-tabs{display:flex;gap:22px;padding:0 24px;border-bottom:1px solid #e5eaf0;flex:0 0 auto}.trainer-surface-tabs button{border:0;border-bottom:2px solid transparent;border-radius:0;background:transparent;padding:11px 0;color:#8492a6}.trainer-surface-tabs button[aria-pressed=true]{border-bottom-color:#4169e1;color:#1c2a3a}.trainer-surface-workarea{display:grid;grid-template-columns:minmax(0,1fr) 242px;min-height:0;flex:1}.trainer-surface-session{display:flex;flex-direction:column;min-width:0;min-height:0;padding:18px 24px;overflow:auto}.trainer-surface-sessionbar{display:flex;align-items:center;gap:7px;color:#8492a6;font-size:11px;margin-bottom:20px}.trainer-surface-led{width:6px;height:6px;background:#1f9d68;border-radius:50%}.trainer-surface-user{align-self:flex-end;max-width:92%;background:#f1f4f8;border-radius:13px 13px 3px 13px;padding:10px 13px;margin-bottom:18px}.trainer-surface-message{display:flex;gap:10px;align-items:flex-start}.trainer-surface-avatar{width:28px;height:28px;display:grid;place-items:center;border-radius:9px;background:#e8efff;color:#4169e1;flex:0 0 auto}.trainer-surface-message-body{min-width:0}.trainer-surface-message-name{font-weight:600;margin:2px 0 8px}.trainer-surface-evidence{border:1px solid #e2e8ef;border-radius:11px;padding:12px;margin-top:12px}.trainer-surface-step{display:flex;align-items:center;gap:8px;padding:7px 0;border-bottom:1px solid #edf1f5}.trainer-surface-step:last-child{border-bottom:0}.trainer-surface-step-mark{display:grid;place-items:center;width:19px;height:19px;border-radius:50%;background:#f1f4f8;color:#6f7d8e;font-size:11px;flex:0 0 auto}.trainer-surface-step-label{min-width:0;overflow-wrap:anywhere}.trainer-surface-step-state{margin-left:auto;color:#8492a6;font-size:11px;white-space:nowrap}.trainer-surface-spacer{flex:1;min-height:18px}.trainer-surface-chips{display:flex;gap:6px;flex-wrap:wrap;margin:10px 0}.trainer-surface-chip{font-size:11px!important;color:#6f7d8e!important;padding:5px 8px!important}.trainer-surface-composer{border:1px solid #dfe6ee;border-radius:11px;padding:10px 12px;background:#f7f9fb}.trainer-surface-composer textarea{display:block;width:100%;min-height:60px;resize:vertical;border:0;outline:0;background:transparent}.trainer-surface-composer-bottom{display:flex;align-items:center;justify-content:space-between;gap:8px;color:#8492a6;font-size:11px;margin-top:5px}.trainer-surface-inspector{min-width:0;min-height:0;overflow:auto;align-self:stretch;display:flex;flex-direction:column;justify-content:flex-start;align-content:flex-start;background:#f7f9fb;border-left:1px solid #e5eaf0;padding:12px 14px}.trainer-surface-inspector>*{min-width:0;width:100%;flex:0 0 auto}.trainer-surface-inspector>[data-testid="trainer-run-details"]{display:flex;flex-direction:column;justify-content:flex-start;align-items:stretch;min-width:0;width:100%;min-height:0;flex:1 1 auto;margin:0;overflow:auto;overflow-wrap:anywhere}.trainer-surface-inspector .trainer-details{height:auto;padding:0;overflow:visible}.trainer-surface-inspector h2{font-size:14px;margin:0}.trainer-surface-inspector .trainer-controls{position:static;flex:0 0 auto;background:transparent;border-top:1px solid #e5eaf0;margin-top:14px}.trainer-surface-inspector .trainer-step{min-width:0;white-space:normal;overflow-wrap:anywhere;line-height:1.4;border:1px solid #dfe6ee;border-left-width:1px;border-radius:9px;margin:7px 0;background:#fff}.trainer-surface-inspector .trainer-error{max-width:100%;overflow:auto;word-break:break-word}.trainer-surface-inspector pre{max-height:180px}.trainer-surface-plain{padding:24px;color:#8492a6}.trainer-surface-status{font-size:11px;color:#8492a6;margin-top:8px}.trainer-surface-native-prompt{display:flex;gap:12px;align-items:flex-start;border:1px solid #e2e8ef;border-radius:11px;padding:16px;background:#fbfcfe}.trainer-surface-native-prompt p{margin:7px 0;color:#6f7d8e}.trainer-surface-native-icon{width:30px;height:30px;display:grid;place-items:center;border-radius:9px;background:#e8efff;color:#4169e1;flex:0 0 auto}.trainer-surface-run-list{display:grid;gap:7px}.trainer-surface-run-row{display:flex;justify-content:space-between;gap:12px;text-align:left;width:100%;background:#fff}.trainer-surface-composer label{display:block;margin-bottom:5px}.trainer-surface-composer textarea{border:1px solid #dfe6ee!important;background:#fff!important;border-radius:7px!important;min-height:72px;padding:8px!important}@media(max-width:900px){.trainer-surface{inset:6px}.trainer-surface-project{display:none}.trainer-surface-top{padding:10px 12px}.trainer-surface-shell{grid-template-columns:162px minmax(0,1fr)}.trainer-surface-workarea{grid-template-columns:minmax(0,1fr) 215px}.trainer-surface-heading,.trainer-surface-session{padding-left:15px;padding-right:15px}.trainer-surface-tabs{padding:0 15px}}@media(max-width:720px){.trainer-surface-workarea{grid-template-columns:1fr}.trainer-surface-inspector{border-left:0;border-top:1px solid #e5eaf0}.trainer-surface-top{flex-wrap:wrap;height:auto}.trainer-surface-modes{order:3;width:100%;justify-content:center}.trainer-surface-demo{display:none}}@media(max-width:480px){.trainer-surface{inset:0;border-radius:0}.trainer-surface-shell{display:block}.trainer-surface-side{border-right:0;border-bottom:1px solid #e5eaf0;max-height:210px}.trainer-surface-side-foot{display:none}.trainer-surface-heading h1{font-size:18px}}
`;

// V2 keeps the current full-screen workbench geometry and changes only visual
// tokens and status treatment.  The base rules above remain the V1 fallback;
// switching the root data-theme attribute back to "v1" restores them exactly.
export const TRAINER_SURFACE_THEME_KEY = 'trainer-workbench-ui-version-v1-v2';
export const TRAINER_SURFACE_V2_OVERRIDES = String.raw`
.trainer-surface[data-theme="v2"]{--trainer-v2-ink:#17243a;--trainer-v2-muted:#52647a;--trainer-v2-border:#d7e0ec;--trainer-v2-panel:#f5f8fc;--trainer-v2-blue:#2f5fe5;--trainer-v2-blue-soft:#e8efff;--trainer-v2-complete:#177245;--trainer-v2-complete-soft:#e7f6ee;--trainer-v2-running:#b45309;--trainer-v2-running-soft:#fff4e0;--trainer-v2-error:#b42318;--trainer-v2-error-soft:#fdecec;--trainer-v2-idle:#52647a;--trainer-v2-idle-soft:#edf2f7;color:var(--trainer-v2-ink);font-size:14px;line-height:1.58;-webkit-font-smoothing:antialiased;text-rendering:optimizeLegibility;background:#fff;border-color:var(--trainer-v2-border);box-shadow:0 18px 70px #10243a2b}
.trainer-surface[data-theme="v2"] button{border-color:var(--trainer-v2-border);transition:background-color .15s ease,border-color .15s ease,color .15s ease,box-shadow .15s ease}
.trainer-surface[data-theme="v2"] button:hover:not(:disabled){border-color:#9db3dd;box-shadow:0 2px 8px #1f3b7014}
.trainer-surface[data-theme="v2"] button:focus-visible{outline:3px solid #9db9ff;outline-offset:1px}
.trainer-surface[data-theme="v2"] .trainer-surface-top{border-bottom-color:var(--trainer-v2-border);background:#fff}
.trainer-surface[data-theme="v2"] .trainer-surface-brand{font-size:16px;color:var(--trainer-v2-ink)}
.trainer-surface[data-theme="v2"] .trainer-surface-brand-mark{background:var(--trainer-v2-blue);box-shadow:0 3px 8px #2f5fe53d}
.trainer-surface[data-theme="v2"] .trainer-surface-project,.trainer-surface[data-theme="v2"] .trainer-surface-crumb,.trainer-surface[data-theme="v2"] .trainer-surface-subline,.trainer-surface[data-theme="v2"] .trainer-surface-status,.trainer-surface[data-theme="v2"] .trainer-surface-step-state{color:var(--trainer-v2-muted)}
.trainer-surface[data-theme="v2"] .trainer-surface-demo{color:#3155a7;border-color:#b8c8eb;background:#f4f7ff;font-weight:600}
.trainer-surface[data-theme="v2"] .trainer-surface-theme-toggle{border-color:#b8c8eb;background:#f7f9ff;color:#3155a7;font-weight:600}
.trainer-surface[data-theme="v2"] .trainer-surface-modes{background:#edf2f8}
.trainer-surface[data-theme="v2"] .trainer-surface-modes button[aria-pressed=true]{color:var(--trainer-v2-blue)}
.trainer-surface[data-theme="v2"] .trainer-surface-shell{background:#fff}
.trainer-surface[data-theme="v2"] .trainer-surface-side,.trainer-surface[data-theme="v2"] .trainer-surface-inspector{background:var(--trainer-v2-panel)}
.trainer-surface[data-theme="v2"] .trainer-surface-side{border-right-color:var(--trainer-v2-border)}
.trainer-surface[data-theme="v2"] .trainer-surface-inspector{border-left-color:var(--trainer-v2-border)}
.trainer-surface[data-theme="v2"] .trainer-surface-side-label{color:#60738c;font-weight:700}
.trainer-surface[data-theme="v2"] .trainer-surface-side-foot{border-top-color:var(--trainer-v2-border);color:#60738c}
.trainer-surface[data-theme="v2"] .trainer-surface-nav{color:#243650}
.trainer-surface[data-theme="v2"] .trainer-surface-nav:hover{background:#eaf0fa!important}
.trainer-surface[data-theme="v2"] .trainer-surface-nav.selected{background:var(--trainer-v2-blue-soft)!important;color:#234dbd;font-weight:600}
.trainer-surface[data-theme="v2"] .trainer-surface-count{color:#60738c}
.trainer-surface[data-theme="v2"] .trainer-surface-heading,.trainer-surface[data-theme="v2"] .trainer-surface-tabs{border-bottom-color:var(--trainer-v2-border)}
.trainer-surface[data-theme="v2"] .trainer-surface-heading{padding-top:22px;padding-bottom:16px}
.trainer-surface[data-theme="v2"] .trainer-surface-heading h1{font-size:22px;color:var(--trainer-v2-ink);letter-spacing:-.01em}
.trainer-surface[data-theme="v2"] .trainer-surface-tabs{gap:25px}
.trainer-surface[data-theme="v2"] .trainer-surface-tabs button{font-size:14px;padding-top:12px;padding-bottom:12px}
.trainer-surface[data-theme="v2"] .trainer-surface-tabs button[aria-pressed=true]{background:transparent;border-bottom-color:var(--trainer-v2-blue);color:var(--trainer-v2-ink);font-weight:600}
.trainer-surface[data-theme="v2"] .trainer-surface-session{padding-top:20px}
.trainer-surface[data-theme="v2"] .trainer-surface-sessionbar{color:var(--trainer-v2-muted)}
.trainer-surface[data-theme="v2"] .trainer-surface-led{width:8px;height:8px;background:#9aaabd}
.trainer-surface[data-theme="v2"] .trainer-surface-led.trainer-status-complete{background:var(--trainer-v2-complete)}
.trainer-surface[data-theme="v2"] .trainer-surface-led.trainer-status-running{background:var(--trainer-v2-running)}
.trainer-surface[data-theme="v2"] .trainer-surface-led.trainer-status-error{background:var(--trainer-v2-error)}
.trainer-surface[data-theme="v2"] .trainer-surface-led.trainer-status-idle{background:#9aaabd}
.trainer-surface[data-theme="v2"] .trainer-surface-primary{background:var(--trainer-v2-blue);border-color:var(--trainer-v2-blue);color:#fff}
.trainer-surface[data-theme="v2"] .trainer-surface-primary:hover:not(:disabled){background:#244fc9;border-color:#244fc9}
.trainer-surface[data-theme="v2"] .trainer-surface-native-prompt{border-color:#cbd8ec;background:#f7faff;box-shadow:0 2px 9px #203b6b0d}
.trainer-surface[data-theme="v2"] .trainer-surface-native-prompt p{color:#52647a}
.trainer-surface[data-theme="v2"] .trainer-surface-native-icon{background:var(--trainer-v2-blue-soft);color:var(--trainer-v2-blue)}
.trainer-surface[data-theme="v2"] .trainer-surface-composer{border-color:#cbd8ec;background:#f5f8fc}
.trainer-surface[data-theme="v2"] .trainer-surface-composer textarea{border-color:#cbd8ec!important}
.trainer-surface[data-theme="v2"] .trainer-surface-chip{color:#465a74!important;background:#fff}
.trainer-surface[data-theme="v2"] .trainer-surface-inspector .trainer-controls{border-top-color:var(--trainer-v2-border)}
.trainer-surface[data-theme="v2"] .trainer-surface-inspector .trainer-step{border-color:#cbd8ec;background:#fff;box-shadow:0 2px 8px #203b6b0d}.trainer-surface[data-theme="v2"] .trainer-surface-inspector .trainer-step[aria-pressed=true]{background:#fff;color:var(--trainer-v2-ink);border-color:#8daafb}
.trainer-surface[data-theme="v2"] .trainer-surface-status{font-size:12px}
.trainer-surface[data-theme="v2"] .trainer-surface-plain{color:var(--trainer-v2-muted)}
.trainer-surface[data-theme="v2"] .trainer-surface-run-row{background:#fff}
.trainer-surface[data-theme="v2"] .trainer-status-badge{display:inline-flex;align-items:center;gap:6px;width:max-content;padding:3px 8px;border-radius:999px;font-size:12px;font-weight:700;line-height:1.35}
.trainer-surface[data-theme="v2"] .trainer-status-badge::before{content:"";width:7px;height:7px;border-radius:50%;background:currentColor}
.trainer-surface[data-theme="v2"] .trainer-status-complete{color:var(--trainer-v2-complete);background:var(--trainer-v2-complete-soft)}
.trainer-surface[data-theme="v2"] .trainer-status-running{color:var(--trainer-v2-running);background:var(--trainer-v2-running-soft)}
.trainer-surface[data-theme="v2"] .trainer-status-error{color:var(--trainer-v2-error);background:var(--trainer-v2-error-soft)}
.trainer-surface[data-theme="v2"] .trainer-status-idle{color:var(--trainer-v2-idle);background:var(--trainer-v2-idle-soft)}
.trainer-surface[data-theme="v2"] .trainer-step.trainer-status-complete{border-left:4px solid var(--trainer-v2-complete)}
.trainer-surface[data-theme="v2"] .trainer-step.trainer-status-running{border-left:4px solid var(--trainer-v2-running)}
.trainer-surface[data-theme="v2"] .trainer-step.trainer-status-error{border-left:4px solid var(--trainer-v2-error)}
.trainer-surface[data-theme="v2"] .trainer-step.trainer-status-idle{border-left:4px solid #9aaabd}
.trainer-surface[data-theme="v2"] .trainer-error{color:var(--trainer-v2-error);background:var(--trainer-v2-error-soft);border-radius:7px;padding:8px}
.trainer-surface[data-theme="v2"] .trainer-warning{color:#854d0e;background:var(--trainer-v2-running-soft)}
`;
export const TRAINER_SURFACE_STYLES_V1 = TRAINER_SURFACE_STYLES;
export const TRAINER_SURFACE_STYLES_V2 = TRAINER_SURFACE_STYLES + TRAINER_SURFACE_V2_OVERRIDES;

export function trainerSurfaceTheme() {
  try { return globalThis.localStorage?.getItem(TRAINER_SURFACE_THEME_KEY) === 'v1' ? 'v1' : 'v2'; }
  catch { return 'v2'; }
}

export function trainerStatusTone(status) {
  if (status === 'completed') return 'complete';
  if (['queued', 'preparing', 'running', 'pausing', 'stopping'].includes(status)) return 'running';
  if (['failed', 'cancelled', 'interrupted'].includes(status)) return 'error';
  return 'idle';
}

export function trainerStatusClass(status) { return `trainer-status-badge trainer-status-${trainerStatusTone(status)}`; }

export function trainerJson(value) { return JSON.stringify(value ?? null, null, 2); }

export const TRAINER_TARGET_STORAGE_KEY = 'trainer-workbench-target-v1';
export function trainerRememberTarget(target) {
  if (!target?.projectId || !target?.targetKind || !target?.targetId) return;
  try { globalThis.localStorage?.setItem(TRAINER_TARGET_STORAGE_KEY, JSON.stringify(target)); } catch { /* optional preference */ }
}
export function trainerRememberedTarget(projectId, project) {
  try {
    const value = JSON.parse(globalThis.localStorage?.getItem(TRAINER_TARGET_STORAGE_KEY) ?? 'null');
    if (!value || value.projectId !== projectId) return null;
    const exists = value.targetKind === 'workflow'
      ? (project?.workflows ?? []).some(item => item.workflowId === value.targetId)
      : (project?.agents ?? []).some(item => item.agentId === value.targetId);
    return exists ? { projectId, targetKind: value.targetKind, targetId: value.targetId } : null;
  } catch { return null; }
}
export function trainerPreferredTarget(projectId, project, runs = []) {
  const remembered = trainerRememberedTarget(projectId, project);
  if (remembered) return remembered;
  const valid = run => run?.projectId === projectId && ['workflow', 'agent'].includes(run.targetKind) && run.targetId && run.status === 'completed';
  const recent = [...runs].filter(valid).sort((a, b) => Date.parse(b.updatedAt ?? b.completedAt ?? b.startedAt ?? 0) - Date.parse(a.updatedAt ?? a.completedAt ?? a.startedAt ?? 0))[0];
  if (recent) {
    const target = { projectId, targetKind: recent.targetKind, targetId: recent.targetId };
    const exists = target.targetKind === 'workflow'
      ? (project?.workflows ?? []).some(item => item.workflowId === target.targetId)
      : (project?.agents ?? []).some(item => item.agentId === target.targetId);
    if (exists) return target;
  }
  const first = project?.workflows?.[0] ?? project?.agents?.[0];
  return first ? { projectId, targetKind: first.workflowId ? 'workflow' : 'agent', targetId: first.workflowId ?? first.agentId } : null;
}
export function trainerWorkflowDefaultInputText(target, assets) {
  if (target?.targetKind !== 'workflow') return '{}';
  try {
    const fixture = JSON.parse(assets?.files?.[`tests/${target.targetId}.json`] ?? 'null');
    const input = fixture?.cases?.[0]?.input;
    return input && typeof input === 'object' ? trainerJson(input) : '{}';
  } catch { return '{}'; }
}
export function trainerRunLabel(status) {
  return ({ queued: '已排队', preparing: '准备执行包', running: '运行中', pausing: '等待当前步骤结束后暂停',
    paused: '已暂停', stopping: '正在请求停止', completed: '框架验证通过', failed: '失败', cancelled: '已取消', interrupted: '重启中断' })[status] ?? status ?? '尚未运行';
}

export function trainerRunDuration(run, now = Date.now()) {
  if (!run?.startedAt) return '—';
  const stamp = value => typeof value === 'number' ? value : Date.parse(value);
  const elapsed = Math.max(0, (run.completedAt ? stamp(run.completedAt) : now) - stamp(run.startedAt));
  return Number.isFinite(elapsed) ? `${Math.floor(elapsed / 1000)} 秒` : '—';
}

export function useTrainerDialogFocus(close) {
  useEffect(() => {
    const previous = document.activeElement;
    const dialog = document.querySelector('.trainer-modal');
    const controls = () => [...(dialog?.querySelectorAll('button:not(:disabled),input:not(:disabled),select:not(:disabled),textarea:not(:disabled),summary') ?? [])];
    controls()[0]?.focus();
    const keydown = event => {
      if (event.key === 'Escape') { event.preventDefault(); close(); }
      if (event.key !== 'Tab') return;
      const elements = controls(); const first = elements[0]; const last = elements.at(-1);
      if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last?.focus(); }
      else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first?.focus(); }
    };
    dialog?.addEventListener('keydown', keydown);
    return () => { dialog?.removeEventListener('keydown', keydown); if (previous?.isConnected) previous.focus?.(); };
  }, []);
}

export function TrainerRunDetails({ store, compact = false, onDiagnose }) {
  const state = useSyncExternalStore(store.subscribe, store.getSnapshot, store.getSnapshot);
  const run = state.run;
  const [stepId, setStepId] = useState(null);
  const step = run?.steps?.find(item => item.stepId === stepId) ?? run?.steps?.[0];
  const completed = run?.steps?.filter(item => item.status === 'completed').length ?? 0;
  const control = action => { void store.perform('control', { runId: run.runId, action }).catch(() => {}); };
  return createElement('section', { className: 'trainer-ui', 'data-testid': 'trainer-run-details' },
    createElement('h2', null, '运行观察'),
    createElement('strong', { className: trainerStatusClass(run?.status) }, trainerRunLabel(run?.status)),
    createElement('p', null, run ? `完成 ${completed}/${run.steps?.length ?? 0} · ${trainerRunDuration(run)}` : '选择历史运行，或发起合成训练。'),
    run && createElement('p', { className: 'trainer-meta' }, `本次匹配的测试断言 ${run.testResults?.length ?? 0} 项`),
    createElement('div', { className: 'trainer-meta' }, run?.runId, run ? ` · ${run.purpose} · ${run.revisionId}` : ''),
    run?.revisionId && state.project?.revisionId !== run.revisionId && createElement('p', { className: 'trainer-warning' }, `历史运行使用 ${run.revisionId}；当前候选 ${state.project?.revisionId ?? '读取中'}。`),
    run?.cancellationRequested && createElement('p', { className: 'trainer-warning' }, run.childTerminationConfirmed === true ? '子任务终止已确认' : '已请求取消；子任务终止尚未确认'),
    run?.error && createElement('pre', { className: 'trainer-error' }, trainerJson(run.error)),
    state.events.length > 0 && createElement('p', { className: 'trainer-meta' }, '最近可见动作：', trainerJson(state.events[state.events.length - 1])),
    !compact && run && createElement('div', null,
      createElement('h3', null, '步骤顺序'),
      (run.steps ?? []).map(item => createElement('button', { className: `trainer-object trainer-step trainer-status-${trainerStatusTone(item.status)}`, key: item.stepId, onClick: () => setStepId(item.stepId), 'aria-pressed': step?.stepId === item.stepId }, `${item.stepId} · ${item.agentId} · ${trainerRunLabel(item.status)}`)),
      createElement('div', { className: 'trainer-meta' }, `包 SHA-256：${run.bundleSha256 ?? '未提供'}`),
      createElement('div', { className: 'trainer-meta' }, `开始：${run.startedAt ?? '—'} · 更新：${run.updatedAt ?? '—'}`),
      step && createElement('div', null,
        createElement('h3', null, '实际输入'), createElement('pre', null, trainerJson(step.input)),
        createElement('h3', null, '实际输出'), createElement('pre', null, trainerJson(step.output)),
        createElement('h3', null, '子任务与装载证据'), createElement('pre', null, trainerJson({ parentSessionId: step.parentSessionId, childSessionId: step.childSessionId, actualLoadedRefs: step.actualLoadedRefs, error: step.error })))),
    createElement('div', { className: 'trainer-controls' },
      createElement('div', { className: 'trainer-row' }, ['pause', 'resume', 'stop'].map(action => {
        const permission = trainerControlState(run, action);
        const title = !permission.allowed ? permission.reason : state.busy ? '上一操作尚未完成' : { pause: '当前步骤结束后暂停后续派发', resume: '继续已暂停的运行', stop: '请求取消当前子任务并停止后续派发' }[action];
        return createElement('button', { key: action, disabled: state.busy || !permission.allowed, title, onClick: () => control(action) }, { pause: '暂停', resume: '继续', stop: '停止' }[action]);
      })),
      createElement('div', { className: 'trainer-meta' }, ['pause', 'resume', 'stop'].map(action => {
        const permission = trainerControlState(run, action);
        return permission.allowed ? '' : `${{ pause: '暂停', resume: '继续', stop: '停止' }[action]}：${permission.reason}`;
      }).filter(Boolean).join('；'))),
    run && createElement('button', { disabled: state.busy, onClick: () => onDiagnose?.(run) }, '让 Trainer 诊断此运行'),
    createElement('p', { className: 'trainer-meta' }, '仅验证合成训练框架 · 业务门禁未通过'));
}

export function TrainerAssetEditor({ store, close }) {
  useTrainerDialogFocus(close);
  const state = useSyncExternalStore(store.subscribe, store.getSnapshot, store.getSnapshot);
  const [base, setBase] = useState(null);
  const [path, setPath] = useState('');
  const [drafts, setDrafts] = useState({});
  const [diff, setDiff] = useState(null);
  const [error, setError] = useState('');
  useEffect(() => {
    let alive = true;
    void store.perform('assets', {}, { mutation: false }).then(value => {
      if (alive) { setBase(value); setPath(Object.keys(value.files ?? {})[0] ?? ''); setDrafts({ ...value.files }); }
    }).catch(e => { if (alive) setError(e.message); });
    return () => { alive = false; };
  }, [store]);
  const changes = base ? Object.keys(drafts).filter(name => drafts[name] !== base.files[name]).map(name => ({ path: name, content: drafts[name] })) : [];
  const save = async freeze => {
    setError('');
    try {
      let revisionId = base.revisionId;
      if (freeze) {
        const result = await store.perform('freeze', { revisionId, baseRevision: revisionId, changes, reason: '工作台保存并冻结当前编辑', linkedRunId: state.selectedRunId });
        setBase({ ...base, revisionId: result.revisionId, files: { ...drafts } });
        setDiff(result);
      } else if (changes.length) {
        const result = await store.perform('apply-changes', { baseRevision: revisionId, changes, reason: '工作台保存候选', linkedRunId: state.selectedRunId });
        revisionId = result.revisionId;
        setBase({ ...base, revisionId, files: { ...drafts } }); setDiff(result.diff);
      }
    } catch (e) { setError(e.message); }
  };
  return createElement('div', { className: 'trainer-modal-backdrop' }, createElement('section', { className: 'trainer-ui trainer-modal', role: 'dialog', 'aria-modal': true, 'aria-label': '候选资产与差异' },
    createElement('div', { className: 'trainer-row' }, createElement('h2', null, '候选资产与差异'), createElement('button', { onClick: close }, '关闭')),
    createElement('p', { className: 'trainer-meta' }, `编辑基线 ${base?.revisionId ?? '读取中'} · ${changes.length} 个未保存文件`),
    createElement('select', { value: path, 'aria-label': '资产文件', onChange: e => setPath(e.target.value) }, Object.keys(drafts).map(name => createElement('option', { key: name, value: name }, name))),
    createElement('textarea', { 'aria-label': '资产内容', value: drafts[path] ?? '', disabled: !base || state.mode !== 'training', onChange: e => setDrafts({ ...drafts, [path]: e.target.value }) }),
    createElement('details', null, createElement('summary', null, '查看当前文件修改'), createElement('div', { className: 'trainer-diff' },
      createElement('div', null, '保存前', createElement('pre', null, base?.files[path] ?? '')), createElement('div', null, '保存后', createElement('pre', null, drafts[path] ?? '')))),
    diff && createElement('details', null, createElement('summary', null, '已保存变更记录'), createElement('pre', null, trainerJson(diff))),
    createElement('div', { className: 'trainer-row' },
      createElement('button', { disabled: !base || state.busy || state.mode !== 'training' || !changes.length, onClick: () => void save(false) }, '保存'),
      createElement('button', { disabled: !base || state.busy || state.mode !== 'training', onClick: () => void save(true) }, '保存并冻结')),
    (error || state.error) && createElement('p', { className: 'trainer-error', role: 'alert' }, error || state.error)));
}

export function TrainerProjectDialog({ store, kind, close }) {
  useTrainerDialogFocus(close);
  const state = useSyncExternalStore(store.subscribe, store.getSnapshot, store.getSnapshot);
  const [error, setError] = useState('');
  const [agentId, setAgentId] = useState('');
  const [name, setName] = useState('');
  const [workflowId, setWorkflowId] = useState('');
  const [workflowName, setWorkflowName] = useState('');
  const [base, setBase] = useState(null);
  const [workflow, setWorkflow] = useState(null);
  const [selectedAgent, setSelectedAgent] = useState(state.project?.agents?.[0]?.agentId ?? '');
  const [firstWorkflowAgent, setFirstWorkflowAgent] = useState(state.project?.agents?.[0]?.agentId ?? '');
  const [secondWorkflowAgent, setSecondWorkflowAgent] = useState(state.project?.agents?.[1]?.agentId ?? '');
  const [frozenVersionId, setFrozenVersionId] = useState(state.frozenVersion?.frozenVersionId ?? '');
  const [evidenceRunId, setEvidenceRunId] = useState(state.selectedRunId ?? '');
  const [releaseId, setReleaseId] = useState('');
  const [beforeRunId, setBeforeRunId] = useState('');
  const [afterRunId, setAfterRunId] = useState(state.selectedRunId ?? '');
  const [result, setResult] = useState(null);
  useEffect(() => {
    let alive = true;
    if (kind === 'agent' || kind === 'workflow' || kind === 'workflow-create') {
      void store.perform('assets', {}, { mutation: false }).then(value => {
        if (!alive) return;
        setBase(value);
        if (kind === 'workflow') {
          const file = value.files[`workflows/${state.target.targetId}.json`];
          if (!file) throw new Error('所选工作流文件不存在');
          setWorkflow(JSON.parse(file));
        }
      }).catch(e => { if (alive) setError(e.message); });
    }
    if (kind === 'versions') void store.perform('releases', {}, { mutation: false }).catch(e => { if (alive) setError(e.message); });
    return () => { alive = false; };
  }, [kind, store]);
  const action = async task => {
    try { setError(''); const value = await task(); setResult(value); return value; }
    catch (e) { setError(e.message); return null; }
  };
  const save = () => action(async () => {
    const changes = kind === 'agent' ? trainerNewAgentChanges({ agentId, name })
      : kind === 'workflow-create' ? trainerNewWorkflowChanges({ workflowId, name: workflowName, firstAgentId: firstWorkflowAgent, secondAgentId: secondWorkflowAgent })
      : [{ path: `workflows/${workflow.workflowId}.json`, content: `${JSON.stringify(workflow, null, 2)}\n` }];
    if (['agent', 'workflow-create'].includes(kind) && changes.some(change => Object.hasOwn(base.files, change.path))) throw new Error(`${kind === 'agent' ? 'Agent ID 或其合同文件' : '工作流 ID'} 已存在，请使用新 ID`);
    const reason = kind === 'agent' ? '创建合成 Agent 模板' : kind === 'workflow-create' ? '创建合成工作流模板' : '编辑工作流步骤';
    const saved = await store.perform('apply-changes', { baseRevision: base.revisionId, changes, reason, linkedRunId: state.selectedRunId });
    setBase({ ...base, revisionId: saved.revisionId, files: { ...base.files, ...Object.fromEntries(changes.map(item => [item.path, item.content])) } });
    return saved;
  });
  const runOptions = state.runs.filter(run => run.projectId === state.projectId).map(run => createElement('option', { key: run.runId, value: run.runId }, `${run.runId} · ${run.status} · ${run.revisionId}`));
  const frozenVersions = trainerFrozenVersionsFor(state.frozenVersions ?? [], state.target);
  const selectedFrozen = frozenVersions.find(version => version.frozenVersionId === frozenVersionId);
  const knownRuns = [...new Map([...state.runs, ...(state.run ? [state.run] : [])].map(run => [run.runId, run])).values()];
  const matchingRuns = trainerMatchingEvidence(knownRuns, selectedFrozen);
  const evidence = matchingRuns.find(run => run.runId === evidenceRunId);
  const agents = state.project?.agents ?? [];
  return createElement('div', { className: 'trainer-modal-backdrop' }, createElement('section', { className: 'trainer-ui trainer-modal', role: 'dialog', 'aria-modal': true, 'aria-label': { agent: '新建 Agent', 'workflow-create': '新建工作流', workflow: '工作流顺序', versions: '冻结与发布', compare: '运行比较' }[kind] },
    createElement('div', { className: 'trainer-row' }, createElement('h2', null, { agent: '新建 Agent', 'workflow-create': '新建工作流', workflow: '工作流顺序', versions: '冻结与发布', compare: '运行比较' }[kind]), createElement('button', { onClick: close }, '关闭')),
    kind === 'agent' && createElement('div', { className: 'trainer-stack' },
      createElement('label', null, 'Agent ID ', createElement('input', { value: agentId, onChange: e => setAgentId(e.target.value), placeholder: 'lab-new-agent' })),
      createElement('label', null, '名称 ', createElement('input', { value: name, onChange: e => setName(e.target.value) })),
      createElement('p', null, '创建合成指令与宽松 JSON 对象合同；注册后可独立训练或加入工作流。')),
    kind === 'workflow-create' && createElement('div', { className: 'trainer-stack' },
      createElement('p', { className: 'trainer-warning' }, '新工作流先创建两个不同 Agent 的步骤；保存后可在“工作流配置”中继续添加、删除、排序和修改输入映射。'),
      createElement('label', null, '工作流 ID ', createElement('input', { value: workflowId, onChange: e => setWorkflowId(e.target.value), placeholder: 'dft-review-flow' })),
      createElement('label', null, '工作流名称 ', createElement('input', { value: workflowName, onChange: e => setWorkflowName(e.target.value), placeholder: 'DFT 分析 → 复核' })),
      createElement('label', null, '第 1 步 Agent ', createElement('select', { value: firstWorkflowAgent, onChange: e => setFirstWorkflowAgent(e.target.value), 'aria-label': '第 1 步 Agent' }, agents.map(agent => createElement('option', { key: agent.agentId, value: agent.agentId }, agent.name)))),
      createElement('label', null, '第 2 步 Agent ', createElement('select', { value: secondWorkflowAgent, onChange: e => setSecondWorkflowAgent(e.target.value), 'aria-label': '第 2 步 Agent' }, agents.map(agent => createElement('option', { key: agent.agentId, value: agent.agentId }, agent.name)))),
      createElement('p', { className: 'trainer-meta' }, '默认交接：第 1 步接收整个运行输入，第 2 步接收第 1 步的完整 JSON 输出；保存后可在步骤编辑器中改成 DFT 的实际字段。')),
    kind === 'workflow' && workflow && createElement('div', { className: 'trainer-stack' },
      createElement('p', { className: 'trainer-warning' }, '每一步都可以更换 Agent；步骤 ID 与输入映射会保留，但更换 Agent 后请检查输入输出合同和前序步骤引用。保存与运行均由服务端校验。'),
      workflow.steps.map((step, index) => createElement('div', { key: step.stepId, className: 'trainer-step' },
        createElement('div', { className: 'trainer-row' }, createElement('strong', null, `${index + 1}. ${step.agentId} · ${step.stepId}`),
          createElement('button', { disabled: index === 0, onClick: () => setWorkflow(trainerMoveStep(workflow, index, -1)), 'aria-label': `上移 ${step.stepId}` }, '↑'),
          createElement('button', { disabled: index === workflow.steps.length - 1, onClick: () => setWorkflow(trainerMoveStep(workflow, index, 1)), 'aria-label': `下移 ${step.stepId}` }, '↓'),
          createElement('button', { disabled: workflow.steps.length === 1, onClick: () => setWorkflow({ ...workflow, steps: workflow.steps.filter(item => item.stepId !== step.stepId) }) }, '移除')),
        createElement('label', null, 'Agent ', createElement('select', {
          'aria-label': `${step.stepId} Agent`, value: step.agentId,
          onChange: e => {
            const agentId = e.target.value;
            setError('');
            setWorkflow({ ...workflow, steps: workflow.steps.map(item => {
              if (item.stepId !== step.stepId) return item;
              const next = { ...item, agentId };
              // A frozen version belongs to the previous Agent and must not
              // silently travel with a replacement Agent.
              delete next.agentVersion;
              return next;
            }) });
          }
        }, agents.map(agent => createElement('option', { key: agent.agentId, value: agent.agentId }, `${agent.name} · ${agent.agentId}`)))),
        createElement('label', null, '版本来源 ', createElement('select', {
          'aria-label': `${step.stepId} 版本来源`, value: step.agentVersion?.kind === 'frozen' ? step.agentVersion.frozenVersionId : '',
          onChange: e => { try { setWorkflow(trainerStepVersion(workflow, step.stepId, e.target.value, state.frozenVersions ?? [], state.projectId)); setError(''); } catch (error) { setError(error.message); } }
        }, createElement('option', { value: '' }, '当前候选（运行开始时固定）'),
        step.agentVersion?.kind === 'frozen' && !trainerFrozenVersionsFor(state.frozenVersions ?? [], { projectId: state.projectId, targetKind: 'agent', targetId: step.agentId }).some(version => version.frozenVersionId === step.agentVersion.frozenVersionId)
          && createElement('option', { value: step.agentVersion.frozenVersionId, disabled: true }, `未找到冻结版本：${step.agentVersion.frozenVersionId}（保留原引用）`),
        ...trainerFrozenVersionsFor(state.frozenVersions ?? [], { projectId: state.projectId, targetKind: 'agent', targetId: step.agentId }).map(version => createElement('option', { key: version.frozenVersionId, value: version.frozenVersionId }, trainerFrozenVersionLabel(version))))),
        !Object.keys(step.inputBindings ?? {}).length && createElement('p', { className: 'trainer-warning', role: 'status' }, '此步骤尚未配置输入映射：运行时会收到整份运行输入，不会自动接收前一步输出。若需接收其他步骤的结果，请配置 source: "step"、stepId 和 pointer，并核对当前 Agent 的输入合同。'),
        createElement('label', null, '输入映射 JSON（离开输入框时校验）', createElement('textarea', { style: { minHeight: '70px' }, defaultValue: trainerJson(step.inputBindings), onBlur: e => {
          try { const inputBindings = JSON.parse(e.target.value); setError(''); setWorkflow({ ...workflow, steps: workflow.steps.map(item => item.stepId === step.stepId ? { ...item, inputBindings } : item) }); }
          catch (error) { setError(`${step.stepId}: ${error.message}`); }
        } })))),
      createElement('div', { className: 'trainer-row' }, createElement('select', { value: selectedAgent, onChange: e => setSelectedAgent(e.target.value), 'aria-label': '添加步骤 Agent' }, (state.project?.agents ?? []).map(agent => createElement('option', { key: agent.agentId, value: agent.agentId }, agent.name))),
        createElement('button', { disabled: !selectedAgent || workflow.steps.length >= 64, onClick: () => setWorkflow(trainerAppendStep(workflow, selectedAgent)) }, '添加步骤（可重复）'))),
    ['agent', 'workflow-create', 'workflow'].includes(kind) && createElement('button', { disabled: !base || state.busy || state.mode !== 'training' || (kind === 'workflow' && (!workflow || !!error)), onClick: () => void save() }, '保存候选'),
    kind === 'versions' && createElement('div', { className: 'trainer-stack' },
      createElement('p', null, '发布使用匹配执行包的成功运行证据。服务端核验包摘要，不接受页面声明的成功。'),
      createElement('label', null, '冻结版本 ', createElement('select', { value: frozenVersionId, 'aria-label': '冻结版本', onChange: e => { setFrozenVersionId(e.target.value); setEvidenceRunId(''); } },
        createElement('option', { value: '' }, '请选择冻结版本（不自动选择最新）'),
        frozenVersionId && !selectedFrozen && createElement('option', { value: frozenVersionId, disabled: true }, `未找到冻结版本：${frozenVersionId}`),
        ...frozenVersions.map(version => createElement('option', { key: version.frozenVersionId, value: version.frozenVersionId }, trainerFrozenVersionLabel(version))))),
      selectedFrozen && createElement('div', { className: 'trainer-meta' }, trainerFrozenVersionLabel(selectedFrozen)),
      !frozenVersions.length && createElement('p', { className: 'trainer-meta' }, '该目标暂无已登记冻结版本；列表从服务端恢复。'),
      createElement('button', { disabled: state.busy || state.mode !== 'training', onClick: () => void action(async () => { const frozen = await store.perform('freeze', { revisionId: state.project.revisionId }); setFrozenVersionId(frozen.frozenVersionId); setEvidenceRunId(''); return frozen; }) }, '冻结当前已保存候选'),
      createElement('label', null, '同包验证运行 ', createElement('select', { value: evidenceRunId, onChange: e => setEvidenceRunId(e.target.value) },
        createElement('option', { value: '' }, '请选择同目标、同摘要的成功运行'),
        evidenceRunId && !evidence && createElement('option', { value: evidenceRunId, disabled: true }, `${evidenceRunId}（未匹配当前冻结包）`),
        ...matchingRuns.map(run => createElement('option', { key: run.runId, value: run.runId }, `${run.runId} · ${run.revisionId} · ${run.bundleSha256}`)))),
      selectedFrozen && !matchingRuns.length && createElement('p', { className: 'trainer-warning' }, '已加载历史中没有此冻结包的成功记录。可加载更早运行，或让 Trainer 按此冻结版本进行合成验证。'),
      createElement('button', { disabled: state.busy || !selectedFrozen || !evidence || state.mode === 'engineering', onClick: () => void action(async () => { const staged = await store.perform('stage-release', { frozenVersionId, runId: evidenceRunId }); setReleaseId(staged.releaseId); await store.perform('releases', {}, { mutation: false }); return staged; }) }, '生成自包含发布包'),
      createElement('label', null, '发布版本 ', createElement('select', { value: releaseId, onChange: e => setReleaseId(e.target.value) }, createElement('option', { value: '' }, '请选择发布包'), ...(state.releases ?? []).map(release => createElement('option', { key: release.releaseId, value: release.releaseId }, `${release.releaseId} · ${release.targetKind}/${release.targetId}`)))),
      createElement('button', { disabled: state.busy || !releaseId || state.mode === 'engineering', onClick: () => void action(() => store.perform('activate-release', { releaseId })) }, '激活所选发布版本')),
    kind === 'compare' && createElement('div', { className: 'trainer-stack' },
      createElement('label', null, '修改前 ', createElement('select', { value: beforeRunId, onChange: e => setBeforeRunId(e.target.value) }, createElement('option', { value: '' }, '请选择'), ...runOptions)),
      createElement('label', null, '修改后 ', createElement('select', { value: afterRunId, onChange: e => setAfterRunId(e.target.value) }, createElement('option', { value: '' }, '请选择'), ...runOptions)),
      createElement('button', { disabled: state.busy || !beforeRunId || !afterRunId, onClick: () => void action(() => store.perform('compare', { beforeRunId, afterRunId }, { mutation: false })) }, '比较版本与运行结果')),
    result && createElement('pre', null, trainerJson(result)),
    (error || state.error) && createElement('p', { className: 'trainer-error', role: 'alert' }, error || state.error)));
}


export function TrainerSurfaceSidebar({ store, navigate, openDialog }) {
  const state = useSyncExternalStore(store.subscribe, store.getSnapshot, store.getSnapshot);
  const target = state.target;
  // Selecting an Agent or workflow is a navigation action inside the
  // workbench, not permission to create a native DSH session.  Native
  // creation must remain behind the explicit session-card button so the
  // button is stable and users can choose when to open a conversation.
  const select = (kind, id, mode = state.mode, runId = null) => {
    const next = { projectId: state.projectId, targetKind: kind, targetId: id };
    trainerRememberTarget(next);
    store.select(next, mode, runId);
  };
  const agents = state.project?.agents ?? [];
  const workflows = state.project?.workflows ?? [];
  return createElement('aside', { className: 'trainer-surface-side', 'aria-label': 'Agent 与工作流导航' },
    createElement('button', { className: 'trainer-surface-nav ' + (!target ? 'selected' : ''), onClick: () => {
      const first = workflows[0] ?? agents[0];
      if (first) select(first.workflowId ? 'workflow' : 'agent', first.workflowId ?? first.agentId, 'training', null);
    } }, '✣', createElement('strong', null, 'Agent Trainer')),
    createElement('div', { className: 'trainer-surface-side-group' },
      createElement('div', { className: 'trainer-surface-side-label' }, 'AGENTS ', createElement('span', { className: 'trainer-surface-count' }, agents.length)),
      ...agents.map(agent => createElement('button', { className: 'trainer-surface-nav ' + (target?.targetKind === 'agent' && target.targetId === agent.agentId ? 'selected' : ''), key: agent.agentId, disabled: state.busy, onClick: () => select('agent', agent.agentId) }, '◌', createElement('span', null, agent.name))),
      state.mode === 'training' && createElement('button', { className: 'trainer-surface-nav', disabled: state.busy, onClick: () => openDialog('agent') }, '+', createElement('span', null, '新建 Agent'))),
    createElement('div', { className: 'trainer-surface-side-group' },
      createElement('div', { className: 'trainer-surface-side-label' }, '工作流'),
      ...workflows.map(flow => createElement('button', { className: 'trainer-surface-nav ' + (target?.targetKind === 'workflow' && target.targetId === flow.workflowId ? 'selected' : ''), key: flow.workflowId, disabled: state.busy, onClick: () => select('workflow', flow.workflowId) }, '⌘', createElement('span', null, flow.name), createElement('span', { className: 'trainer-surface-count' }, flow.steps?.length ?? ''))),
      state.mode === 'training' && createElement('button', { className: 'trainer-surface-nav', disabled: state.busy, onClick: () => openDialog('workflow-create') }, '+', createElement('span', null, '新建工作流'))),
    createElement('div', { className: 'trainer-surface-side-group' },
      createElement('div', { className: 'trainer-surface-side-label' }, '观察与记录'),
      createElement('button', { className: 'trainer-surface-nav', disabled: state.busy, onClick: () => openDialog('compare') }, '◷', createElement('span', null, '运行比较'))),
    createElement('div', { className: 'trainer-surface-side-foot' }, createElement('strong', null, 'ATE-Coding-Flow'), createElement('div', null, state.mode === 'training' ? '训练候选 · 可编辑' : state.mode === 'published' ? '冻结版本 · 待发布' : '已激活版本 · 只读'), createElement('div', null, '仅合成训练 · 业务门禁未通过')));
}

export function TrainerSurfaceMain({ store, navigate, openEditor, openDialog, diagnose, openNative }) {
  const state = useSyncExternalStore(store.subscribe, store.getSnapshot, store.getSnapshot);
  const [tab, setTab] = useState('chat');
  const [inputText, setInputText] = useState('{}');
  const [inputTargetKey, setInputTargetKey] = useState('');
  const target = state.target;
  const targetKey = target ? `${target.targetKind}:${target.targetId}` : '';
  const defaultInputText = trainerWorkflowDefaultInputText(target, state.assets);
  useEffect(() => {
    if (!targetKey) return;
    if (inputTargetKey === targetKey && !(inputText.trim() === '{}' && defaultInputText !== '{}')) return;
    setInputText(defaultInputText);
    setInputTargetKey(targetKey);
  }, [defaultInputText, inputTargetKey, inputText, targetKey]);
  const workflowSummary = target?.targetKind === 'workflow' ? (state.project?.workflows ?? []).find(item => item.workflowId === target.targetId) : null;
  const assetWorkflow = state.assets?.files?.['workflows/' + target?.targetId + '.json'];
  // Workflow summaries intentionally contain only identity fields. Only the
  // selected candidate asset is authoritative for step count/order; when it is
  // unavailable, keep the name from the summary but do not infer any steps.
  let workflow = target?.targetKind === 'workflow' ? null : workflowSummary;
  try { if (assetWorkflow) workflow = JSON.parse(assetWorkflow); } catch { workflow = null; /* editor shows the parse error */ }
  const steps = workflow?.steps?.length ? workflow.steps : target?.targetKind === 'agent' ? [{ stepId: 'agent', agentId: target.targetId }] : [];
  const stepCountLabel = target?.targetKind === 'workflow'
    ? (Array.isArray(workflow?.steps) ? steps.length : '步骤待读取') : 1;
  const selectedRun = state.run ?? (state.selectedRunId ? state.runs.find(item => item.runId === state.selectedRunId) : null);
  const targetName = workflow?.name ?? workflowSummary?.name ?? state.project?.agents?.find(item => item.agentId === target?.targetId)?.name ?? target?.targetId ?? 'Agent Trainer';
  const trainerSession = state.binding?.sessionId ?? null;
  const runUnavailableReason = state.busy ? '正在处理操作或刷新状态，请稍候；完成后可再次运行。'
    : !target ? '请先选择一个 Agent 或工作流。'
      : state.mode === 'published' ? '发布模式不执行运行，请切换到训练模式或工程模式。'
        : !state.binding ? '请先创建并打开 DSH 原生会话，绑定完成后即可运行。' : '';
  const selectRun = run => {
    if (!run) return;
    const next = { projectId: run.projectId, targetKind: run.targetKind, targetId: run.targetId };
    trainerRememberTarget(next);
    const mode = run.purpose === 'FRAMEWORK_REPLAY' ? 'engineering' : 'training';
    store.select(next, mode, run.runId); void navigate(next, mode, true, run.runId);
  };
  const start = async () => {
    if (!target || !state.binding) { store.update({ error: TRAINER_UNBOUND_NOTICE }); return; }
    let input;
    try { input = JSON.parse(inputText); } catch (error) { store.update({ error: '运行输入 JSON 无效：' + error.message }); return; }
    try {
      const result = await store.perform('run', { input, ...(state.selectedRunId ? { derivedFromRunId: state.selectedRunId } : {}) });
      const current = store.getSnapshot();
      if (current.target && current.target.targetKind === target.targetKind && current.target.targetId === target.targetId && current.mode === state.mode) {
        store.select(target, state.mode, result.runId);
        void navigate(target, state.mode, state.binding?.presetId === 'agent-trainer' || target.targetKind === 'workflow', result.runId);
      }
    } catch { /* state.error is rendered below */ }
  };
  const error = state.error || state.readError;
  const surfaceTone = trainerStatusTone(state.run?.status);
  const modeLabel = state.mode === 'training' ? '训练工作区' : state.mode === 'published' ? '发布管理' : '工程执行';
  const renderTab = tab === 'chat'
    ? createElement('div', { className: 'trainer-surface-native-prompt' },
        createElement('div', { className: 'trainer-surface-native-icon' }, '✣'),
        createElement('div', null,
          createElement('strong', null, trainerSession ? '已绑定 DSH 原生会话' : '尚未打开 DSH 原生会话'),
          createElement('p', null, trainerSession ? '会话内容由 DSH 原生会话渲染。工作台不复制或伪造对话记录。' : '工作台只负责目标、流程和运行控制；打开原生会话后再输入消息。'),
          createElement('div', { className: 'trainer-row' }, createElement('button', { className: 'trainer-surface-primary', disabled: state.busy || !target, onClick: openNative, title: state.busy ? '正在创建或打开 DSH 原生会话…' : (trainerSession ? '打开已绑定的 DSH 原生会话' : '创建并打开 DSH 原生会话') }, trainerSession ? '打开原生会话' : '创建并打开原生会话'), trainerSession && createElement('span', { className: 'trainer-meta' }, trainerSession))))
    : tab === 'config'
      ? createElement('div', { className: 'trainer-surface-plain' }, createElement('h3', null, '工作流配置'), createElement('p', null, target?.targetKind === 'workflow' ? '当前候选包含 ' + steps.length + ' 个步骤。' : 'Agent 候选由指令、Skill 和接口合同组成。'), createElement('button', { disabled: state.busy || !target, onClick: () => openDialog(target?.targetKind === 'workflow' ? 'workflow' : 'assets') }, target?.targetKind === 'workflow' ? '编辑步骤与输入映射' : '打开候选资产'))
      : tab === 'diff'
        ? createElement('div', { className: 'trainer-surface-plain' }, createElement('h3', null, '修改记录'), createElement('p', null, '当前候选版本：' + (state.project?.revisionId ?? '读取中')), createElement('p', { className: 'trainer-meta' }, state.assets ? '已加载候选资产，可在编辑器中查看完整文件差异。' : '修改候选后可查看完整文件差异。'), createElement('button', { disabled: state.busy || !target, onClick: openEditor }, '查看候选资产'))
        : createElement('div', { className: 'trainer-surface-plain' }, createElement('h3', null, '运行记录'), state.runs.length ? createElement('div', { className: 'trainer-surface-run-list' }, ...state.runs.slice(0, 20).map(run => createElement('button', { key: run.runId, className: 'trainer-surface-run-row', onClick: () => selectRun(run), disabled: state.busy }, createElement('span', null, run.runId), createElement('span', { className: trainerStatusClass(run.status) }, trainerRunLabel(run.status) + ' · ' + run.revisionId)))) : createElement('p', null, '尚无运行记录。'), state.nextRunsCursor != null && createElement('button', { disabled: state.busy, onClick: () => void store.loadMoreRuns().catch(() => {}) }, '加载更早运行'));
  return createElement('main', { className: 'trainer-surface-main' },
    createElement('section', { className: 'trainer-surface-heading' }, createElement('div', { className: 'trainer-surface-crumb' }, modeLabel, ' 〉 ', target?.targetKind === 'agent' ? '单个 Agent' : '工作流', target ? ' 〉 Agent Trainer' : ''), createElement('div', { className: 'trainer-surface-heading-row' }, createElement('div', null, createElement('h1', null, targetName), createElement('div', { className: 'trainer-surface-subline' }, target ? (target.targetKind === 'workflow' ? '线性编排 · ' : '独立训练 · ') + stepCountLabel + (stepCountLabel === '步骤待读取' ? '' : ' 个执行步骤') + ' · 候选 ' + (state.project?.revisionId ?? '读取中') : '选择一个 Agent 或工作流开始训练')), createElement('div', { className: 'trainer-surface-actions' }, createElement('button', { disabled: state.busy || !target, onClick: openEditor }, '▣ 保存'), createElement('button', { disabled: state.busy || !target, onClick: () => openDialog('versions') }, '❄ 冻结 / 发布')))),
    createElement('nav', { className: 'trainer-surface-tabs', 'aria-label': '训练工作区标签' }, ...[['chat', '训练会话'], ['config', '工作流配置'], ['diff', '修改记录'], ['runs', '运行记录']].map(item => createElement('button', { key: item[0], 'aria-pressed': tab === item[0], onClick: () => setTab(item[0]) }, item[1]))),
    createElement('div', { className: 'trainer-surface-workarea' }, createElement('section', { className: 'trainer-surface-session', 'aria-label': 'Trainer 工作区' }, createElement('div', { className: 'trainer-surface-sessionbar' }, createElement('span', { className: `trainer-surface-led trainer-status-${surfaceTone}` }), trainerSession ? 'DSH 会话已绑定' : '工作台概览', ' · ', targetName, createElement('span', { style: { marginLeft: 'auto' } }, trainerSession ?? '未绑定')), renderTab, createElement('div', { className: 'trainer-surface-spacer' }), createElement('div', { className: 'trainer-surface-chips' }, createElement('button', { className: 'trainer-surface-chip', disabled: state.busy || !target, onClick: () => void store.refresh() }, '检查当前运行'), createElement('button', { className: 'trainer-surface-chip', disabled: state.busy || state.mode !== 'training' || !target, onClick: openEditor }, '修改并复测'), createElement('button', { className: 'trainer-surface-chip trainer-surface-primary', disabled: !!runUnavailableReason, title: runUnavailableReason || '运行当前候选', onClick: () => void start() }, '运行一次')), runUnavailableReason && createElement('p', { className: 'trainer-meta', role: 'status' }, runUnavailableReason), createElement('div', { className: 'trainer-surface-composer' }, createElement('label', { className: 'trainer-meta', htmlFor: 'trainer-surface-input' }, '合成运行输入 JSON'), createElement('textarea', { id: 'trainer-surface-input', 'aria-label': '运行输入 JSON', value: inputText, onChange: event => setInputText(event.target.value), placeholder: defaultInputText }), createElement('div', { className: 'trainer-surface-composer-bottom' }, createElement('span', null, '仅合成训练 · 不启动真实业务流'), createElement('button', { disabled: state.busy || !trainerSession, onClick: openNative }, '进入原生会话')))), createElement('aside', { className: 'trainer-surface-inspector', 'aria-label': '运行状态' }, createElement(TrainerRunDetails, { store, onDiagnose: diagnose }), selectedRun && createElement('div', { className: 'trainer-surface-status' }, '候选版本：' + (selectedRun.revisionId ?? '—') + ' · 业务门禁未通过'), error && createElement('p', { className: 'trainer-error', role: 'alert' }, error), state.notice && createElement('p', { className: 'trainer-surface-status', role: 'status' }, state.notice))));
}

export function TrainerWorkbenchSurface({ store, navigate, openEditor, openDialog, diagnose, openNative }) {
  const [surfaceTheme, setSurfaceTheme] = useState(trainerSurfaceTheme);
  const state = useSyncExternalStore(store.subscribe, store.getSnapshot, store.getSnapshot);
  useEffect(() => {
    if (!state.enabled || state.surfaceVisible === false || state.target || !state.project) return;
    const preferred = trainerPreferredTarget(state.projectId, state.project, state.runs);
    // Opening the overview must not implicitly create or bind a native DSH
    // session.  Selecting the first target loads its real project/assets;
    // the user explicitly starts native-session work with the button in the
    // session card.  This keeps the empty state recoverable when the host
    // session index is still pending and avoids a surprise timeout on load.
    if (preferred) { trainerRememberTarget(preferred); store.select(preferred, state.mode, null); }
  }, [state.enabled, state.surfaceVisible, state.target, state.project, state.runs, state.loading, state.projectId, state.mode]);
  if (!state.enabled || state.surfaceVisible === false) return null;
  const toggleSurfaceTheme = () => {
    const next = surfaceTheme === 'v2' ? 'v1' : 'v2';
    setSurfaceTheme(next);
    try { globalThis.localStorage?.setItem(TRAINER_SURFACE_THEME_KEY, next); } catch { /* optional UI preference */ }
  };
  return createElement('div', { className: `trainer-surface trainer-surface-${surfaceTheme}`, 'data-theme': surfaceTheme, 'data-ui-version': surfaceTheme.toUpperCase(), role: 'dialog', 'aria-label': 'DSH Agent Trainer 工作台' }, createElement('style', null, TRAINER_SURFACE_STYLES_V2),
    createElement('header', { className: 'trainer-surface-top' }, createElement('div', { className: 'trainer-surface-brand' }, createElement('span', { className: 'trainer-surface-brand-mark' }, 'D'), createElement('strong', null, 'DSH'), ' / ', createElement('strong', null, 'PTC 工作台'), createElement('span', { className: 'trainer-surface-project' }, 'ATE-Coding-Flow')),
      createElement('nav', { className: 'trainer-surface-modes', 'aria-label': '工作模式' }, ...[['training', '训练模式'], ['published', '发布模式'], ['engineering', '工程模式']].map(item => createElement('button', { key: item[0], 'aria-pressed': state.mode === item[0], disabled: state.busy, onClick: () => { const target = state.target; if (target) { store.select(target, item[0], null); void navigate(target, item[0], item[0] === 'training' || target.targetKind === 'workflow', null); } else store.select(null, item[0]); } }, item[1]))),
      createElement('span', { className: 'trainer-surface-demo' }, `${surfaceTheme.toUpperCase()} · 合成训练·演示数据`), createElement('button', { className: 'trainer-surface-theme-toggle', onClick: toggleSurfaceTheme, title: surfaceTheme === 'v2' ? '切换到 V1 当前样式' : '切换到 V2 试用样式' }, surfaceTheme === 'v2' ? 'V1 样式' : 'V2 样式'), createElement('button', { className: 'trainer-surface-close', onClick: () => store.update({ surfaceVisible: false }) }, '收起')),
    createElement('div', { className: 'trainer-surface-shell' }, createElement(TrainerSurfaceSidebar, { store, navigate, openDialog }), createElement(TrainerSurfaceMain, { store, navigate, openEditor, openDialog, diagnose, openNative })));
}

export function TrainerSidebar({ store, navigate, openEditor, openDialog, wide = true, expandSidebar }) {
  const state = useSyncExternalStore(store.subscribe, store.getSnapshot, store.getSnapshot);
  const [inputText, setInputText] = useState('{}');
  const [tab, setTab] = useState('objects');
  const [localError, setLocalError] = useState('');
  const target = state.target;
  const select = (kind, id, mode = state.mode, trainer = false, runId = null) => {
    const next = { projectId: state.projectId, targetKind: kind, targetId: id };
    store.select(next, mode, runId);
    void navigate(next, mode, trainer, runId);
  };
  const start = async () => {
    try {
      setLocalError('');
      const result = await store.perform('run', { input: JSON.parse(inputText), ...(state.selectedRunId ? { derivedFromRunId: state.selectedRunId } : {}) });
      const current = store.getSnapshot();
      if (current.target?.targetKind === target.targetKind && current.target?.targetId === target.targetId && current.mode === state.mode) select(target.targetKind, target.targetId, state.mode, state.binding?.presetId === 'agent-trainer', result.runId);
    } catch (error) { setLocalError(error.message); }
  };
  if (!wide) return createElement('div', { className: 'trainer-ui' }, createElement('button', { title: '展开 Agent Trainer', onClick: expandSidebar }, 'AT'));
  return createElement('aside', { className: 'trainer-ui trainer-nav', 'data-testid': 'trainer-sidebar' },
    createElement('h2', null, 'Agent Trainer'),
    createElement('div', { className: 'trainer-meta' }, state.projectId),
    createElement('div', { className: 'trainer-row' }, ['training', 'published', 'engineering'].map(mode => createElement('button', { key: mode, disabled: state.busy, 'aria-pressed': state.mode === mode,
      onClick: () => { if (target) select(target.targetKind, target.targetId, mode); else store.select(null, mode); } }, { training: '训练', published: '发布', engineering: '工程' }[mode]))),
    target && createElement('p', { className: 'trainer-meta' }, `${target.targetKind} / ${target.targetId} · 候选 ${state.project?.revisionId ?? '—'}`),
    createElement('div', { className: 'trainer-row' }, ['objects', 'history', 'observe'].map(value => createElement('button', { key: value, 'aria-pressed': tab === value, onClick: () => setTab(value) }, { objects: '对象', history: '历史', observe: '观察' }[value]))),
    tab === 'objects' && createElement('div', null,
      createElement('h3', null, '已登记 Agent'), createElement('div', { className: 'trainer-stack' }, (state.project?.agents ?? []).map(agent => createElement('button', { className: 'trainer-object', key: agent.agentId, disabled: state.busy, 'aria-pressed': target?.targetKind === 'agent' && target.targetId === agent.agentId, onClick: () => select('agent', agent.agentId) }, agent.name))),
      createElement('button', { disabled: state.busy || state.mode !== 'training', onClick: () => openDialog('agent') }, '新建 Agent'),
      createElement('h3', null, '工作流'), createElement('div', { className: 'trainer-stack' }, (state.project?.workflows ?? []).map(flow => createElement('button', { className: 'trainer-object', key: flow.workflowId, disabled: state.busy, 'aria-pressed': target?.targetKind === 'workflow' && target.targetId === flow.workflowId, onClick: () => select('workflow', flow.workflowId) }, flow.name))),
      state.mode === 'training' && createElement('button', { disabled: state.busy, onClick: () => openDialog('workflow-create') }, '新建工作流'),
      !state.project && createElement('p', null, state.loading ? '读取项目…' : '项目尚未就绪'),
      target && createElement('div', { className: 'trainer-stack' },
        createElement('h3', null, '训练与版本'),
        createElement('button', { disabled: state.busy || state.mode !== 'training', onClick: () => { store.update({ surfaceVisible: true }); select(target.targetKind, target.targetId, 'training', true, state.selectedRunId); } }, '打开 Agent Trainer'),
        createElement('button', { disabled: state.busy, onClick: openEditor }, state.mode === 'training' ? '编辑候选 / 保存 / 冻结' : '查看候选（只读）'),
        target.targetKind === 'workflow' && createElement('button', { disabled: state.busy || state.mode !== 'training', onClick: () => openDialog('workflow') }, '编辑步骤与顺序'),
        createElement('button', { disabled: state.busy, onClick: () => openDialog('versions') }, '冻结 / 发布 / 激活'),
        createElement('button', { disabled: state.busy, onClick: () => openDialog('compare') }, '比较运行与修改'),
        createElement('label', null, '运行输入 JSON', createElement('textarea', { 'aria-label': '运行输入 JSON', value: inputText, onChange: e => setInputText(e.target.value), rows: 3, style: { width: '100%' } })),
        createElement('button', { className: 'trainer-primary', disabled: state.busy || !state.binding || state.mode === 'published', onClick: () => void start() }, state.mode === 'engineering' ? '运行活动发布版' : '运行当前候选'))),
    tab === 'history' && createElement('div', { className: 'trainer-stack' }, state.runs.map(run => createElement('button', { key: run.runId, className: 'trainer-object', disabled: state.busy, onClick: () => select(run.targetKind, run.targetId, run.purpose === 'FRAMEWORK_REPLAY' ? 'engineering' : 'training', true, run.runId) }, createElement('span', null, run.runId, createElement('div', { className: 'trainer-meta' }, `${trainerRunLabel(run.status)} · ${run.revisionId}`))))),
    tab === 'history' && state.nextRunsCursor != null && createElement('button', { disabled: state.busy, onClick: () => void store.loadMoreRuns().catch(() => {}) }, '加载更早运行'),
    tab === 'observe' && createElement(TrainerRunDetails, { store, compact: true, onDiagnose: run => select(run.targetKind, run.targetId, 'training', true, run.runId) }),
    createElement('p', { className: 'trainer-empty trainer-meta' }, '布局帮助：新建空会话时，可在左栏“观察”查看运行；非空会话可用顶部“运行观察”打开右栏。'),
    createElement('div', { className: 'trainer-row' }, createElement('button', { onClick: () => store.update({ detailsVisible: !state.detailsVisible }) }, state.detailsVisible ? '原生工具详情' : '运行观察右栏'), createElement('button', { onClick: () => store.enable(false) }, '退出工作台')),
    state.notice && createElement('p', { role: 'status' }, state.notice),
    (localError || state.error || state.readError) && createElement('p', { role: 'alert', className: 'trainer-error' }, localError || state.error || state.readError));
}

// Public slot registrations are acquired only while this workbench owns the surface.
export function installTrainerWorkbench(ctx, { store = createTrainerStore() } = {}) {
  const navigator = createTrainerNavigator({ services: ctx, api: store.api });
  let navigationVersion = 0;
  let disposed = false;
  let editorOpen = false;
  const editorListeners = new Set();
  const setEditor = value => { editorOpen = value; editorListeners.forEach(fn => fn()); };
  const navigate = async (target, mode, trainer, selectedRunId) => {
    navigationVersion += 1;
    try {
      const binding = await navigator.open({ target, mode, trainer, selectedRunId, title: `${trainer ? 'Agent Trainer' : 'Framework'} · ${target.targetId}` });
      store.setBinding(binding);
      return binding;
    } catch (error) { if (error.name !== 'AbortError') store.update({ error: error.message }); return null; }
  };
  const openNative = async () => {
    let current = store.getSnapshot();
    if (current.busy) return;
    let target = current.target;
    if (!target) {
      target = trainerPreferredTarget(current.projectId, current.project, current.runs);
      if (!target) { store.update({ error: '项目尚无可用 Agent 或工作流' }); return; }
      trainerRememberTarget(target);
      store.select(target, current.mode, null);
      current = store.getSnapshot();
    }
    store.update({ busy: true, error: null, notice: '正在创建或打开 DSH 原生会话…' });
    try {
      const binding = await navigate(target, current.mode, current.mode === 'training' || target.targetKind === 'workflow', current.selectedRunId);
      if (!binding) { store.update({ notice: '' }); return; }
      current = store.getSnapshot();
      if (!current.binding?.sessionId) throw new Error('原生会话绑定未完成');
      store.update({ surfaceVisible: false, detailsVisible: false, notice: '已切换到 DSH 原生会话；工作台仍保留在 Agent Trainer 入口。' });
    } catch (error) {
      if (error.name !== 'AbortError') store.update({ error: error.message, notice: '' });
      else store.update({ notice: '' });
    }
    finally { store.update({ busy: false }); }
  };
  const diagnose = run => {
    const target = { projectId: run.projectId, targetKind: run.targetKind, targetId: run.targetId };
    store.select(target, 'training', run.runId); void navigate(target, 'training', true, run.runId);
  };
  const Footer = () => {
    const state = useSyncExternalStore(store.subscribe, store.getSnapshot, store.getSnapshot);
    return createElement('div', { className: 'trainer-ui' }, createElement('style', null, TRAINER_STYLES), createElement('button', { onClick: () => state.enabled ? store.update({ surfaceVisible: !state.surfaceVisible }) : store.enable(true), 'aria-pressed': state.enabled }, 'Agent Trainer'));
  };
  const Sidebar = props => createElement(TrainerSidebar, { ...props, store, navigate, openEditor: () => setEditor('assets'), openDialog: setEditor });
  const Details = ({ sessionId }) => {
    const state = useSyncExternalStore(store.subscribe, store.getSnapshot, store.getSnapshot);
    const sessions = useSyncExternalStore(ctx.sessions.list.subscribe, ctx.sessions.list.getSnapshot, ctx.sessions.list.getSnapshot);
    const blank = sessions.byId[sessionId]?.blank !== false;
    useEffect(() => {
      if (!blank && state.enabled && state.binding?.sessionId === sessionId && state.detailsVisible) ctx.layout.openDetails();
    }, [sessionId, blank, state.binding?.bindingRevision, state.enabled, state.detailsVisible]);
    return createElement('div', { className: 'trainer-ui trainer-details' }, createElement('button', { onClick: () => store.update({ detailsVisible: false }) }, '切回原生工具详情'), createElement(TrainerRunDetails, { store, onDiagnose: diagnose }));
  };
  const Header = ({ sessionId }) => {
    const state = useSyncExternalStore(store.subscribe, store.getSnapshot, store.getSnapshot);
    if (!state.enabled || state.binding?.sessionId !== sessionId) return null;
    return createElement('div', { className: 'trainer-ui trainer-header' }, createElement('div', { className: 'trainer-meta' }, `${state.binding.presetId} · ${state.target.targetId} · ${state.selectedRunId ?? '未选择运行'}`), createElement('button', { onClick: () => { store.update({ detailsVisible: true }); ctx.layout.openDetails(); } }, '运行观察'));
  };
  const EditorLayer = () => {
    const state = useSyncExternalStore(store.subscribe, store.getSnapshot, store.getSnapshot);
    const open = useSyncExternalStore(fn => { editorListeners.add(fn); return () => editorListeners.delete(fn); }, () => editorOpen, () => false);
    return open && state.enabled ? createElement(open === 'assets' ? TrainerAssetEditor : TrainerProjectDialog, { key: `${state.projectId}/${state.target?.targetId}/${state.mode}/${open}`, kind: open, store, close: () => setEditor(false) }) : null;
  };
  const fixed = [
    ctx.slots.inject('sidebar.footer.action', () => ctx.slots.register({ name: 'sidebar.footer.action', id: 'trainer-entry', order: 50 }, Footer)),
    ctx.slots.inject('conversation.session.header.actions', () => ctx.slots.register({ name: 'conversation.session.header.actions', id: 'trainer-binding', order: -20 }, Header)),
    ctx.slots.inject('shell.overlay', () => ctx.slots.register({ name: 'shell.overlay', id: 'trainer-editor', order: 95 }, EditorLayer)),
    // Host fallback only: this surface is a truthful trainer overview; DSH conversation/composer stays native.
    ctx.slots.inject('shell.overlay', () => ctx.slots.register({ name: 'shell.overlay', id: 'trainer-surface', order: 100 }, () => createElement(TrainerWorkbenchSurface, { store, navigate, openEditor: () => setEditor('assets'), openDialog: setEditor, diagnose, openNative })))
  ];
  let sidebarDispose = null;
  let detailsDispose = null;
  let observedSession;
  let observing = false;
  let restoreVersion = 0;
  function restore(current) {
    const version = ++restoreVersion;
    const navigation = navigationVersion;
    if (!current) { store.update({ binding: null }); return; }
    void store.api('bind-session', { projectId: store.getSnapshot().projectId, sessionId: current }).then(binding => {
      if (disposed || version !== restoreVersion || navigation !== navigationVersion || !store.getSnapshot().enabled || ctx.sessions.list.getSnapshot().current !== current) return;
      if (binding.projectId !== store.getSnapshot().projectId) throw new Error('当前会话属于其他项目');
      if (store.getSnapshot().binding?.sessionId === current) return;
      store.select({ projectId: binding.projectId, targetKind: binding.targetKind, targetId: binding.targetId }, binding.mode, binding.selectedRunId ?? null);
      store.setBinding(binding);
    }).catch(error => {
      if (disposed || version !== restoreVersion || navigation !== navigationVersion || !store.getSnapshot().enabled || ctx.sessions.list.getSnapshot().current !== current) return;
      store.select(null);
      store.update({ notice: error.code === 'session_unbound' ? TRAINER_UNBOUND_NOTICE : '', error: error.code === 'session_unbound' ? null : error.message });
    });
  }
  function reconcile() {
    const state = store.getSnapshot();
    const current = ctx.sessions.list.getSnapshot().current;
    try { globalThis.localStorage?.setItem('trainer-workbench-enabled-v1', state.enabled ? 'true' : 'false'); } catch { /* optional UI preference */ }
    if (state.enabled && (!observing || current !== observedSession)) {
      observing = true; observedSession = current; restore(current);
    }
    if (!state.enabled) { observing = false; restoreVersion += 1; }
    if (state.enabled && !sidebarDispose) sidebarDispose = ctx.slots.inject('sidebar.workspaces', () => ctx.slots.register({ name: 'sidebar.workspaces', id: 'trainer-navigation', priority: -50 }, Sidebar));
    if (!state.enabled && sidebarDispose) { sidebarDispose(); sidebarDispose = null; navigator.cancel(); setEditor(false); }
    const show = state.enabled && state.detailsVisible && current && state.binding?.sessionId === current;
    if (show && !detailsDispose) detailsDispose = ctx.slots.inject('details', () => ctx.slots.register({ name: 'details', id: 'trainer-observer', priority: -50 }, Details));
    if (!show && detailsDispose) { detailsDispose(); detailsDispose = null; }
  }
  fixed.push(store.subscribe(reconcile), ctx.sessions.list.subscribe(reconcile));
  let restoreEnabled = false;
  try { restoreEnabled = globalThis.localStorage?.getItem('trainer-workbench-enabled-v1') === 'true'; } catch { /* optional UI preference */ }
  if (restoreEnabled) store.enable(true);
  reconcile();
  return () => {
    disposed = true; restoreVersion += 1;
    navigator.cancel(); store.dispose(); sidebarDispose?.(); detailsDispose?.();
    fixed.reverse().forEach(dispose => dispose()); editorListeners.clear();
  };
}
