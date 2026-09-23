/**
 * P0-A guard-mount verification (handoff P0-A: "验证 guard API 在当前 profile
 * 内能挂载并拒绝受限路径").
 *
 * HONESTY BOUNDARY — read before trusting a green run:
 * `fakeCtx` below is a MIRROR of the host's tool pipeline, not the host. It
 * implements the two stages the real registry documents
 * (`dsh-tools/lib/types/index.js`: pre-execute waterfall, then a monotonic
 * guard stage where the first string wins and no guard can force-allow) and the
 * disposer contract of `tools.guard()`. What this file proves:
 *   1. `lib/policy.js` denies the restricted paths when reached through a
 *      guard-shaped stage, and the executing callback is never invoked;
 *   2. the denial is monotonic — a later force-allow cannot overturn it;
 *   3. the plugin's CURRENT registration shape (recorded below);
 *   4. mounting through the guard stage is possible with the API as verified.
 * What it does NOT prove: that the real host pipeline behaves identically.
 * That needs a host whose workspaceRoot is this checkout — see the P0-A
 * host-bound verification item.
 */
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import test, { after } from 'node:test';
import { apply } from '../lib/index.js';
import { decision } from '../lib/policy.js';

// ── minimal synthetic workspace ─────────────────────────────────────────────

const ws = fs.realpathSync.native(fs.mkdtempSync(path.join(os.tmpdir(), 'ptc-guard-')));
const P = (...parts) => path.join(ws, ...parts);
const put = (rel) => {
  fs.mkdirSync(path.dirname(P(rel)), { recursive: true });
  fs.writeFileSync(P(rel), 'synthetic\n');
};
put('project/DALI/Input_GlobalMaterial/Dali_testmode.xlsx');
put('project/DALI/Output_Global_Material/dft/TM106/dft-meta.json');
put('project/DALI/Output_Global_Material/dft/TM110/dft-meta.json');
put('outside/secret/dft-meta.json');

const dftAgent = {
  session: {
    header: { cwd: ws },
    events: [{ type: 'subagent/descriptor', data: { label: 'PTC dft expert [TM106]' } }],
  },
};
const call = (name, args, agent = dftAgent) => ({ name, arguments: args, agent });
const ownOutput = () => P('project/DALI/Output_Global_Material/dft/TM106/dft-meta.json');
const otherOutput = () => P('project/DALI/Output_Global_Material/dft/TM110/dft-meta.json');
const outside = () => P('outside/secret/dft-meta.json');

// ── mirror of the host pipeline ─────────────────────────────────────────────

function fakeCtx() {
  const preExecute = [];
  const guards = [];
  return {
    logger: { info() {}, warn() {}, error() {} },
    subagents: { getProvider: () => undefined },
    on(name, fn, options) {
      if (name === 'tools/pre-execute') preExecute.push({ fn, prepend: options?.prepend === true });
      return () => {};
    },
    tools: {
      guard(fn) {
        guards.push(fn);
        return () => {
          const at = guards.indexOf(fn);
          if (at >= 0) guards.splice(at, 1);
        };
      },
    },
    guardCount: () => guards.length,
    /** Pre-execute waterfall (prepended first) then the monotonic guard stage. */
    runToolCall(exec, onExecute) {
      const ordered = [
        ...preExecute.filter((entry) => entry.prepend),
        ...preExecute.filter((entry) => !entry.prepend),
      ];
      for (const entry of ordered) {
        const outcome = entry.fn(exec, () => ({ kind: 'allow' }));
        if (outcome && outcome.kind === 'deny') return outcome;
      }
      for (const guard of guards) {
        const reason = guard(exec);
        if (typeof reason === 'string' && reason !== '') return { kind: 'deny', reason };
      }
      onExecute?.();
      return { kind: 'allow' };
    },
  };
}

const mount = () => {
  const ctx = fakeCtx();
  apply(ctx, { workspaceRoot: ws });
  return ctx;
};

// ── the recorded registration shape ────────────────────────────────────────

test('RECORDED: the plugin mounts its boundary through BOTH tools/pre-execute and one monotonic guard', () => {
  // Deliberate change detector, updated in the same commit that adopted the
  // guard (handoff P0 item 6). If a future change drops the guard, this fails.
  const ctx = mount();
  assert.equal(ctx.guardCount(), 1, 'the boundary must also be registered as a monotonic guard');
});

test('the mounted boundary denies a restricted path and never runs the call', () => {
  const ctx = mount();
  let executed = false;
  const denied = ctx.runToolCall(call('read', { file_path: otherOutput() }), () => { executed = true; });
  assert.equal(denied.kind, 'deny');
  assert.match(denied.reason, /PTC material boundary/);
  assert.equal(executed, false, 'a denied call must not reach execution');

  let allowedExecuted = false;
  const allowed = ctx.runToolCall(call('read', { file_path: ownOutput() }), () => { allowedExecuted = true; });
  assert.equal(allowed.kind, 'allow');
  assert.equal(allowedExecuted, true);
});

test('the mounted boundary denies a path outside the material root entirely', () => {
  const ctx = mount();
  const denied = ctx.runToolCall(call('read', { file_path: outside() }));
  assert.equal(denied.kind, 'deny');
  assert.match(denied.reason, /PTC material boundary/);
});

// ── the guard-shaped route ─────────────────────────────────────────────────

test('the same policy mounted through tools.guard() denies, and the denial is monotonic', () => {
  const ctx = mount();
  const base = ctx.guardCount();
  const dispose = ctx.tools.guard((exec) => decision(exec, ws));
  assert.equal(ctx.guardCount(), base + 1);

  const denied = ctx.runToolCall(call('read', { file_path: otherOutput() }));
  assert.equal(denied.kind, 'deny');
  assert.match(denied.reason, /PTC material boundary/);

  // A second guard that tries to force-allow cannot overturn the first denial:
  // stage order is first-denial-wins and force-allow is not a thing.
  const disposeAllow = ctx.tools.guard(() => undefined);
  assert.equal(ctx.guardCount(), base + 2);
  const stillDenied = ctx.runToolCall(call('read', { file_path: outside() }));
  assert.equal(stillDenied.kind, 'deny');

  // The guard stays silent on permitted paths, so it does not break them.
  assert.equal(ctx.runToolCall(call('read', { file_path: ownOutput() })).kind, 'allow');

  dispose();
  assert.equal(ctx.guardCount(), base + 1, 'the disposer must remove exactly its own guard');
  disposeAllow();
  assert.equal(ctx.guardCount(), base);
});

test('a guard that always denies wins over every allow, including on permitted paths', () => {
  const ctx = mount();
  ctx.tools.guard(() => 'unconditional test denial');
  const denied = ctx.runToolCall(call('read', { file_path: ownOutput() }));
  assert.equal(denied.kind, 'deny');
  assert.equal(denied.reason, 'unconditional test denial');
});

after(() => {
  fs.rmSync(ws, { recursive: true, force: true });
});
