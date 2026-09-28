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
import { createElement } from "react";
import { createPtcStateStore } from "./state.js";
import { PtcControlPanel } from "./panel.js";

/** Locale namespace for this plugin. */
export const PTC_CONTROL_PLANE_LOCALE_NAMESPACE = "ptc-control-plane";

/** Locale dictionaries (zh / en), mirroring the agent-teams pattern. */
export const localeDictionaries = {
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
export const inject = ["slots", "locale"];

/** Slot mount point proven to exist in the current DSH web client. */
export const SHELL_SLOT_NAME = "shell.overlay";
export const PANEL_SLOT_ID = "ptc-control-plane";

/**
 * Install the plugin into a DSH client context.
 *
 * @param {{ slots: object, locale: object, effect: Function }} ctx
 */
export function apply(ctx) {
  ctx.effect(
    () => ctx.locale.register(PTC_CONTROL_PLANE_LOCALE_NAMESPACE, localeDictionaries),
    "ptc-control-plane: dictionaries"
  );

  const store = createPtcStateStore();

  const mount = (sessionServices = null) => {
    const Panel = ({ t }) => createElement(PtcControlPanel, { store, t, sessionServices });
    ctx.slots.inject(SHELL_SLOT_NAME, () => ctx.slots.register(
      { name: SHELL_SLOT_NAME, id: PANEL_SLOT_ID, order: 90,
        label: "PTC control plane", locale: PTC_CONTROL_PLANE_LOCALE_NAMESPACE }, Panel));
  };

  // Native slot injection: the host places the panel in its overlay region.
  if (typeof ctx.inject === "function") {
    ctx.inject(["connection", "sessions", "workspaces"],
      sessionServices => mount(sessionServices));
  } else mount(null);
}

export default { inject, apply, PtcControlPanel, createPtcStateStore };
