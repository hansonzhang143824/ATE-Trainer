import assert from 'node:assert/strict';
import fs from 'node:fs';
import test from 'node:test';

test('cordis patch uses a package name and the approved workspace', () => {
  const patch = fs.readFileSync(new URL('../cordis.patch.yml', import.meta.url), 'utf8');
  assert.match(patch, /name: dsh-ptc-control-plane/);
  assert.doesNotMatch(patch, /name:\s*(?:\.\/|\.\.\/|[A-Za-z]:[\\/]|file:)/);
  assert.match(patch, /workspaceRoot: D:\/Newtest\/DSH\/ATE-Coding-Flow/);
});
