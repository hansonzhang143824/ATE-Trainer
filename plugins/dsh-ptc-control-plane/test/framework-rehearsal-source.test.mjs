import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import test from 'node:test';
import { preflightFrameworkRehearsalSources, assertFrameworkSourcesUnchanged } from '../lib/framework-rehearsal-source.js';

const SHA = 'a'.repeat(64);
const SCH = ['SCH-Connect-Map.txt', 'SCH-Connect-Map.json', 'Component-Statistic.txt',
  'Components-Statistic.json', 'Path-Proofs.txt', 'Path-Proofs.json', 'schematic-receipt.json'];
const DFT = ['dft-meta.json', 'dft-conditions.yaml', 'dft-semantic-review.json'];

function fixture(t) {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'ptc-rehearsal-source-'));
  t.after(() => fs.rmSync(root, { recursive: true, force: true }));
  const input = path.join(root, 'project/DALI/Input_GlobalMaterial');
  const sch = path.join(root, 'project/DALI/Output_Global_Material/schematic');
  const dft = path.join(root, 'project/DALI/Output_Global_Material/dft/TM109');
  for (const directory of [input, sch, dft]) fs.mkdirSync(directory, { recursive: true });
  for (const file of SCH) fs.writeFileSync(path.join(sch, file), file);
  for (const file of DFT) fs.writeFileSync(path.join(dft, file), file);
  fs.writeFileSync(path.join(input, 'sch.csv'), 'source');
  fs.writeFileSync(path.join(input, 'dft.xlsx'), 'source');
  const reports = [
    { role: 'schematic-expert', gate: 'SCHEMATIC_OUTPUT', status: 'ready',
      canonicalInput: { path: path.join(input, 'sch.csv'), sha256: SHA },
      requiredOutputs: SCH.map(name => path.join(sch, name)), missingOrStaleOutputs: [] },
    { role: 'dft-expert', gate: 'DFT_OUTPUT', status: 'ready',
      canonicalInput: { path: path.join(input, 'dft.xlsx'), sha256: SHA },
      requiredOutputs: DFT.map(name => path.join(dft, name)), missingOrStaleOutputs: [] },
  ];
  return { root, reports };
}

test('rehearsal source preflight accepts only gate-ready exact product sets', async t => {
  const { root, reports } = fixture(t);
  const commands = [];
  const result = await preflightFrameworkRehearsalSources(root, ['TM109'], {
    runHostCommand: async (exe, args, options) => {
      commands.push({ exe, args, options });
      return { status: 'passed', exitCode: 0, stdout: JSON.stringify(reports[commands.length - 1]) };
    },
  });
  assert.equal(result.kind, 'verified-source-products');
  assert.equal(result.schematic.files.length, 7);
  assert.equal(result.dft[0].files.length, 3);
  assert.equal(assertFrameworkSourcesUnchanged(root, result), true);
  assert.equal(commands.length, 2);
  assert.ok(commands.every(command => command.exe === 'python' && command.options.timeoutMs === 30_000));
  assert.deepEqual(commands[1].args.slice(-2), ['--tm', 'TM109']);
  fs.appendFileSync(result.dft[0].files[0], 'tamper');
  assert.throws(() => assertFrameworkSourcesUnchanged(root, result), /changed during snapshot/);
});

test('rehearsal source preflight fails closed on stale or misdirected gate outputs', async t => {
  const { root, reports } = fixture(t);
  const run = async altered => preflightFrameworkRehearsalSources(root, ['TM109'], {
    runHostCommand: async (_exe, args) => ({ status: 'passed', exitCode: 0,
      stdout: JSON.stringify(args.some(arg => arg.includes('schematic')) ? reports[0] : altered) }),
  });
  await assert.rejects(run({ ...reports[1], status: 'stale' }), /did not attest ready/);
  await assert.rejects(run({ ...reports[1], requiredOutputs: reports[1].requiredOutputs.slice(1) }), /unexpected/);
  await assert.rejects(run({ ...reports[1], canonicalInput: { path: path.join(root, 'outside.xlsx'), sha256: SHA } }), /outside the approved/);
  await assert.rejects(preflightFrameworkRehearsalSources(root, ['TM109', 'TM109']), /unique explicit/);
});

test('timed-out source gate preserves exact command and uncertain tree cleanup evidence', async t => {
  const { root } = fixture(t);
  await assert.rejects(preflightFrameworkRehearsalSources(root, ['TM109'], {
    runHostCommand: async () => ({ command: 'python -X utf8 scripts/validate_schematic_outputs.py',
      status: 'blocked', stopReason: 'timeout', exitCode: null, terminationConfirmed: false,
      treeTerminationConfirmed: false, termination: { status: 'unknown' } }),
  }), error => {
    assert.match(error.message, /validate_schematic_outputs.py.*timeout/);
    assert.equal(error.commandEvidence.terminationConfirmed, false);
    assert.deepEqual(error.commandEvidence.termination, { status: 'unknown' });
    return true;
  });
});
