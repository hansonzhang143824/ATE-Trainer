import test from 'node:test';
import assert from 'node:assert/strict';
import { workflowStatusSummary } from '../client/workflow-status.js';

test('workflow status counts only host receipts and shows current handoff', () => {
  const summary = workflowStatusSummary({
    stages: [
      { tasks: [{ profileId: 'ptc-dft-expert', status: 'completed' },
        { profileId: 'ptc-schematic-expert', status: 'dispatching' }] },
      { tasks: [{ profileId: 'strategy-expert', status: 'pending' }] },
    ],
    auxiliaryTasks: [{ profileId: 'evolution-expert', status: 'pending' }],
  });
  assert.deepEqual(summary, { completed: 1, total: 4, currentProfileId: 'ptc-schematic-expert',
    handoffFrom: 'ptc-dft-expert', currentStatus: 'dispatching' });
});

test('workflow status remains empty without a real orchestration', () => {
  assert.deepEqual(workflowStatusSummary(null), { completed: 0, total: 0,
    currentProfileId: null, handoffFrom: null, currentStatus: null });
});
