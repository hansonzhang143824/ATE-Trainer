#!/usr/bin/env node
// 任务 B 验收脚本（Claude 编写）。在仓库根目录运行：
//   node docs/tasks/verify/verify-b.mjs snapshot   【B 开工前、改代码前】保存 3 种模式的 context 基线
//   node docs/tasks/verify/verify-b.mjs compare    【B 部署重启后、任何会改数据的测试之前】对比 context 与基线是否一致
//   node docs/tasks/verify/verify-b.mjs            只读检查：构建产物、路由、target-session 记录与绑定文件的结构和不变量
// 会话「打开 / 复用 / 新开」需要 DSH 宿主窗口，无法用脚本完成，由 Claude 在浏览器中验收。
import fs from 'node:fs';
import path from 'node:path';
import { BASE, ROOT, CONTROL_DIR, PROJECT_ID, api, context, assets, readJson, rel, sha256,
  pass, fail, skip, warn, check, summary, assert } from './lib.mjs';

const MODES = ['training', 'engineering', 'published'];
const PRESET = 'agent-trainer';
const RESULTS = path.join(ROOT, 'docs/tasks/verify/results');
const BASELINE = path.join(RESULTS, 'context-baseline.json');
const cmd = process.argv[2] || 'check';
console.log(`任务 B 验收 · ${cmd} · ${BASE} · 仓库 ${ROOT}\n`);

async function snapshotAll() {
  const out = {};
  for (const mode of MODES) {
    const r = await api('context', { mode });
    out[mode] = r.ok ? { ok: true, value: r.value } : { ok: false, error: r.error };
  }
  return out;
}
function diffPaths(a, b, p = '', out = []) {
  if (out.length > 20) return out;
  if (typeof a !== typeof b || Array.isArray(a) !== Array.isArray(b) || a === null || b === null || typeof a !== 'object') {
    if (JSON.stringify(a) !== JSON.stringify(b)) out.push(`${p || '/'}: ${JSON.stringify(a)?.slice(0, 80)} → ${JSON.stringify(b)?.slice(0, 80)}`);
    return out;
  }
  for (const k of new Set([...Object.keys(a), ...Object.keys(b)])) diffPaths(a[k], b[k], `${p}/${k}`, out);
  return out;
}

if (cmd === 'snapshot') {
  const snap = await snapshotAll();
  fs.mkdirSync(RESULTS, { recursive: true });
  fs.writeFileSync(BASELINE, JSON.stringify({ at: new Date().toISOString(), snap }, null, 2));
  for (const m of MODES) (snap[m].ok ? pass : warn)(`B-snap ${m}`, snap[m].ok ? `revision ${snap[m].value.candidateRevision}` : `${snap[m].error?.code} ${snap[m].error?.message}`);
  console.log(`\n基线已保存：${rel(BASELINE)}。请在改代码前完成此步。`);
  summary();
  process.exit();
}

if (cmd === 'compare') {
  const base = readJson(BASELINE);
  if (!base) { fail('B-ctx 基线文件', `未找到 ${rel(BASELINE)}，请先在改代码前运行 snapshot`); summary(); process.exit(); }
  const now = await snapshotAll();
  for (const m of MODES) {
    const d = diffPaths(base.snap[m], now[m]);
    if (d.length) fail(`B-ctx ${m} 模式 context 与改造前一致`, `差异 ${d.length} 处：${d.slice(0, 5).join(' ; ')}`);
    else pass(`B-ctx ${m} 模式 context 与改造前一致`);
  }
  summary(path.join(RESULTS, 'verify-b-compare.json'));
  process.exit();
}

