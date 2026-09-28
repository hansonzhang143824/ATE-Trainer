import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import test from 'node:test';
import vm from 'node:vm';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');

test('generated client bundle registers the DSH module contract', () => {
  const code = fs.readFileSync(path.join(root, 'lib/client.js'), 'utf8');
  let registration;
  const context = {
    window: { __ModuleLoader__: { load(value) { registration = value; } } },
    console,
    fetch: async () => ({ ok: true, json: async () => ({}) }),
    setInterval() { return 1; },
    clearInterval() {},
  };
  vm.runInNewContext(code, context, { filename: 'lib/client.js' });
  assert.equal(registration.id, 'dsh-ptc-control-plane');
  const client = registration.factory((id) => {
    assert.equal(id, 'react');
    return {
      createElement() {}, useEffect() {}, useState(value) { return [value, () => {}]; }, useSyncExternalStore() {},
    };
  });
  assert.deepEqual(Array.from(client.inject), ['slots', 'locale']);
  assert.equal(typeof client.apply, 'function');
  assert.equal(code.includes('import '), false);
  assert.equal(code.includes('export '), false);
  assert.match(code, /function DraftEditor\(/);
  assert.match(code, /function workflowStatusSummary\(/);
  assert.match(code, /ptc-cp-generic-workflow-template/);
  assert.match(code, /const h = createElement/);
  assert.match(code, /ptc-cp-create-framework-rehearsal/);
  assert.match(code, /framework-releases\/publish/);
  assert.match(code, /framework-rehearsals\/recover/);
  assert.match(code, /framework-releases\/execute/);
  assert.match(code, /framework-releases\/control/);
  assert.match(code, /ptc-cp-start-published-framework/);
  assert.match(code, /ptc-cp-pipeline-model/);
});
