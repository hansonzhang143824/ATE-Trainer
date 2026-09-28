import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { assertSafeRunPath } from './run-context.js';
import { runHostCommand } from './host-command.js';

const SHA256 = /^[a-f0-9]{64}$/;
const DFT_NAMES = ['dft-meta.json', 'dft-conditions.yaml', 'dft-semantic-review.json'];
const SCHEMATIC_NAMES = [
  'SCH-Connect-Map.txt', 'SCH-Connect-Map.json', 'Component-Statistic.txt',
  'Components-Statistic.json', 'Path-Proofs.txt', 'Path-Proofs.json', 'schematic-receipt.json',
];

function exactPaths(root, actual, relativeDirectory, names) {
  const expected = names.map(name => assertSafeRunPath(root, path.join(root, relativeDirectory, name)));
  if (!Array.isArray(actual) || actual.length !== expected.length
      || actual.some((file, index) => typeof file !== 'string'
        || path.resolve(file) !== expected[index]
        || !fs.statSync(expected[index]).isFile())) {
    throw new Error(`framework source gate returned unexpected ${relativeDirectory} products`);
  }
  return expected;
}

async function gate(root, script, args, expectedRole, expectedGate, expectedDirectory, names, signal, command) {
  const result = await command('python', ['-X', 'utf8', script, ...args], {
    cwd: root, timeoutMs: 30_000, signal,
  });
  if (result.status !== 'passed' || result.exitCode !== 0) {
    const error = new Error(`${result.command ?? script} did not pass: ${result.stopReason ?? result.stderr ?? result.stdout ?? result.exitCode}`);
    error.commandEvidence = { command: result.command ?? `python -X utf8 ${script} ${args.join(' ')}`,
      status: result.status, stopReason: result.stopReason ?? null, exitCode: result.exitCode ?? null,
      terminationConfirmed: result.terminationConfirmed === true,
      treeTerminationConfirmed: result.treeTerminationConfirmed === true,
      termination: result.termination ?? null };
    throw error;
  }
  let report;
  try { report = JSON.parse(result.stdout); }
  catch { throw new Error(`${script} returned invalid JSON`); }
  if (report.role !== expectedRole || report.gate !== expectedGate || report.status !== 'ready'
      || !SHA256.test(report.canonicalInput?.sha256)
      || typeof report.canonicalInput?.path !== 'string'
      || !Array.isArray(report.missingOrStaleOutputs) || report.missingOrStaleOutputs.length !== 0) {
    throw new Error(`${script} did not attest ready source products`);
  }
  const input = assertSafeRunPath(root, report.canonicalInput.path);
  const inputRoot = path.join(root, 'project', 'DALI', 'Input_GlobalMaterial');
  const relativeInput = path.relative(inputRoot, input);
  if (!relativeInput || relativeInput === '..' || relativeInput.startsWith(`..${path.sep}`)
      || path.isAbsolute(relativeInput)) throw new Error('framework source input is outside the approved input directory');
  const files = exactPaths(root, report.requiredOutputs, expectedDirectory, names);
  const fileHashes = files.map(file => ({ path: file,
    sha256: crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex') }));
  return { role: expectedRole, canonicalInput: report.canonicalInput, files, fileHashes, gate: expectedGate };
}

/**
 * Read-only preflight for an explicitly labeled framework rehearsal. Canonical
 * DLP source digests come solely from the approved Python gates; generated
 * product bytes are subsequently snapshotted and hashed by the rehearsal core.
 */
export async function preflightFrameworkRehearsalSources(workspaceRoot, testItems, options = {}) {
  const root = path.resolve(workspaceRoot);
  if (!Array.isArray(testItems) || !testItems.length
      || testItems.some(tm => typeof tm !== 'string' || !/^TM\d+$/.test(tm))
      || new Set(testItems).size !== testItems.length) {
    throw new Error('framework rehearsal requires unique explicit TM identifiers');
  }
  const command = options.runHostCommand ?? runHostCommand;
  const signal = options.signal;
  const schematic = await gate(root, 'scripts/validate_schematic_outputs.py', [], 'schematic-expert',
    'SCHEMATIC_OUTPUT', 'project/DALI/Output_Global_Material/schematic', SCHEMATIC_NAMES, signal, command);
  const dft = [];
  for (const tm of testItems) {
    dft.push({ tm, ...await gate(root, 'scripts/validate_dft_outputs.py', ['--tm', tm], 'dft-expert',
      'DFT_OUTPUT', `project/DALI/Output_Global_Material/dft/${tm}`, DFT_NAMES, signal, command) });
  }
  return { schemaVersion: 1, kind: 'verified-source-products', testItems: [...testItems],
    schematic, dft, verifiedAt: new Date().toISOString() };
}

/** Recheck exact generated-product bytes after the private snapshot copy. */
export function assertFrameworkSourcesUnchanged(workspaceRoot, preflight) {
  const root = path.resolve(workspaceRoot);
  if (preflight?.schemaVersion !== 1 || preflight.kind !== 'verified-source-products'
      || !Array.isArray(preflight.dft) || !preflight.schematic) throw new Error('invalid rehearsal source preflight');
  for (const source of [preflight.schematic, ...preflight.dft]) {
    if (!Array.isArray(source.fileHashes) || source.fileHashes.length !== source.files?.length) {
      throw new Error('rehearsal source digest list is incomplete');
    }
    for (const [index, item] of source.fileHashes.entries()) {
      const file = assertSafeRunPath(root, item.path);
      if (file !== source.files[index] || !SHA256.test(item.sha256)
          || crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex') !== item.sha256) {
        throw new Error(`rehearsal source changed during snapshot: ${item.path}`);
      }
    }
  }
  return true;
}
