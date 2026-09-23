/**
 * P0-A path-boundary regression suite (handoff rule 3).
 *
 * Everything here runs against a SYNTHETIC workspace built in the OS temp
 * directory, so the suite is host-independent: it needs no real DALI material,
 * no running DSH host, and no sibling repository. The only production code it
 * touches is `lib/policy.js`.
 *
 * Cases the handoff names explicitly: realpath, `..`, junction, symbolic link,
 * case, and `Input` / `Input-old` prefix confusion.
 *
 * A case that cannot be constructed on this machine (Windows file symlinks
 * need privilege) is SKIPPED and reported as skipped — never as a pass.
 */
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import test, { after } from 'node:test';
import { decision } from '../lib/policy.js';

const DENIED = /PTC material boundary/;

// ── synthetic workspace ─────────────────────────────────────────────────────
// realpath the temp dir itself: on Windows TEMP may carry a short (8.3) name
// that would otherwise mismatch every realpath comparison in lib/policy.js.

const ws = fs.realpathSync.native(fs.mkdtempSync(path.join(os.tmpdir(), 'ptc-boundary-')));
const P = (...parts) => path.join(ws, ...parts);
const put = (rel, text = 'synthetic\n') => {
  const full = P(rel);
  fs.mkdirSync(path.dirname(full), { recursive: true });
  fs.writeFileSync(full, text);
  return full;
};

put('project/DALI/Input_GlobalMaterial/Dali_testmode.xlsx');
put('project/DALI/Input_GlobalMaterial/Dali_testmode.xlsx.bak'); // file-level prefix confusion
put('project/DALI/Input_GlobalMaterial-old/Dali_testmode.xlsx'); // directory-level prefix confusion
put('project/DALI/Output_Global_Material/dft/TM106/dft-meta.json');
put('project/DALI/Output_Global_Material/dft/TM106/sub/dft-meta.json'); // for `..` spellings
put('project/DALI/Output_Global_Material/dft/TM106-suffix/dft-meta.json'); // sibling extending the permitted name
put('project/DALI/Output_Global_Material/dft/TM110/dft-meta.json');
put('project/DALI/Output_Global_Material-old/dft/TM106/dft-meta.json'); // sibling of the permitted output root
put('project/DALI/Output_Global_Material/schematic/SCH-Connect-Map.json');
put('project/DALI/ErrorLog/.keep');
put('outside/secret/dft-meta.json');

const linked = {};
const tryLink = (kind, target, linkPath) => {
  try {
    fs.symlinkSync(target, linkPath, kind);
    return true;
  } catch {
    return false;
  }
};
linked.outEscape = tryLink('junction', P('outside/secret'), P('project/DALI/Output_Global_Material/dft/TM106/escape'));
linked.schEscape = tryLink('junction', P('outside/secret'), P('project/DALI/Output_Global_Material/schematic/alias-out'));
linked.leakFile = tryLink('file', P('outside/secret/dft-meta.json'), P('project/DALI/Output_Global_Material/dft/TM106/leak.json'));
linked.aliasIn = tryLink('junction', P('project/DALI/Output_Global_Material/dft/TM110'), P('project/DALI/Output_Global_Material-old/TM110'));

// ── exec/agent doubles mirroring the real shapes ────────────────────────────
// The real runtime hands the guard `{ name, arguments, agent }`, where the agent
// carries its session header (cwd) and the persisted subagent/descriptor event.

const session = (label) => ({
  session: {
    header: { cwd: ws },
    events: [{ type: 'subagent/descriptor', data: { label } }],
  },
});
const dftAgent = session('PTC dft expert [TM106]');
const schematicAgent = session('PTC schematic expert');
const call = (name, args, agent = dftAgent) => ({ name, arguments: args, agent });

const out = (rel) => P('project/DALI/Output_Global_Material/dft', rel);
const sch = (rel) => P('project/DALI/Output_Global_Material/schematic', rel);
const canonical = () => P('project/DALI/Input_GlobalMaterial/Dali_testmode.xlsx');
const allow = (name, args, agent = dftAgent) =>
  assert.equal(decision(call(name, args, agent), ws), undefined, `${name} ${JSON.stringify(args)} should be allowed`);
const deny = (name, args, agent = dftAgent) =>
  assert.match(decision(call(name, args, agent), ws), DENIED, `${name} ${JSON.stringify(args)} should be denied`);

