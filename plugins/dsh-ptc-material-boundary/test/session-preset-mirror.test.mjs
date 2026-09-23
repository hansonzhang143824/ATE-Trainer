/**
 * Differential check: my `resolveSessionPreset` must agree with DSH's own.
 *
 * Reading two implementations side by side is weaker than running both on the
 * same inputs, so this imports the INSTALLED `@deepseek-ai/dsh-agent-presets`
 * implementation and compares results case by case. When the package cannot be
 * found (the plugin is deployed without the harness checkout) the comparison is
 * SKIPPED and says so — it never reports agreement it did not check.
 */
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import test from 'node:test';
import { pathToFileURL } from 'node:url';
import { resolveSessionPreset } from '../lib/session-preset.js';

function findDshImplementation() {
  const candidates = [
    path.join(process.env.APPDATA ?? path.join(os.homedir(), 'AppData', 'Roaming'),
      'npm', 'node_modules', '@deepseek-ai', 'dsh', 'node_modules', '@deepseek-ai',
      'dsh-agent-presets', 'lib', 'types', 'session.js'),
    path.join(os.homedir(), '.dsh', 'profiles', 'node_modules', '@deepseek-ai',
      'dsh-agent-presets', 'lib', 'types', 'session.js'),
  ];
  return candidates.find((candidate) => fs.existsSync(candidate));
}

const CASES = [
  ['no header preset, no events', { header: {}, events: [] }],
  ['header only', { header: { agentPreset: 'standard-70' }, events: [] }],
  ['event only', { header: {}, events: [{ type: 'agent-preset/selected', data: { agentPreset: 'ptc-dft-expert' } }] }],
  ['event wins over header', { header: { agentPreset: 'ate-ptc' }, events: [{ type: 'agent-preset/selected', data: { agentPreset: 'ptc-dft-expert' } }] }],
  ['newest event wins', {
    header: { agentPreset: 'ate-ptc' },
    events: [
      { type: 'agent-preset/selected', data: { agentPreset: 'ptc-dft-expert' } },
      { type: 'other', data: {} },
      { type: 'agent-preset/selected', data: { agentPreset: 'ptc-schematic-expert' } },
    ],
  }],
  ['unrelated events are ignored', { header: { agentPreset: 'standard-70' }, events: [{ type: 'turn/start', data: {} }] }],
];

test('my resolveSessionPreset agrees with the installed DSH implementation', async (t) => {
  const implementation = findDshImplementation();
  if (implementation === undefined) {
    t.skip('the installed @deepseek-ai/dsh-agent-presets package was not found, so agreement could not be checked');
    return;
  }
  const dsh = await import(pathToFileURL(implementation).href);
  assert.equal(typeof dsh.resolveSessionPreset, 'function', 'the DSH module must export resolveSessionPreset');
  for (const [label, session] of CASES) {
    assert.equal(
      resolveSessionPreset(session),
      dsh.resolveSessionPreset(session),
      `disagreement on: ${label}`,
    );
  }
});

test('my resolveSessionPreset tolerates the shapes a live session can have', () => {
  assert.equal(resolveSessionPreset(undefined), undefined);
  assert.equal(resolveSessionPreset({}), undefined);
  assert.equal(resolveSessionPreset({ header: { agentPreset: 'ate-ptc' } }), 'ate-ptc', 'an absent event array falls back to the header');
  assert.equal(resolveSessionPreset({ header: {}, events: [{ type: 'agent-preset/selected' }] }), undefined, 'an event with no data yields undefined rather than throwing');
});
