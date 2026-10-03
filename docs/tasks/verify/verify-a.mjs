#!/usr/bin/env node
// 任务 A 验收脚本（Claude 编写）。在仓库根目录运行：
//   node docs/tasks/verify/verify-a.mjs              只读检查（安全）
//   node docs/tasks/verify/verify-a.mjs --mutate     额外执行「绕过页面」的服务端强校验测试（被正确拒绝时不会写入任何数据）
//   node docs/tasks/verify/verify-a.mjs --smoke      额外跑一次「新工作流 1」SMOKE_ONLY（约 1~2 分钟）
// 可选环境变量：TRAINER_BASE（默认 http://127.0.0.1:3080）、TRAINER_ROOT（默认当前目录）、SMOKE_WORKFLOW（工作流名或 ID）
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { execFileSync } from 'node:child_process';
import { randomUUID } from 'node:crypto';
import { BASE, ROOT, PROJECT_DIR, LEDGER, api, must, context, assets, parseLedger, walk, rel, readJson, validId,
  requestId, pass, fail, skip, warn, check, summary, assert, args } from './lib.mjs';

console.log(`任务 A 验收 · ${BASE} · 仓库 ${ROOT}\n`);

// ---------- A-1 页面静态检查 ----------
await check('A-page-1 页面可访问且脚本语法正确', async () => {
  const html = await (await fetch(`${BASE}/agent-trainer`)).text();
  const scripts = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => m[1]).join('\n');
  globalThis.__pageScript = scripts;
  assert(scripts.length > 1000, '未找到内联脚本');
  const tmp = path.join(os.tmpdir(), `trainer-page-${Date.now()}.js`);
  fs.writeFileSync(tmp, scripts);
  try { execFileSync(process.execPath, ['--check', tmp], { stdio: 'pipe' }); } catch (e) { throw new Error(`node --check 失败：${String(e.stderr || e.message).slice(0, 300)}`); } finally { fs.rmSync(tmp, { force: true }); }
  globalThis.__pageScript = scripts;
});
const page = globalThis.__pageScript || '';
await check('A-page-2 T0 轮询修复仍在（回归）', () => {
  for (const marker of ['LIVE_RUN_POLL_MAX_MS', 'BUSINESS_RUN_POLL_MAX_MS', 'pollLiveRun(', 'pollBusinessRun(']) assert(page.includes(marker), `缺少 ${marker}`);
  for (const old of ['attempt<30', 'attempt<90']) assert(!page.includes(old), `旧逻辑仍在：${old}`);
});
await check('A-page-3 无 window.confirm / alert / prompt', () => {
  const hits = page.match(/(^|[^\w.$])(window\.)?(confirm|alert|prompt)\s*\(/g) || [];
  assert(!hits.length, `发现：${hits.slice(0, 3).join(' | ')}`);
});
await check('A-page-4 已去除 agent-T1~T3 / custom-agent-N 的 ID 分配逻辑', () => {
  assert(!/agents\['agent-T1'\]\?/.test(page), "仍有 agents['agent-T1']? 优先分配逻辑");
  assert(!/`custom-agent-\$\{no\}`/.test(page), '仍有 custom-agent-${no} 分配逻辑');
});
await check('A-page-5 存在删除计划函数 agentDeletionPlan', () => assert(page.includes('agentDeletionPlan'), '未找到 agentDeletionPlan'));

// ---------- A-2 registry 与台账 ----------
let ctx, files, ledger;
await check('A-reg-1 读取训练模式 registry', async () => {
  ctx = await context('training');
  files = (await assets('training', ctx.candidateRevision)).files;
  return `revision ${ctx.candidateRevision} · ${ctx.project.agents.length} 个 Agent · ${ctx.project.workflows.length} 条工作流`;
});
await check('A-reg-2 台账存在且结构合法', () => {
  assert(files && Object.hasOwn(files, LEDGER), `候选中没有 ${LEDGER}`);
  const parsed = parseLedger(files[LEDGER]);
  assert(parsed.ok, `台账损坏：${parsed.why}`);
  ledger = parsed.data;
  return `allocated ${ledger.allocated.length} 个`;
});
await check('A-reg-3 当前全部 Agent 都已登记在台账', () => {
  assert(ledger, '台账不可用');
  const missing = ctx.project.agents.map(a => a.agentId).filter(id => !ledger.allocated.includes(id));
  assert(!missing.length, `未登记：${missing.join(', ')}`);
});
await check('A-reg-4 每个 agent.json 的 agentId 与目录一致、name 为非空字符串', () => {
  const bad = [];
  for (const [p, c] of Object.entries(files || {})) {
    const m = p.match(/^agents\/([^/]+)\/agent\.json$/); if (!m) continue;
    const a = JSON.parse(c);
    if (a.agentId !== m[1] || typeof a.name !== 'string' || !a.name.trim()) bad.push(m[1]);
  }
  assert(!bad.length, `不一致：${bad.join(', ')}`);
});

// ---------- A-3 台账独立复扫（与 Codex 初始化脚本交叉核对） ----------
await check('A-scan-1 独立扫描 4 个来源，台账必须覆盖全部历史 Agent ID', () => {
  assert(ledger, '台账不可用');
  const sources = {
    'projects/agent-trainer/revisions': path.join(PROJECT_DIR, 'revisions'),
    'projects/agent-trainer/versions': path.join(PROJECT_DIR, 'versions'),
    'publish/versions': path.join(ROOT, 'publish/versions'),
    'publish/workflow-templates/versions': path.join(ROOT, 'publish/workflow-templates/versions'),
  };
  const found = new Map(); const counts = {}; const unreadable = [];
  for (const [name, dir] of Object.entries(sources)) {
    let n = 0;
    for (const file of walk(dir)) {
      const r = rel(file);
      const am = r.match(/(?:^|\/)agents\/([^/]+)\/agent\.json$/);
      const wm = /(?:^|\/)workflows\/[^/]+\.json$/.test(r);
      if (!am && !wm) continue;
      const data = readJson(file);
      if (data === undefined) { unreadable.push(r); continue; }
      const ids = am ? (data.agentId === am[1] ? [am[1]] : []) : (Array.isArray(data.steps) ? data.steps.map(s => s?.agentId) : []);
      for (const id of ids) if (validId(id)) { if (!found.has(id)) found.set(id, r); n++; }
    }
    counts[name] = n;
  }
  const missing = [...found.keys()].filter(id => !ledger.allocated.includes(id));
  if (unreadable.length) warn('A-scan-1a 解析失败的文件（已跳过）', unreadable.slice(0, 10).join(', '));
  assert(!missing.length, `台账漏登记 ${missing.length} 个：${missing.slice(0, 10).map(id => `${id}（${found.get(id)}）`).join(', ')}`);
  return `扫描到 ${found.size} 个不同 ID · ${Object.entries(counts).map(([k, v]) => `${k}:${v}`).join(' · ')} · 台账另含 ${ledger.allocated.length - found.size} 个（多登记无害）`;
});

// ---------- A-4 服务端强校验（--mutate） ----------
function agentFiles(id) {
  const input = `contracts/${id}-input.schema.json`, output = `contracts/${id}-output.schema.json`;
  const schema = JSON.stringify({ $schema: 'https://json-schema.org/draft/2020-12/schema', type: 'object', additionalProperties: true }, null, 2) + '\n';
  return [
    { path: `agents/${id}/instructions.md`, content: `verify ${id}\n` },
    { path: `agents/${id}/agent.json`, content: JSON.stringify({ agentId: id, name: `verify ${id}`, instructionsRef: `agents/${id}/instructions.md`, skillRefs: [], toolIds: [], inputSchemaRef: input, outputSchemaRef: output }, null, 2) + '\n' },
    { path: input, content: schema }, { path: output, content: schema },
  ];
}
const ledgerText = list => JSON.stringify({ schemaVersion: 1, allocated: list }, null, 2) + '\n';
async function expectReject(id, changes, code, cleanup) {
  const base = (await context('training')).candidateRevision;
  const r = await api('apply-changes', { requestId: requestId('a'), baseRevision: base, reason: `verify-a ${id}`, changes });
  const after = (await context('training')).candidateRevision;
  if (r.ok) {
    fail(id, `本应被拒绝（${code}），却提交成功并生成 ${r.value?.revisionId}；正在回滚测试数据`);
    try { await cleanup?.(after); } catch (e) { fail(`${id} 回滚`, e.message); }
    return;
  }
  if (after !== base) return fail(id, `请求被拒绝但 revision 变化：${base} → ${after}`);
  if (r.error?.code !== code) return fail(id, `错误码应为 ${code}，实际 ${r.error?.code}：${r.error?.message}`);
  pass(id, `${code}，revision 未变`);
}
if (args.has('--mutate') && ledger) {
  const current = new Set(ctx.project.agents.map(a => a.agentId));
  const reusable = ledger.allocated.find(id => !current.has(id) && !Object.keys(files).some(p => p.startsWith(`agents/${id}/`)));
  const deleteFiles = id => async base => must('apply-changes', { requestId: requestId('cleanup'), baseRevision: base, reason: `verify-a 回滚 ${id}`, changes: agentFiles(id).map(f => ({ path: f.path, content: null })) });
  const restoreLedger = async base => must('apply-changes', { requestId: requestId('cleanup'), baseRevision: base, reason: 'verify-a 回滚台账', changes: [{ path: LEDGER, content: files[LEDGER] }] });
  if (reusable) await expectReject('A-srv-1 复用台账中已有的 ID 新建 Agent', agentFiles(reusable), 'TRAINER_AGENT_ID_REUSED', deleteFiles(reusable));
  else skip('A-srv-1 复用台账中已有的 ID 新建 Agent', '台账中没有「已登记但当前不存在」的 ID（先通过页面新建并删除一个 Agent 再运行）');
  const fresh = `agent-${randomUUID().replace(/-/g, '').slice(0, 8)}`;
  await expectReject('A-srv-2 新建 Agent 但不登记台账', agentFiles(fresh), 'TRAINER_AGENT_ID_UNREGISTERED', deleteFiles(fresh));
  const fresh2 = `agent-${randomUUID().replace(/-/g, '').slice(0, 8)}`, fresh3 = `agent-${randomUUID().replace(/-/g, '').slice(0, 8)}`;
  await expectReject('A-srv-3 一次新建两个 Agent 只登记一个', [...agentFiles(fresh2), ...agentFiles(fresh3), { path: LEDGER, content: ledgerText([...ledger.allocated, fresh2]) }], 'TRAINER_AGENT_ID_UNREGISTERED',
    async base => must('apply-changes', { requestId: requestId('cleanup'), baseRevision: base, reason: 'verify-a 回滚', changes: [...agentFiles(fresh2), ...agentFiles(fresh3)].map(f => ({ path: f.path, content: null })) }));
  await expectReject('A-srv-4 缩小台账', [{ path: LEDGER, content: ledgerText(ledger.allocated.slice(0, -1)) }], 'TRAINER_AGENT_ID_LEDGER_SHRINK', restoreLedger);
  await expectReject('A-srv-5 删除台账文件', [{ path: LEDGER, content: null }], 'TRAINER_AGENT_ID_LEDGER_SHRINK', restoreLedger);
  await expectReject('A-srv-6 提交损坏的台账（schemaVersion 错）', [{ path: LEDGER, content: JSON.stringify({ schemaVersion: 2, allocated: ledger.allocated }) }], 'TRAINER_AGENT_ID_LEDGER_INVALID', restoreLedger);
  await expectReject('A-srv-7 提交损坏的台账（重复 ID）', [{ path: LEDGER, content: ledgerText([...ledger.allocated, ledger.allocated[0]]) }], 'TRAINER_AGENT_ID_LEDGER_INVALID', restoreLedger);
} else if (!args.has('--mutate')) skip('A-srv-* 服务端强校验', '未加 --mutate');

// ---------- A-5 SMOKE 回归（--smoke） ----------
if (args.has('--smoke')) {
  await check('A-smoke-1 「新工作流 1」SMOKE_ONLY 全部步骤 completed', async () => {
    const want = process.env.SMOKE_WORKFLOW || '新工作流 1';
    const wf = (await context('training')).project.workflows.find(w => w.name === want || w.workflowId === want);
    assert(wf, `找不到工作流 ${want}`);
    const started = await must('run', { mode: 'training', targetKind: 'workflow', workflowId: wf.workflowId, targetId: wf.workflowId, executionMode: 'SMOKE_ONLY', requestId: requestId('smoke'), input: { receivedValue: '1+2' } });
    const runId = (started.run || started).runId; assert(runId, '未返回 runId');
    const t0 = Date.now(); let run;
    while (Date.now() - t0 < 10 * 60 * 1000) {
      run = await must('runs', { runId }); run = run.run || run;
      if (['completed', 'failed', 'stopped', 'cancelled', 'interrupted'].includes(String(run.status).toLowerCase())) break;
      await new Promise(r => setTimeout(r, 3000));
    }
    assert(run?.status === 'completed', `运行 ${runId} 状态 ${run?.status}`);
    const bad = (run.steps || []).filter(s => s.status !== 'completed').map(s => `${s.agentId}:${s.status}`);
    assert(!bad.length, `未完成步骤：${bad.join(', ')}`);
    return `${runId} · ${(run.steps || []).length} 步 · ${Math.round((Date.now() - t0) / 1000)}s`;
  });
} else skip('A-smoke-1 SMOKE 回归', '未加 --smoke');

summary(path.join(ROOT, 'docs/tasks/verify/results/verify-a.json'));
