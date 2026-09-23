import { decision } from './policy.js';
import { installCaptainEntryHook } from './captain-entry.js';

export const name = 'dsh-ptc-material-boundary';
export const inject = ['tools', 'subagents'];

export function apply(ctx, config = {}) {
  if (typeof config.workspaceRoot !== 'string' || !config.workspaceRoot) {
    throw new Error('dsh-ptc-material-boundary: workspaceRoot is required');
  }
  // Captain's first-message hook creates the batch before the model can plan
  // or dispatch. The existing tool hook keeps DFT/schematic source boundaries.
  ctx.logger?.info?.("dsh-ptc-material-boundary active");
  installCaptainEntryHook(ctx, config);
  const options = {
    // Handoff section 5.1 has the user run evaluate-then-publish from the training
    // session, so a training session may invoke the gated publisher by default.
    // Set `allowTrainingPublish: false` to make training strictly draft-only
    // (rule 6 read literally); nothing else changes.
    allowTrainingPublish: config.allowTrainingPublish !== false,
  };
  ctx.on('tools/pre-execute', (exec, next) => {
    const reason = decision(exec, config.workspaceRoot, options);
    return reason ? { kind: 'deny', reason } : next();
  }, { prepend: true });
  // The same decision is ALSO registered as a monotonic guard (handoff P0 item 6).
  // The guard stage runs after the pre-execute waterfall, the first denial wins,
  // and no guard can force an allow — so this can only add denials, never remove
  // one. It matters because `toolFilter` is not a security boundary and a caller
  // that never reaches the waterfall would otherwise skip the check entirely.
  ctx.tools.guard((exec) => decision(exec, config.workspaceRoot, options));
}
