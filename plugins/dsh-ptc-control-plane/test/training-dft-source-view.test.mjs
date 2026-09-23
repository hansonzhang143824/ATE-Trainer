import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import test from 'node:test';

const repo = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../../..');
const hash = (bytes) => crypto.createHash('sha256').update(bytes).digest('hex');
// Technical parser fixtures only: not user workbooks, never read production XLSX.
const fixtureProgram = `import json, pathlib, sys
from openpyxl import Workbook
sys.path.insert(0, str(pathlib.Path(sys.argv[1]) / 'scripts'))
from material_plaintext_hash import sha256_plaintext
root = pathlib.Path(sys.argv[1])
mode = sys.argv[2]
digests = {}
for run_id in ['run-one', 'run-two']:
 book = Workbook()
 sheet = book.active
 sheet.title = 'OVERVIEW'
 sheet.append(['Item', 'Condition', 'Value', 'Comment'])
 sheet.append(['TM108', 'setup', 0, None])
 sheet.append(['TM109', 'VSET 1.25', 1.25, '=C3*2'])
 sheet.append(['TM110', 'shutdown', False, None])
 sheet.merge_cells('B1:C1')
 if mode == 'duplicate': sheet.append(['TM109', 'conflicting row'])
 if mode == 'large':
  for col in range(5, 15): sheet.cell(3, col, 'x' * 20000)
 target = root / 'Training_Materials' / 'runs' / run_id / 'input' / 'Dali_testmode.xlsx'
 book.save(target)
 digests[run_id] = sha256_plaintext(target)
print(json.dumps(digests))`;

function python(args, cwd) {
  const result = spawnSync('python', ['-X', 'utf8', ...args], {
    cwd, encoding: 'utf8', timeout: 30000, maxBuffer: 512 * 1024, windowsHide: true,
  });
  assert.equal(result.error, undefined, `Python execution failed: ${result.error?.message}`);
  return result;
}

function fixture(t, mode = 'normal') {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'ptc-source-view-'));
  t.after(() => fs.rmSync(root, { recursive: true, force: true }));
  fs.mkdirSync(path.join(root, 'scripts'));
  for (const name of ['training_dft_source_view.py', 'material_plaintext_hash.py']) {
    fs.copyFileSync(path.join(repo, 'scripts', name), path.join(root, 'scripts', name));
  }
  for (const runId of ['run-one', 'run-two']) {
    fs.mkdirSync(path.join(root, 'Training_Materials/runs', runId, 'input'), { recursive: true });
  }
  const generated = python(['-c', fixtureProgram, root, mode], root);
  assert.equal(generated.status, 0, generated.stderr);
  const digests = JSON.parse(generated.stdout);
  for (const runId of ['run-one', 'run-two']) {
    const runRoot = `Training_Materials/runs/${runId}`;
    const files = [{ source: 'Training_Materials/Input_GlobalMaterial/Dali_testmode.xlsx',
      path: `${runRoot}/input/Dali_testmode.xlsx`, sha256: digests[runId], view: 'python-plaintext' }];
    const policies = [{ path: 'scripts/dft_source.py', sha256: 'a'.repeat(64) }];
    const cacheKey = hash(Buffer.from(JSON.stringify({ materials: files.map(({ source, sha256 }) => ({ source, sha256 })), policies })));
    fs.writeFileSync(path.join(root, runRoot, 'run.json'), JSON.stringify({ schemaVersion: 1, runId, mode: 'training',
      profileSource: 'draft', orchestrationSource: 'draft', artifactRoot: runRoot, releaseId: null }));
    fs.writeFileSync(path.join(root, runRoot, 'material-manifest.json'), JSON.stringify({ schemaVersion: 2,
      runId, testItems: ['TM109', 'TM110', 'TM999'], files, policies, cacheKey }));
  }
  return root;
}

function invoke(root, runId = 'run-one', tms = ['TM109']) {
  const result = python([path.join(root, 'scripts/training_dft_source_view.py'), '--run-id', runId,
    ...tms.flatMap((tm) => ['--tm', tm])], root);
  assert.ok(result.stdout.trim(), result.stderr);
  return { ...result, report: JSON.parse(result.stdout) };
}