// ── baseline: the permitted set still works ─────────────────────────────────

test('baseline: canonical input and the assigned output folder stay readable', () => {
  allow('read', { file_path: canonical() });
  allow('read', { file_path: out('TM106/dft-meta.json') });
  allow('write', { file_path: out('TM106/dft-semantic-review.json') });
});

test('baseline: a different TM stays denied; schematic products are readable references ([31])', () => {
  deny('read', { file_path: out('TM110/dft-meta.json') });
  // [31] user ruling 2026-09-22: schematic products are reference material for the DFT expert (read-only).
  allow('read', { file_path: sch('SCH-Connect-Map.json') });
});

test('schematic expert keeps only its canonical inputs and its own output', () => {
  allow('read', { file_path: sch('SCH-Connect-Map.json') }, schematicAgent);
  deny('read', { file_path: canonical() }, schematicAgent);
  deny('read', { file_path: out('TM106/dft-meta.json') }, schematicAgent);
});

// ── `..` and spelling normalisation ────────────────────────────────────────

test('dot-segments inside the permitted folder are normalised, not trusted', () => {
  allow('read', { file_path: out('TM106/./dft-meta.json') });
  allow('read', { file_path: out('TM106/sub/../dft-meta.json') });
});

test('parent traversal out of the permitted folder is denied', () => {
  // five `..` from .../dft/TM106 lands on the workspace root, where the decoy lives
  deny('read', { file_path: out('TM106/../../../../../outside/secret/dft-meta.json') });
  deny('read', { file_path: P('project/DALI/Input_GlobalMaterial/../../../outside/secret/dft-meta.json') });
  deny('write', { file_path: out('TM106/../../../ErrorLog/escape.log') });
});

test('the permitted folder itself is not enumerable', () => {
  deny('read', { file_path: out('') });
  deny('read', { file_path: out('TM106/..') });
});

// ── prefix confusion ──────────────────────────────────────────────────────

test('Input / Input-old and TM106 / TM106-suffix prefix confusion is denied', () => {
  deny('read', { file_path: P('project/DALI/Input_GlobalMaterial-old/Dali_testmode.xlsx') });
  deny('read', { file_path: out('TM106-suffix/dft-meta.json') });
});

test('a file whose name extends the canonical input name is denied', () => {
  deny('read', { file_path: P('project/DALI/Input_GlobalMaterial/Dali_testmode.xlsx.bak') });
});

test('a sibling of the permitted output root is denied', () => {
  deny('read', { file_path: P('project/DALI/Output_Global_Material-old/dft/TM106/dft-meta.json') });
});

// ── P0-C: the retired schematic IR is never an input ───────────────────────

test('the retired schematic IR is refused as an input, even when it exists in the output root', () => {
  // The handoff names this case explicitly. The file is created so the refusal is
  // the boundary rule, not a missing-file error.
  put('project/DALI/Output_Global_Material/schematic/schematic-ir.json', '{"retired":true}\n');
  put('project/DALI/schematic-ir.json', '{"retired":true}\n');
  deny('read', { file_path: sch('schematic-ir.json') }, schematicAgent);
  deny('read', { file_path: sch('schematic-ir.json') }, dftAgent);
  deny('write', { file_path: sch('schematic-ir.json') }, schematicAgent);
  deny('read', { file_path: P('project/DALI/schematic-ir.json') }, schematicAgent);
});

test('the schematic expert reads exactly its canonical inputs and writes only its own output', () => {
  for (const name of ['Dali-SCH.csv', 'sch_confirmed.json', 'CBIT表-DALI.xlsx']) {
    put(`project/DALI/Input_GlobalMaterial/${name}`);
    allow('read', { file_path: P('project/DALI/Input_GlobalMaterial', name) }, schematicAgent);
  }
  allow('write', { file_path: sch('schematic-receipt.json') }, schematicAgent);
  deny('read', { file_path: canonical() }, schematicAgent);
  deny('read', { file_path: P('project/DALI/ErrorLog/dft-expert.log') }, schematicAgent);
});

// ── case handling ─────────────────────────────────────────────────────────

test('a case-variant spelling of the real file is the same file (realpath identity, not spelling)', () => {
  allow('read', { file_path: P('PROJECT/DALI/INPUT_GLOBALMATERIAL/DALI_TESTMODE.XLSX') });
});