// ---------- 静态检查 ----------
const PLUGIN = path.join(ROOT, 'plugins/dsh-ptc-control-plane');
await check('B-build-1 lib/client.js 已由最新源码构建', () => {
  const src = path.join(PLUGIN, 'client/native-sessions.js'), out = path.join(PLUGIN, 'lib/client.js');
  assert(fs.existsSync(out), 'lib/client.js 不存在');
  assert(fs.statSync(out).mtimeMs >= fs.statSync(src).mtimeMs, 'lib/client.js 比 client/native-sessions.js 旧，需重新运行 scripts/build-client.mjs');
  const text = fs.readFileSync(out, 'utf8');
  for (const marker of ['matchesTarget', 'target-session', 'forget-target-session']) assert(text.includes(marker), `lib/client.js 中没有 ${marker}`);
});
await check('B-build-2 客户端会话键与 matches 不再包含 revision / runId', () => {
  const text = fs.readFileSync(path.join(PLUGIN, 'client/native-sessions.js'), 'utf8');
  const keyArrays = [...text.matchAll(/ptcSessionKey\([\s\S]{0,200}?JSON\.stringify\(\[([\s\S]*?)\]\)/g)].map(m => m[1]);
  assert(keyArrays.length, '未找到 ptcSessionKey(..., JSON.stringify([...])) 调用，无法核对会话键');
  const bad = keyArrays.filter(k => /candidateRevision|selectedRunId/.test(k));
  assert(!bad.length, `会话键仍包含 revision/runId：${bad[0]?.slice(0, 160)}`);
  const m = text.match(/function matchesTarget[\s\S]*?\n\}/) || text.match(/const matchesTarget[\s\S]*?;\n/);
  assert(m, '未找到 matchesTarget');
  assert(!/candidateRevision|selectedRunId/.test(m[0]), 'matchesTarget 中仍比较 candidateRevision / selectedRunId');
});
await check('B-build-3 路由白名单包含两个新 operation', () => {
  const text = fs.readFileSync(path.join(PLUGIN, 'lib/trainer-api.js'), 'utf8');
  for (const op of ['target-session', 'forget-target-session']) assert(text.includes(`'${op}'`), `TRAINER_API_OPERATIONS 缺少 ${op}`);
});
await check('B-build-4 trainer-service.js 中存在 resolveTarget 且被 4 处调用', () => {
  const text = fs.readFileSync(path.join(PLUGIN, 'lib/trainer-service.js'), 'utf8');
  assert(/function resolveTarget|resolveTarget\s*=/.test(text), '未找到 resolveTarget 定义');
  const calls = (text.match(/resolveTarget\(/g) || []).length - 1;
  assert(calls >= 4, `resolveTarget 调用次数 ${calls}，应至少覆盖 context / session-workspace / target-session / open-native-session`);
  return `调用 ${calls} 处`;
});

// ---------- 接口检查 ----------
const identityKeys = ['source', 'revisionId', 'frozenVersionId', 'releaseId'];
const validIdentity = x => x && typeof x === 'object' && ['candidate', 'frozen', 'release'].includes(x.source) && identityKeys.every(k => Object.hasOwn(x, k));
let trainingCtx, engineeringIds = null;
await check('B-api-1 target-session 接口可用', async () => {
  trainingCtx = await context('training');
  const a = trainingCtx.project.agents[0];
  assert(a, '候选中没有 Agent');
  const r = await api('target-session', { mode: 'training', targetKind: 'agent', targetId: a.agentId, presetId: PRESET });
  assert(r.ok, `调用失败：${r.error?.code} ${r.error?.message}`);
});
await check('B-api-2 training 模式各目标的 target-session 记录结构正确', async () => {
  const targets = [...trainingCtx.project.agents.map(a => ['agent', a.agentId]), ...trainingCtx.project.workflows.map(w => ['workflow', w.workflowId])];
  let withRecord = 0;
  for (const [kind, id] of targets) {
    const r = await api('target-session', { mode: 'training', targetKind: kind, targetId: id, presetId: PRESET });
    assert(r.ok, `${kind}/${id}：${r.error?.code} ${r.error?.message}`);
    const v = r.value; if (!v) continue; withRecord++;
    assert(v.targetKind === kind && v.targetId === id && v.mode === 'training' && v.presetId === PRESET, `${kind}/${id} 记录字段不匹配`);
    assert(typeof v.sessionId === 'string' && v.sessionId, `${kind}/${id} 缺少 sessionId`);
    assert(validIdentity(v.lastResolved), `${kind}/${id} lastResolved 结构不正确`);
    assert(v.lastResolved.source === 'candidate', `${kind}/${id} training 模式 lastResolved.source 应为 candidate`);
  }
  return `${targets.length} 个目标，其中 ${withRecord} 个已有会话记录`;
});
await check('B-api-3 engineering 模式：只在候选中的目标不返回会话', async () => {
  const eng = await api('context', { mode: 'engineering' });
  if (!eng.ok) return `engineering context 不可用（${eng.error?.code}），跳过`;
  const engFiles = (await assets('engineering').catch(() => ({ files: {} }))).files || {};
  engineeringIds = new Set(eng.value.project.agents.map(a => a.agentId));
  for (const [p, c] of Object.entries(engFiles)) if (/^workflows\/[^/]+\.json$/.test(p)) { try { for (const s of JSON.parse(c).steps || []) engineeringIds.add(s.agentId); } catch {} }
  const candidateOnly = trainingCtx.project.agents.map(a => a.agentId).filter(id => !engineeringIds.has(id));
  for (const id of candidateOnly) {
    const r = await api('target-session', { mode: 'engineering', targetKind: 'agent', targetId: id, presetId: PRESET });
    assert(r.ok, `${id}：${r.error?.code} ${r.error?.message}`);
    assert(r.value === null, `${id} 只在候选中，engineering 下却返回会话 ${r.value?.sessionId}`);
  }
  return `检查 ${candidateOnly.length} 个只在候选中的 Agent`;
});

// ---------- 磁盘文件检查 ----------
const TS_DIR = path.join(CONTROL_DIR, 'target-sessions'), BIND_DIR = path.join(CONTROL_DIR, 'bindings');
await check('B-file-1 target-sessions 记录：文件名哈希、字段、绑定存在、sessionId 唯一', () => {
  if (!fs.existsSync(TS_DIR)) return '目录尚不存在（还没有打开过会话）';
  const seen = new Map(); const problems = [];
  for (const name of fs.readdirSync(TS_DIR).filter(n => n.endsWith('.json'))) {
    const rec = readJson(path.join(TS_DIR, name));
    if (!rec) { problems.push(`${name} 无法解析`); continue; }
    const expected = sha256(`${rec.projectId}|${rec.mode}|${rec.targetKind}|${rec.targetId}|${rec.presetId}`).slice(0, 32) + '.json';
    if (name !== expected) problems.push(`${name} 文件名与键不符（应为 ${expected}）`);
    if (rec.schemaVersion !== 1 || !rec.sessionId || !rec.createdAt || !rec.updatedAt) problems.push(`${name} 缺少必需字段`);
    if (!validIdentity(rec.lastResolved)) problems.push(`${name} lastResolved 结构不正确`);
    if (!fs.existsSync(path.join(BIND_DIR, `${rec.sessionId}.json`))) problems.push(`${name} 的绑定文件 ${rec.sessionId}.json 不存在`);
    if (seen.has(rec.sessionId)) problems.push(`sessionId ${rec.sessionId} 同时被 ${seen.get(rec.sessionId)} 与 ${name} 使用`);
    seen.set(rec.sessionId, name);
  }
  assert(!problems.length, problems.slice(0, 8).join(' ; '));
  return `${seen.size} 条记录`;
});
await check('B-file-2 bindings 中 pendingContextChange 结构与删除硬规则', () => {
  if (!fs.existsSync(BIND_DIR)) return 'bindings 目录不存在';
  const problems = []; let pending = 0;
  for (const name of fs.readdirSync(BIND_DIR).filter(n => n.endsWith('.json'))) {
    const b = readJson(path.join(BIND_DIR, name)); if (!b?.pendingContextChange) continue; pending++;
    const p = b.pendingContextChange;
    if (!validIdentity(p.from) || !validIdentity(p.to)) { problems.push(`${name} from/to 结构不正确`); continue; }
    if (!Object.hasOwn(p, 'fromRunId') || !Object.hasOwn(p, 'toRunId') || !p.changedAt) problems.push(`${name} 缺少 fromRunId/toRunId/changedAt`);
    const sameSource = identityKeys.every(k => p.from[k] === p.to[k]);
    if (sameSource && (p.fromRunId ?? null) === (p.toRunId ?? null)) problems.push(`${name} 来源与 runId 都相同却未删除`);
  }
  assert(!problems.length, problems.slice(0, 8).join(' ; '));
  return `${pending} 个绑定有未消费的变化`;
});
await check('B-file-3 页面无 window.confirm / alert / prompt', async () => {
  const html = await (await fetch(`${BASE}/agent-trainer`)).text();
  const hits = html.match(/(^|[^\w.$])(window\.)?(confirm|alert|prompt)\s*\(/g) || [];
  assert(!hits.length, `发现：${hits.slice(0, 3).join(' | ')}`);
});

summary(path.join(RESULTS, 'verify-b.json'));