function output(root, runId = 'run-one') {
  return path.join(root, 'Training_Materials/runs', runId, 'input/dft-source-view.json');
}

test('source view preserves raw coordinates, header, formula/type and merged ranges; identical reentry reuses bytes', (t) => {
  const root = fixture(t);
  const first = invoke(root);
  assert.equal(first.status, 0, first.stdout);
  assert.equal(first.report.status, 'SOURCE_VIEW');
  assert.equal(first.report.reused, false);
  const bytes = fs.readFileSync(output(root));
  assert.equal(hash(bytes), first.report.sha256);
  const view = JSON.parse(bytes);
  assert.equal(view.kind, 'ptc-dft-source-view');
  assert.equal(view.source.sha256, first.report.sourceSha256);
  const item = view.items[0];
  assert.equal(item.matchedRow, 3);
  assert.deepEqual(item.headerRows, [1]);
  assert.deepEqual(item.mergedRanges, ['B1:C1']);
  const cells = item.rows.find((row) => row.row === 3).cells;
  assert.deepEqual(cells[2], { coordinate: 'C3', value: 1.25, dataType: 'n', valueType: 'float', numberFormat: 'General' });
  assert.equal(cells[3].value, '=C3*2');
  assert.equal(cells[3].dataType, 'f');
  const before = fs.statSync(output(root)).mtimeMs;
  const second = invoke(root);
  assert.equal(second.status, 0, second.stdout);
  assert.equal(second.report.reused, true);
  assert.equal(fs.statSync(output(root)).mtimeMs, before);
  assert.deepEqual(fs.readFileSync(output(root)), bytes);
});

test('same TM in separate runs remains private; existing different view is never overwritten', (t) => {
  const root = fixture(t);
  assert.equal(invoke(root).status, 0);
  assert.equal(invoke(root, 'run-two').status, 0);
  const second = fs.readFileSync(output(root, 'run-two'));
  fs.writeFileSync(output(root), 'existing snapshot must survive');
  const blocked = invoke(root);
  assert.equal(blocked.status, 2);
  assert.match(blocked.report.reason, /not overwritten/);
  assert.equal(fs.readFileSync(output(root), 'utf8'), 'existing snapshot must survive');
  assert.deepEqual(fs.readFileSync(output(root, 'run-two')), second);
});

test('tampered workbook, mismatched run identity, traversal and missing TM all block without writing', (t) => {
  const root = fixture(t);
  const missing = invoke(root, 'run-one', ['TM999']);
  assert.equal(missing.status, 2);
  assert.match(missing.report.reason, /missing/);
  assert.equal(fs.existsSync(output(root)), false);
  const traversal = invoke(root, '../run-one');
  assert.equal(traversal.status, 2);
  assert.match(traversal.report.reason, /unsafe run id/);
  fs.appendFileSync(path.join(root, 'Training_Materials/runs/run-one/input/Dali_testmode.xlsx'), 'tampered');
  const changed = invoke(root);
  assert.equal(changed.status, 2);
  assert.match(changed.report.reason, /hash mismatch/);
  assert.equal(fs.existsSync(output(root)), false);
  const runFile = path.join(root, 'Training_Materials/runs/run-two/run.json');
  const context = JSON.parse(fs.readFileSync(runFile, 'utf8'));
  context.runId = 'run-one';
  fs.writeFileSync(runFile, JSON.stringify(context));
  assert.match(invoke(root, 'run-two').report.reason, /identity/);
});

test('duplicate TM rows and oversized source content block rather than truncate or pick one', (t) => {
  const duplicate = fixture(t, 'duplicate');
  const ambiguous = invoke(duplicate);
  assert.equal(ambiguous.status, 2);
  assert.match(ambiguous.report.reason, /ambiguous/);
  assert.equal(fs.existsSync(output(duplicate)), false);
  const large = fixture(t, 'large');
  const oversized = invoke(large);
  assert.equal(oversized.status, 2);
  assert.match(oversized.report.reason, /128 KiB/);
  assert.equal(fs.existsSync(output(large)), false);
});