test('a case-variant spelling cannot smuggle a non-permitted path in', () => {
  deny('read', { file_path: P('PROJECT/DALI/OUTPUT_GLOBAL_MATERIAL/DFT/TM110/dft-meta.json') });
});

// ── junction / symlink escape ─────────────────────────────────────────────

test('junction inside the assigned output folder that escapes outside is denied', (t) => {
  if (!linked.outEscape) return t.skip('cannot create a directory junction on this machine');
  deny('read', { file_path: out('TM106/escape/dft-meta.json') });
  deny('write', { file_path: out('TM106/escape/written.json') });
});

test('junction inside the schematic output folder that escapes outside is denied', (t) => {
  if (!linked.schEscape) return t.skip('cannot create a directory junction on this machine');
  deny('read', { file_path: sch('alias-out/dft-meta.json') }, schematicAgent);
});

test('symlinked file inside the assigned output folder that points outside is denied', (t) => {
  if (!linked.leakFile) return t.skip('cannot create a file symlink on this machine (needs privilege)');
  deny('read', { file_path: out('TM106/leak.json') });
});

test('a junction alias that resolves INTO the permitted set is allowed (realpath decides)', (t) => {
  if (!linked.aliasIn) return t.skip('cannot create a directory junction on this machine');
  const agent = session('PTC dft expert [TM106,TM110]');
  allow('read', { file_path: P('project/DALI/Output_Global_Material-old/TM110/dft-meta.json') }, agent);
});

// ── non-existent targets ──────────────────────────────────────────────────

test('creating a new file inside the assigned output folder is allowed', () => {
  allow('write', { file_path: out('TM106/new-file.json') });
});

test('touching a missing path outside the permitted set is denied', () => {
  deny('read', { file_path: P('outside/secret/missing.json') });
  deny('write', { file_path: P('outside/secret/new.json') });
  deny('write', { file_path: P('project/DALI/meta/new.json') });
});

// ── the child's own result channel ────────────────────────────────────────

test('the result channel is allowed for a boundary-controlled specialist', () => {
  // A pinned dispatch passes an outputSchema, so the child answers through
  // `structured_output`. A real host run showed that denying it made every
  // pinned dispatch end with a boundary error instead of a result.
  for (const name of ['structured_output', 'run_code', 'report']) {
    allow(name, { token: 'ONESHOT-CHILD-OK' });
    allow(name, {}, schematicAgent);
  }
});

test('the result channel exception does not open a material bypass', () => {
  // Everything that is not a declared non-material tool is still denied for a
  // specialist, so the exception above cannot be abused to read or write.
  for (const name of ['glob', 'grep', 'list_agents', 'subagent']) {
    deny(name, { pattern: '**/*' });
  }
});

// ── label spoofing (the identity surface the handoff wants replaced) ───────

test('a label with a trailing space is denied, not silently unscoped', () => {
  deny('read', { file_path: out('TM106/dft-meta.json') }, session('PTC dft expert [TM106] '));
});

test('a multi-TM label authorises exactly the named TMs', () => {
  const agent = session('PTC dft expert [TM106,TM110]');
  allow('read', { file_path: out('TM110/dft-meta.json') }, agent);
  deny('read', { file_path: out('TM425/dft-meta.json') }, agent);
});

test('KNOWN GAP: an unrecognised label receives no boundary at all (fail-open)', () => {
  // Recorded deliberately. A case-varied or otherwise malformed label is not
  // recognised as the DFT expert, so `decision()` returns undefined and every
  // path is allowed. This is the concrete reason the handoff requires
  // descriptor-based identity plus a monotonic guard instead of label guessing.
  const spoofed = session('ptc dft expert [TM106]');
  assert.equal(decision(call('read', { file_path: out('TM110/dft-meta.json') }, spoofed), ws), undefined);
  assert.equal(decision(call('read', { file_path: P('outside/secret/dft-meta.json') }, spoofed), ws), undefined);
});

test('a session outside the workspace root receives no boundary (by design)', () => {
  const foreign = { session: { header: { cwd: path.join(os.tmpdir(), 'ptc-elsewhere') }, events: [] } };
  assert.equal(decision(call('read', { file_path: P('outside/secret/dft-meta.json') }, foreign), ws), undefined);
});

after(() => {
  fs.rmSync(ws, { recursive: true, force: true });
});
