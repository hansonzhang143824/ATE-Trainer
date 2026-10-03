#!/usr/bin/env node
// 任务 B 宿主窗口验收驱动（Claude 编写，2026-10-02）。在仓库根目录运行：
//
//   node docs/tasks/verify/verify-b-host.mjs --steps A        # 一次只跑一个步骤（推荐）
//   node docs/tasks/verify/verify-b-host.mjs --steps A,B,C,D,E,F
//
// 它启动一个独立的 Chrome（或 Edge），使用临时 profile 与仅限 127.0.0.1 的调试端口，打开真实 DSH 宿主
// http://127.0.0.1:3080/ 与白色工作台 /agent-trainer?nativeHost=<宿主ID>，像用户一样点击页面按钮，
// 然后读取卡片文字、bindings/*.json、target-sessions/*.json 并逐条判定 PASS / FAIL。
// 不删除任何 DSH 会话或 bindings 文件；唯一的删除动作是步骤 F 对 Z 调用 forget-target-session（只删目标映射）。
//
// 步骤与 B 任务书验收条目的对应：
//   A  第 7 条补做（新开后再次打开仍为 S2；S1 仍保留）+ E-2（全新浏览器 profile 中复用）
//   B  第 9 条（W → X → W 交替；另一 Agent Z 得到不同会话）
//   C  第 3 条（运行后再打开，selectedRunId 更新）+ 第 5 条合并规则（两次运行后 fromRunId / toRunId）
//   D  第 4 条（保存候选后再打开，candidateRevision 更新、卡片显示 revision 旧 → 新）
//   E  第 6 条（清掉宿主 localStorage 中 ptc-native-session: 项，刷新宿主与工作台后仍复用 S2）
//   F  第 12 条（旧格式 localStorage key：Z 指向自己的旧会话；新 Agent V 指向别人的会话）
//   G  第 8 条（Z 的固定会话目录临时移出 ~/.dsh/sessions，再打开 Z 应自动新建；结束后移回）。只在明确要求时运行：--steps G
//   K/T/H/I/J1/J2  任务 C1（业务运行加固），见 docs/tasks/C1-business-run-hardening.md：
//      K 旧流水线入口断开与超时上限；T 步骤卡片超时输入；H 超时生效与提示；I 刷新接回；J1 暂停后重启 DSH；J2 重启后已中断
//
// 参数：--steps <列表>  --chrome <浏览器路径>  --port <调试端口，默认 9333>  --headless  --keep-open
//       --x <Agent X，默认 agent-2abe705b>  --workflow <工作流名，默认「新工作流 1」>  --z <Agent Z，默认 agent-70e75253>
//       --foreign-session <F 步骤用作「别人的会话」的 sessionId，默认自动选择已删除 Agent 的会话>
// 环境变量：TRAINER_BASE、TRAINER_ROOT（见 lib.mjs）、CHROME_PATH、DSH_HOME（默认 ~/.dsh）。
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { BASE, ROOT, CONTROL_DIR, PROJECT_DIR, api, must, readJson, rel, sha256, requestId, pass, fail, skip, warn, summary } from './lib.mjs';
import { launchChrome, closeChrome, Page, sleep } from './cdp.mjs';

// ------------------------------------------------------------------ arguments
const argv = process.argv.slice(2);
const opt = (name, fallback) => { const i = argv.indexOf(`--${name}`); return i >= 0 && argv[i + 1] && !argv[i + 1].startsWith('--') ? argv[i + 1] : fallback; };
const flag = name => argv.includes(`--${name}`);
const STEPS = (opt('steps', 'A,B,C,D,E,F')).split(',').map(s => s.trim().toUpperCase()).filter(Boolean);
const X = opt('x', 'agent-2abe705b');
const W_NAME = opt('workflow', process.env.SMOKE_WORKFLOW || '新工作流 1');
const Z = opt('z', 'agent-70e75253');
const PORT = Number(opt('port', '9333'));
const DSH_HOME = process.env.DSH_HOME || path.join(os.homedir(), '.dsh');
const PRESET = 'agent-trainer', PROJECT = 'agent-trainer', MODE = 'training';
const RESULTS = path.join(ROOT, 'docs/tasks/verify/results');
const RUN_TAG = new Date().toISOString().replace(/[:.]/g, '-');
const SHOTS = path.join(RESULTS, 'host-shots', RUN_TAG);
const EVIDENCE_FILE = path.join(RESULTS, 'verify-b-host.json');

// ------------------------------------------------------------------ evidence
const evidence = { at: new Date().toISOString(), base: BASE, root: ROOT, steps: STEPS, runTag: RUN_TAG, pre: {}, data: {}, console: { host: [], trainer: [] } };
const note = (key, value) => { evidence.data[key] = value; };
const short = (v, n = 400) => (typeof v === 'string' ? v : JSON.stringify(v ?? null)).slice(0, n);

// ------------------------------------------------------------------ disk helpers
const targetKey = (kind, id) => sha256(`${PROJECT}|${MODE}|${kind}|${id}|${PRESET}`).slice(0, 32);
const targetPath = (kind, id) => path.join(CONTROL_DIR, 'target-sessions', `${targetKey(kind, id)}.json`);
const bindingPath = sid => path.join(CONTROL_DIR, 'bindings', `${sid}.json`);
function fileInfo(p) {
  try { const text = fs.readFileSync(p, 'utf8'); const st = fs.statSync(p); return { exists: true, path: rel(p), mtimeMs: st.mtimeMs, sha256: sha256(text), json: JSON.parse(text) }; }
  catch { return { exists: false, path: rel(p) }; }
}
const readTarget = (kind, id) => fileInfo(targetPath(kind, id));
const readBinding = sid => fileInfo(bindingPath(sid));
const bindingFields = info => info.exists ? (({ sessionId, targetKind, targetId, bindingRevision, selectedRunId, candidateRevision, previousSessionId, resolved, pendingContextChange }) =>
  ({ sessionId, targetKind, targetId, bindingRevision, selectedRunId, candidateRevision, previousSessionId: previousSessionId ?? null, resolvedRevisionId: resolved?.revisionId ?? null, pendingContextChange: pendingContextChange ?? null, mtimeMs: info.mtimeMs }))(info.json) : { exists: false };
const targetFields = info => info.exists ? (({ sessionId, previousSessionId, createdAt, updatedAt, lastResolved }) =>
  ({ sessionId, previousSessionId: previousSessionId ?? null, createdAt, updatedAt, lastResolvedRevisionId: lastResolved?.revisionId ?? null, mtimeMs: info.mtimeMs }))(info.json) : { exists: false };

function findDshSessionDir(sid) {
  const root = path.join(DSH_HOME, 'sessions');
  const queue = [[root, 0]];
  while (queue.length) {
    const [dir, depth] = queue.shift();
    let entries; try { entries = fs.readdirSync(dir, { withFileTypes: true }); } catch { continue; }
    for (const e of entries) {
      if (!e.isDirectory()) continue;
      const p = path.join(dir, e.name);
      if (e.name.includes(sid)) return p;
      if (depth < 5) queue.push([p, depth + 1]);
    }
  }
  return null;
}
function workspaceJsonHas(sid) {
  const p = path.join(DSH_HOME, 'storages', 'workspace.json');
  try { return { path: p, includes: fs.readFileSync(p, 'utf8').includes(sid) }; } catch (e) { return { path: p, includes: null, error: e.message }; }
}

// ------------------------------------------------------------------ API helpers
const apiTarget = async (kind, id) => must('target-session', { mode: MODE, targetKind: kind, targetId: id, presetId: PRESET });
const trainingContext = async () => must('context', { mode: MODE });
async function activeRuns() {
  const r = await must('runs', {});
  const terminal = new Set(['completed', 'failed', 'stopped', 'cancelled', 'canceled', 'interrupted', 'error']);
  return (r?.runs || []).filter(run => run?.kind === 'framework-run' && run.runId && !terminal.has(String(run.status || '').toLowerCase()));
}
async function workflowIdByName(name) {
  const ctx = await trainingContext();
  const wf = (ctx.project?.workflows || []).find(w => (w.name || w.workflowId) === name) || (ctx.project?.workflows || []).find(w => w.workflowId === name);
  return wf?.workflowId || null;
}

// ------------------------------------------------------------------ result helpers
function expect(id, cond, okDetail, badDetail) { if (cond) pass(id, okDetail); else fail(id, badDetail); return !!cond; }

// ------------------------------------------------------------------ browser session
let browser = null, host = null, trainer = null, hostId = null;
function captureConsole(page, bucket) {
  page.on('Runtime.consoleAPICalled', p => { if (['error', 'warning'].includes(p.type)) bucket.push(`${p.type}: ${(p.args || []).map(a => a.value ?? a.description ?? '').join(' ')}`.slice(0, 400)); if (bucket.length > 80) bucket.shift(); });
  page.on('Runtime.exceptionThrown', p => { bucket.push(`exception: ${p.exceptionDetails?.exception?.description || p.exceptionDetails?.text}`.slice(0, 400)); if (bucket.length > 80) bucket.shift(); });
}
async function waitHostReady(page) {
  await page.waitFor(`!!document.querySelector('[data-testid="ate-trainer-open"]')`, { timeoutMs: 120000, label: 'DSH 宿主页面出现「打开 ATE Trainer」入口（插件已加载）' });
  return page.eval(`new URL(document.querySelector('[data-testid="ate-trainer-open"]').href, location.href).searchParams.get('nativeHost')`);
}
async function waitTrainerReady(page) {
  await page.waitFor(`(()=>{const n=document.querySelector('#side-project-note');return !!n && n.textContent.includes('当前列表来自 Trainer registry') && document.querySelectorAll('button[data-kind="agent"][data-select]').length>0})()`,
    { timeoutMs: 90000, label: '白色工作台加载完 Trainer registry（左侧出现 Agent 列表）' });
}
async function startBrowser() {
  browser = await launchChrome({ chromePath: opt('chrome'), port: PORT, headless: flag('headless') });
  evidence.chrome = { exe: browser.exe, version: browser.version?.Browser, profileDir: browser.profileDir, port: PORT };
  host = await Page.open(PORT, `${BASE}/`);
  captureConsole(host, evidence.console.host);
  hostId = await waitHostReady(host);
  if (!hostId) throw new Error('宿主「打开 ATE Trainer」链接里没有 nativeHost 参数');
  trainer = await Page.open(PORT, `${BASE}/agent-trainer?nativeHost=${hostId}`);
  captureConsole(trainer, evidence.console.trainer);
  await waitTrainerReady(trainer);
  evidence.hostIds = [hostId];
}
async function reloadHostAndTrainer(label) {
  await host.reload();
  const next = await waitHostReady(host);
  if (next !== hostId) { evidence.hostIds.push(next); hostId = next; }
  await trainer.navigate(`${BASE}/agent-trainer?nativeHost=${hostId}`);
  await waitTrainerReady(trainer);
  note(`${label}.reload`, { hostId, at: new Date().toISOString() });
}
async function shots(label) {
  if (!host || !trainer) return {};
  try { await trainer.eval(`(()=>{const c=document.querySelector('#native-session');if(c)c.scrollIntoView({block:'center'});return true})()`); } catch { /* best effort */ }
  return { trainer: rel(await trainer.screenshot(path.join(SHOTS, `${label}-trainer.png`))), host: rel(await host.screenshot(path.join(SHOTS, `${label}-host.png`))) };
}
const hostStorageKeys = () => host.eval(`Object.keys(localStorage).filter(k=>k.startsWith('ptc-native-session:')).sort().map(k=>[k,localStorage.getItem(k)])`);
const newKey = id => `ptc-native-session:agent:${JSON.stringify([PROJECT, MODE, id, PRESET])}`;
const legacyKey = (id, revision) => `ptc-native-session:agent:${JSON.stringify([PROJECT, MODE, id, PRESET, revision || null, null])}`;

async function clickTarget(kind, key) {
  const ok = await trainer.eval(`(()=>{const b=[...document.querySelectorAll('button[data-kind="${kind}"][data-select]')].find(b=>b.dataset.select===${JSON.stringify(key)});if(!b)return false;b.click();return true})()`);
  if (!ok) throw new Error(`工作台左侧找不到${kind === 'agent' ? ' Agent' : '工作流'}「${key}」的按钮`);
}
async function clickId(id) {
  const r = await trainer.eval(`(()=>{const b=document.getElementById(${JSON.stringify(id)});if(!b)return 'missing';if(b.disabled)return 'disabled';b.click();return 'ok'})()`);
  if (r !== 'ok') throw new Error(`按钮 #${id} 无法点击：${r}`);
}

/** Open a target the way a user does (select it, click the open button) and parse the card. */
async function openTarget(kind, key, { fresh = false, label }) {
  const targetId = kind === 'agent' ? key : await workflowIdByName(key);
  await clickTarget(kind, key);
  await sleep(300);
  await trainer.eval(`(()=>{window.__bMeta=[];const m=document.querySelector('#native-session-meta');if(window.__bObs)window.__bObs.disconnect();window.__bObs=new MutationObserver(()=>window.__bMeta.push(m.textContent));window.__bObs.observe(m,{childList:true,characterData:true,subtree:true});return true})()`);
  if (fresh) {
    await clickId('new-native-session');
    await trainer.waitFor(`!!document.getElementById('new-native-confirm')`, { timeoutMs: 10000, label: '出现「确认新开」按钮' });
    await clickId('new-native-confirm');
  } else await clickId(kind === 'agent' ? 'open-agent-session' : 'open-workflow-session');
  await trainer.waitFor(`window.__bMeta.some(t=>t.startsWith('正在请求'))`, { timeoutMs: 20000, label: '卡片进入「正在请求 DSH 宿主打开原生会话」' });
  const meta = await trainer.waitFor(`(()=>{const log=window.__bMeta;const i=log.findIndex(t=>t.startsWith('正在请求'));return log.slice(i+1).find(t=>t.startsWith('已请求 DSH 宿主打开原生会话')||t.startsWith('原生会话打开失败'))||null})()`,
    { timeoutMs: 150000, intervalMs: 500, label: '卡片出现最终结果（已打开或失败）' });
  const body = await trainer.eval(`document.querySelector('#native-session-body').innerText`);
  const result = { label, kind, key, targetId, meta, body: short(body, 1200), ok: meta.startsWith('已请求') };
  if (result.ok) {
    result.sessionId = (body.match(/sessionId:\s*(session-[0-9a-f-]+)/) || [])[1] || null;
    result.reused = body.includes('已复用会话');
    result.replaced = (body.match(/替换\s*(session-[0-9a-f-]+)/) || [])[1] || null;
    result.cardBindingRevision = Number((body.match(/binding revision:\s*(\d+)/) || [])[1] ?? NaN);
    result.contextLine = (body.split('\n').find(l => l.includes('绑定上下文已更新')) || null);
    result.binding = bindingFields(readBinding(result.sessionId));
    result.target = targetFields(readTarget(kind, targetId));
    result.host = await host.eval(`({href:location.href,title:document.title})`);
    result.hostGuarantee = '宿主侧 openPtcSessionView() 在 scope.sessions.list.current !== sessionId 时抛出 OPEN_FAILED；卡片显示「已请求…」说明宿主当前会话就是该 sessionId';
  } else { result.error = body; result.binding = {}; result.target = {}; fail(`${label} 卡片显示打开失败`, short(body.replace(/\s+/g, ' '), 300)); }
  result.shots = await shots(label);
  note(`open.${label}`, result);
  console.log(`  · ${label}: ${result.ok ? `${result.sessionId} ${result.reused ? '已复用' : '新建'}${result.replaced ? `（替换 ${result.replaced}）` : ''} bindingRevision=${result.binding?.bindingRevision}` : `失败：${short(body, 200)}`}`);
  return result;
}

async function runSmokeOnce(label) {
  await clickTarget('workflow', W_NAME);
  await sleep(300);
  await trainer.eval(`(()=>{const b=document.querySelector('button[data-exec="smoke"]');if(b&&!b.classList.contains('active'))b.click();return true})()`);
  const before = await trainer.eval(`document.querySelector('#run-id').textContent`);
  await clickId('run');
  const text = await trainer.waitFor(`(()=>{const t=document.querySelector('#run-id').textContent;const m=t.match(/^(framework-[A-Za-z0-9-]+) · (已完成|失败|已停止)$/);return m&&t!==${JSON.stringify(before)}?t:null})()`,
    { timeoutMs: 15 * 60000, intervalMs: 2000, label: `${label}：SMOKE 运行结束（#run-id 显示 已完成/失败/已停止）` });
  const [, runId, status] = text.match(/^(framework-[A-Za-z0-9-]+) · (.+)$/);
  const apiRun = await must('runs', { runId }).catch(e => ({ error: e.message }));
  const run = apiRun?.run || apiRun;
  note(`run.${label}`, { runId, pageStatus: status, apiStatus: run?.status ?? null, steps: (run?.steps || []).map(s => s.status) });
  console.log(`  · ${label}: ${runId} ${status}`);
  if (status !== '已完成' || run?.status !== 'completed') throw new Error(`${label} 运行未完成：页面 ${status}，接口 ${run?.status ?? short(apiRun)}`);
  return runId;
}

// ------------------------------------------------------------------ preflight (every invocation)
async function preflight() {
  const res = await fetch(`${BASE}/`).catch(e => ({ status: 0, error: e.message }));
  if (res.status !== 200) throw new Error(`DSH 宿主 ${BASE}/ 不可用（HTTP ${res.status} ${res.error || ''}）`);
  for (let waited = 0; ; waited += 15) {
    const active = await activeRuns();
    if (!active.length) break;
    if (waited >= 15 * 60) throw new Error(`有进行中的 framework run 超过 15 分钟：${active.map(r => r.runId).join(', ')}`);
    console.log(`  · 等待进行中的运行结束：${active.map(r => `${r.runId}(${r.status})`).join(', ')}`);
    await sleep(15000);
  }
  const ctx = await trainingContext();
  const agentIds = (ctx.project?.agents || []).map(a => a.agentId);
  const W = await workflowIdByName(W_NAME);
  const recX = await apiTarget('agent', X);
  const recW = W ? await apiTarget('workflow', W) : null;
  const recZ = agentIds.includes(Z) ? await apiTarget('agent', Z) : null;
  evidence.pre = {
    candidateRevision: ctx.candidateRevision, agentCount: agentIds.length, X, W_NAME, W, Z,
    xPresent: agentIds.includes(X), zPresent: agentIds.includes(Z),
    S2: recX?.sessionId ?? null, S1: recX?.previousSessionId ?? null, SW: recW?.sessionId ?? null, SZ: recZ?.sessionId ?? null,
    xTarget: targetFields(readTarget('agent', X)), wTarget: W ? targetFields(readTarget('workflow', W)) : null,
  };
  if (!agentIds.includes(X)) throw new Error(`当前候选中没有 Agent X=${X}`);
  if (!W) throw new Error(`当前候选中没有工作流「${W_NAME}」`);
  if (!recX?.sessionId) throw new Error(`target-session(X=${X}) 为 null：X 当前没有固定会话（与 e630981 时的状态不符，按 B5 计划书第 6 节 6.3 处理）`);
  console.log(`预检：revision ${ctx.candidateRevision} · X=${X} S2=${evidence.pre.S2} S1=${evidence.pre.S1} · W=${W} SW=${evidence.pre.SW} · Z=${Z} SZ=${evidence.pre.SZ}`);
  return evidence.pre;
}

// ------------------------------------------------------------------ steps
async function stepA(pre) {
  console.log('\n[A] 第 7 条补做 + E-2：再次打开 X 应仍为 S2；S1 保留');
  const S2 = pre.S2, S1 = pre.S1;
  const before = readBinding(S2);
  const s1Before = S1 ? readBinding(S1) : null;
  const r = await openTarget('agent', X, { label: 'A-open-X' });
  expect('A-1 B7 再次打开 X：卡片成功', r.ok, r.meta, r.error);
  expect('A-2 B7 再次打开 X 仍为 S2 且显示「已复用会话」', r.sessionId === S2 && r.reused, `${r.sessionId} 已复用`, `得到 ${r.sessionId}，reused=${r.reused}，期望 ${S2} 已复用`);
  expect('A-3 B7 S2 的 bindingRevision 加 1', before.exists && r.binding.bindingRevision === before.json.bindingRevision + 1, `${before.json?.bindingRevision} → ${r.binding.bindingRevision}`, `之前 ${before.json?.bindingRevision}，之后 ${r.binding.bindingRevision}`);
  expect('A-4 B7 target-session(X).sessionId = S2 且 previousSessionId = S1', r.target.sessionId === S2 && (!S1 || r.target.previousSessionId === S1), JSON.stringify(r.target), JSON.stringify(r.target));
  if (S1) {
    const s1After = readBinding(S1);
    const dir = findDshSessionDir(S1), ws = workspaceJsonHas(S1);
    note('A.S1', { S1, bindingBefore: s1Before?.sha256, bindingAfter: s1After.sha256, dshSessionDir: dir, workspaceJson: ws });
    expect('A-5 B7 S1 的 bindings 文件仍在且未被改写', s1After.exists && s1After.sha256 === s1Before.sha256, rel(bindingPath(S1)), `exists=${s1After.exists}`);
    expect('A-6 B7 S1 的 DSH 会话持久化目录仍在（未被删除）', !!dir, dir || '', `在 ${path.join(DSH_HOME, 'sessions')} 下找不到包含 ${S1} 的目录`);
    if (ws.includes === true) pass('A-7 B7 S1 仍登记在 DSH workspace.json 中', ws.path); else warn('A-7 B7 S1 仍登记在 DSH workspace.json 中', `includes=${ws.includes} ${ws.error || ''}（DSH 列表界面隐藏空白会话；以 A-5/A-6 为准）`);
  } else warn('A-5 B7 S1', 'target-session(X) 没有 previousSessionId，无法核对 S1');
  expect('A-8 E-2 宿主当前会话 = S2（openPtcSessionView 保证）', r.ok && r.sessionId === S2, `宿主地址 ${r.host?.href}`, '打开失败');
}

async function stepB(pre) {
  console.log('\n[B] 第 9 条：W → X → W 交替，Z 得到不同会话');
  const W = pre.W;
  const wBefore = pre.SW ? readBinding(pre.SW) : null;
  const t0 = Date.now();
  const r1 = await openTarget('workflow', W_NAME, { label: 'B-open-W-1' });
  const r2 = await openTarget('agent', X, { label: 'B-open-X' });
  const r3 = await openTarget('workflow', W_NAME, { label: 'B-open-W-2' });
  const r4 = await openTarget('agent', Z, { label: 'B-open-Z' });
  const SW = r1.sessionId;
  expect('B-1 B9 四次打开均成功', [r1, r2, r3, r4].every(r => r.ok), 'ok', [r1, r2, r3, r4].filter(r => !r.ok).map(r => `${r.label}: ${short(r.error, 200)}`).join(' | '));
  expect('B-2 B9 两次打开 W 是同一会话 SW，且第二次显示「已复用会话」', SW && r3.sessionId === SW && r3.reused, `SW=${SW}`, `第一次 ${r1.sessionId}，第二次 ${r3.sessionId} reused=${r3.reused}`);
  if (pre.SW) {
    const swDir = findDshSessionDir(pre.SW);
    note('B.oldSW', { SW: pre.SW, dshSessionDir: swDir, binding: bindingFields(readBinding(pre.SW)) });
    if (SW === pre.SW && r1.reused) pass('B-3 B9 SW 等于预检时 W 的固定会话（冷宿主复用旧会话）', SW);
    else warn('B-3 B9 W 没有复用预检时的固定会话', `预检 ${pre.SW}，实际 ${SW} reused=${r1.reused}；旧会话持久化目录=${swDir || '不存在'}（交 Claude 判断，见 B5 计划书 6.6）`);
  } else warn('B-3 B9 预检时 W 没有固定会话', `第一次打开新建 ${SW}`);
  expect('B-4 B9 中间打开 X 仍为 S2', r2.sessionId === pre.S2 && r2.reused, r2.sessionId, `${r2.sessionId} reused=${r2.reused}`);
  expect('B-5 B9 SW ≠ S2', SW && SW !== pre.S2, `${SW} ≠ ${pre.S2}`, `${SW} 与 ${pre.S2}`);
  expect('B-6 B9 Z 的会话与 S2、SW 都不同', r4.sessionId && ![pre.S2, SW].includes(r4.sessionId), r4.sessionId, `${r4.sessionId}`);
  const wt = readTarget('workflow', W);
  expect('B-7 B9 target-session(W) 指向 SW 且本步骤内已更新', wt.exists && wt.json.sessionId === SW && wt.mtimeMs >= t0, JSON.stringify(targetFields(wt)), JSON.stringify(targetFields(wt)));
  if (wBefore?.exists) expect('B-8 B9 SW 的 bindingRevision 本步骤内加 2', r3.binding.bindingRevision === wBefore.json.bindingRevision + 2, `${wBefore.json.bindingRevision} → ${r3.binding.bindingRevision}`, `${wBefore.json.bindingRevision} → ${r3.binding.bindingRevision}`);
  note('B.ids', { S2: pre.S2, SW, SZ: r4.sessionId });
}

async function stepC(pre) {
  console.log('\n[C] 第 3 条：运行后再打开 X；第 5 条合并：两次运行后 fromRunId/toRunId');
  const S2 = pre.S2;
  const r0 = await openTarget('agent', X, { label: 'C-open-X-0' });
  if (!r0.ok || r0.sessionId !== S2) throw new Error(`C 步骤起点：打开 X 未得到 S2（${r0.sessionId} ${short(r0.error, 200)}）`);
  const base = readBinding(S2).json;
  const expectFromRunId = base.pendingContextChange ? base.pendingContextChange.fromRunId : (base.selectedRunId || null);
  const R1 = await runSmokeOnce('C-run-1');
  const r1 = await openTarget('agent', X, { label: 'C-open-X-1' });
  expect('C-1 B3 运行后再打开 X 仍为 S2（已复用）', r1.sessionId === S2 && r1.reused, S2, `${r1.sessionId} reused=${r1.reused}`);
  expect('C-2 B3 bindings/S2.json 的 selectedRunId = 新 runId', r1.binding.selectedRunId === R1, R1, `selectedRunId=${r1.binding.selectedRunId}，期望 ${R1}`);
  expect('C-3 B3 bindingRevision 比运行前大', r1.binding.bindingRevision > base.bindingRevision, `${base.bindingRevision} → ${r1.binding.bindingRevision}`, `${base.bindingRevision} → ${r1.binding.bindingRevision}`);
  expect('C-4 B3 卡片提示 run 变化', !!r1.contextLine && r1.contextLine.includes(R1), r1.contextLine, `卡片：${short(r1.body, 300)}`);
  const R2 = await runSmokeOnce('C-run-2');
  const r2 = await openTarget('agent', X, { label: 'C-open-X-2' });
  const pc = r2.binding.pendingContextChange;
  expect('C-5 B3 第二次运行后再打开 X：selectedRunId = 第二个 runId', r2.sessionId === S2 && r2.binding.selectedRunId === R2, R2, `${r2.sessionId} selectedRunId=${r2.binding.selectedRunId}`);
  expect('C-6 B5 合并：pendingContextChange.fromRunId 保留最早值、toRunId 为最新值', !!pc && pc.fromRunId === expectFromRunId && pc.toRunId === R2,
    `fromRunId=${pc?.fromRunId} toRunId=${pc?.toRunId}`, `pendingContextChange=${JSON.stringify(pc)}，期望 fromRunId=${expectFromRunId} toRunId=${R2}`);
  note('C.ids', { R1, R2, expectFromRunId });
}

async function stepD(pre) {
  console.log('\n[D] 第 4 条：保存候选后再打开 X');
  const S2 = pre.S2;
  // 页面「保存候选」= 在 agents/<X>/instructions.md 末尾补一行固定标记（已存在则内容不变）。为保证可重复执行，
  // 若标记已在，先通过 apply-changes 去掉它（等同于一次普通候选编辑），再用页面按钮保存。
  const MARKER = '# Candidate saved from white Agent Trainer';
  const insPath = `agents/${X}/instructions.md`;
  const rev0 = (await trainingContext()).candidateRevision;
  const files0 = (await must('assets', { mode: MODE, revisionId: rev0 }))?.files || {};
  if (typeof files0[insPath] !== 'string') throw new Error(`候选中没有 ${insPath}，页面「保存候选」无法工作（见 B5 计划书 6.7）`);
  if (files0[insPath].split(/\r?\n/).some(line => line.trim() === MARKER)) {
    const stripped = files0[insPath].split(/\r?\n/).filter(line => line.trim() !== MARKER).join('\n').replace(/\s+$/, '') + '\n';
    await must('apply-changes', { mode: MODE, requestId: requestId('b-host-unmark'), baseRevision: rev0, reason: 'verify-b-host：去掉上次保存标记，便于重复验收第 4 条', changes: [{ path: insPath, content: stripped }] });
    note('D.unmark', { from: rev0, to: (await trainingContext()).candidateRevision });
  }
  await reloadHostAndTrainer('D');  // 让工作台读到最新候选
  const r0 = await openTarget('agent', X, { label: 'D-open-X-0' });
  if (!r0.ok || r0.sessionId !== S2) throw new Error(`D 步骤起点：打开 X 未得到 S2（${r0.sessionId} ${short(r0.error, 200)}）`);
  const revA = (await trainingContext()).candidateRevision;
  expect('D-1 B4 起点：S2 绑定的 candidateRevision = 当前 revision', r0.binding.candidateRevision === revA, revA, `${r0.binding.candidateRevision} ≠ ${revA}`);
  await clickTarget('agent', X);
  await clickId('save');
  let revB = revA;
  for (let i = 0; i < 60 && revB === revA; i++) { await sleep(500); revB = (await trainingContext()).candidateRevision; }
  if (revB === revA) throw new Error('点击「保存候选」后 30 秒内候选 revision 没有变化（看工作台 toast：可能是「当前 Agent 没有可编辑的 instructions.md」或保存失败）');
  const r1 = await openTarget('agent', X, { label: 'D-open-X-1' });
  const current = readJson(path.join(PROJECT_DIR, 'current.json'));
  expect('D-2 B4 保存后再打开 X 仍为 S2（已复用）', r1.sessionId === S2 && r1.reused, S2, `${r1.sessionId} reused=${r1.reused}`);
  expect('D-3 B4 bindings/S2.json 的 candidateRevision = current.json 的 revisionId = 新 revision', r1.binding.candidateRevision === revB && current?.revisionId === revB,
    `${revA} → ${revB}`, `binding ${r1.binding.candidateRevision}，current.json ${current?.revisionId}，接口 ${revB}`);
  expect('D-4 B4 卡片显示 revision 旧 → 新', !!r1.contextLine && r1.contextLine.includes(`revision ${revA} → ${revB}`), r1.contextLine, `卡片：${short(r1.body, 300)}`);
  note('D.ids', { revA, revB, currentJson: current?.revisionId ?? null });
}

async function stepE(pre) {
  console.log('\n[E] 第 6 条：清掉 ptc-native-session: 缓存，刷新宿主与工作台后仍复用 S2');
  const S2 = pre.S2;
  const r0 = await openTarget('agent', X, { label: 'E-open-X-0' });
  if (!r0.ok || r0.sessionId !== S2) throw new Error(`E 步骤起点：打开 X 未得到 S2（${r0.sessionId}）`);
  const before = await hostStorageKeys();
  await host.eval(`(()=>{for(const k of Object.keys(localStorage))if(k.startsWith('ptc-native-session:'))localStorage.removeItem(k);return true})()`);
  const cleared = await hostStorageKeys();
  await reloadHostAndTrainer('E');
  const afterReload = await hostStorageKeys();
  const r = await openTarget('agent', X, { label: 'E-open-X-1' });
  const after = await hostStorageKeys();
  note('E.storage', { before, cleared, afterReload, after });
  expect('E-1 B6 清理前宿主缓存中有 ptc-native-session: 项', before.length > 0, `${before.length} 项`, '清理前就没有缓存项（无法证明清理动作）');
  expect('E-2 B6 清理后为 0 项，刷新后仍为 0 项', cleared.length === 0 && afterReload.length === 0, '0 项', `清理后 ${cleared.length}，刷新后 ${afterReload.length}`);
  expect('E-3 B6 刷新宿主与工作台后打开 X 仍为 S2（已复用）', r.sessionId === S2 && r.reused, S2, `${r.sessionId} reused=${r.reused} ${short(r.error, 200)}`);
  expect('E-4 B6 打开后缓存重新写入 X 的新格式 key = S2', after.some(([k, v]) => k === newKey(X) && v === S2), newKey(X), JSON.stringify(after));
}

async function stepF(pre) {
  console.log('\n[F] 第 12 条：旧格式 localStorage key');
  // (i) Z：服务端无记录，只有旧格式 key 指向 Z 自己的旧会话
  const r0 = await openTarget('agent', Z, { label: 'F-open-Z-0' });
  if (!r0.ok) throw new Error(`F 步骤起点：打开 Z 失败（${short(r0.error, 200)}）`);
  const SZ = r0.sessionId;
  const szBefore = readBinding(SZ);
  const forgot = await must('forget-target-session', { mode: MODE, targetKind: 'agent', targetId: Z, presetId: PRESET });
  const recAfterForget = await apiTarget('agent', Z);
  expect('F-1 B12 forget 后 target-session(Z) = null，映射文件已删，binding 文件仍在', recAfterForget === null && !readTarget('agent', Z).exists && readBinding(SZ).exists,
    JSON.stringify(forgot), `record=${short(recAfterForget)} file=${readTarget('agent', Z).exists}`);
  const rev = (await trainingContext()).candidateRevision;
  await host.eval(`(()=>{localStorage.removeItem(${JSON.stringify(newKey(Z))});localStorage.setItem(${JSON.stringify(legacyKey(Z, rev))},${JSON.stringify(SZ)});return true})()`);
  await reloadHostAndTrainer('F-i');  // 清掉宿主进程内缓存，只留旧格式 key
  const storageZ = await hostStorageKeys();
  const rz = await openTarget('agent', Z, { label: 'F-open-Z-legacy' });
  const tz = readTarget('agent', Z);
  const branch = rz.ok && rz.reused && rz.sessionId === SZ ? 'reuse' : rz.ok && !rz.reused && rz.sessionId !== SZ ? 'new' : 'inconsistent';
  note('F.i', { SZ, legacyKey: legacyKey(Z, rev), storageBeforeOpen: storageZ, branch, result: rz.sessionId, target: targetFields(tz) });
  expect('F-2 B12(i) 只有旧格式 key 时打开 Z：无报错，结果为「复用」或「新建」之一', branch !== 'inconsistent', `分支=${branch === 'reuse' ? '复用旧会话（宿主已加载该会话）' : '新建（宿主未加载旧会话，不满足任务书 2.2 第 3 条复用条件）'}`, `ok=${rz.ok} reused=${rz.reused} sid=${rz.sessionId} ${short(rz.error, 200)}`);
  expect('F-3 B12(i) 服务端补写 target-session(Z)，sessionId 与本次结果一致', tz.exists && tz.json.sessionId === rz.sessionId, JSON.stringify(targetFields(tz)), JSON.stringify(targetFields(tz)));
  expect('F-4 B12(i) Z 旧会话的 bindings 文件仍在', readBinding(SZ).exists, rel(bindingPath(SZ)), '被删除');
  if (branch === 'new') expect('F-5 B12(i) 新建分支未改写旧会话 binding', readBinding(SZ).sha256 === szBefore.sha256, 'sha256 不变', 'sha256 变化');

  // (ii) V：新 Agent，服务端无记录，旧格式 key 指向「别人的会话」F → 必须新建，且不碰 F
  const ctx0 = await trainingContext();
  const ids0 = new Set((ctx0.project?.agents || []).map(a => a.agentId));
  await clickId('add-agent');
  let V = null;
  for (let i = 0; i < 60 && !V; i++) { await sleep(500); const c = await trainingContext(); V = (c.project?.agents || []).map(a => a.agentId).find(id => !ids0.has(id)) || null; }
  if (!V) throw new Error('点击「新建 Agent」后 30 秒内候选中没有出现新 Agent');
  await trainer.waitFor(`!!document.querySelector('button[data-kind="agent"][data-select=${JSON.stringify(V)}]')`, { timeoutMs: 30000, label: `工作台出现新 Agent ${V}` });
  const recV = await apiTarget('agent', V);
  const currentIds = new Set((await trainingContext()).project?.agents?.map(a => a.agentId) || []);
  let F = opt('foreign-session');
  if (!F) {
    for (const name of fs.readdirSync(path.join(CONTROL_DIR, 'bindings'))) {
      const b = readJson(path.join(CONTROL_DIR, 'bindings', name));
      if (b?.presetId === PRESET && b.targetKind === 'agent' && b.sessionId && !currentIds.has(b.targetId)) { F = b.sessionId; break; }
    }
  }
  if (!F) throw new Error('找不到可用作「别人的会话」的 sessionId（用 --foreign-session 指定一个其他目标的会话）');
  const fBefore = readBinding(F);
  const rev2 = (await trainingContext()).candidateRevision;
  await host.eval(`(()=>{localStorage.removeItem(${JSON.stringify(newKey(V))});localStorage.setItem(${JSON.stringify(legacyKey(V, rev2))},${JSON.stringify(F)});return true})()`);
  await reloadHostAndTrainer('F-ii');
  const rv = await openTarget('agent', V, { label: 'F-open-V-legacy-foreign' });
  const tv = readTarget('agent', V);
  const fAfter = readBinding(F);
  note('F.ii', { V, recBefore: recV, F, fBindingTarget: fBefore.json?.targetId, legacyKey: legacyKey(V, rev2), result: rv.sessionId, target: targetFields(tv) });
  expect('F-6 B12(ii) 新 Agent V 打开前服务端无记录', recV === null, 'null', short(recV));
  expect('F-7 B12(ii) 旧 key 指向别人的会话时：新建会话、无报错、不复用 F', rv.ok && !rv.reused && rv.sessionId && rv.sessionId !== F, `${rv.sessionId}（F=${F}）`, `ok=${rv.ok} reused=${rv.reused} sid=${rv.sessionId} ${short(rv.error, 200)}`);
  expect('F-8 B12(ii) target-session(V) 指向新会话', tv.exists && tv.json.sessionId === rv.sessionId, JSON.stringify(targetFields(tv)), JSON.stringify(targetFields(tv)));
  expect('F-9 B12(ii) F 的 bindings 文件未被改写', fAfter.exists && fAfter.sha256 === fBefore.sha256 && fAfter.mtimeMs === fBefore.mtimeMs, rel(bindingPath(F)), `exists=${fAfter.exists} sha 相同=${fAfter.sha256 === fBefore.sha256} mtime 相同=${fAfter.mtimeMs === fBefore.mtimeMs}`);
}

// 第 8 条：目标当前的固定会话在 DSH 中「消失」后再打开 → 必须自动新建、无报错、记录更新为新会话。
// DSH 没有提供删除会话的功能，这里把该会话的持久化目录临时移出 ~/.dsh/sessions（等同于被删除），
// 验证结束后在 finally 中移回原处，不丢数据。前提：DSH 刚重启过，且重启后没有打开过 Z（会话不在内存中）。
async function stepG(pre) {
  console.log('\n[G] 第 8 条：Z 的固定会话被移除后再打开 Z，应自动新建');
  const SZ = pre.SZ;
  if (!SZ) throw new Error(`target-session(Z=${Z}) 为 null，没有可移除的固定会话（先按计划书处理）`);
  const szBinding = readBinding(SZ);
  const from = findDshSessionDir(SZ);
  if (!from) throw new Error(`在 ${path.join(DSH_HOME, 'sessions')} 下找不到 ${SZ} 的会话目录，无法执行第 8 条`);
  const backupRoot = path.join(DSH_HOME, 'b8-removed-sessions', RUN_TAG);
  const to = path.join(backupRoot, path.basename(path.dirname(from)), path.basename(from));
  const manifest = path.join(backupRoot, 'manifest.json');
  fs.mkdirSync(path.dirname(to), { recursive: true });
  fs.writeFileSync(manifest, JSON.stringify({ sessionId: SZ, from, to, movedAt: new Date().toISOString(), restore: `把 ${to} 移回 ${from}` }, null, 2));
  fs.renameSync(from, to);
  note('G.move', { SZ, from, to, manifest });
  let restored = false;
  try {
    expect('G-1 B8 Z 的会话目录已移出 ~/.dsh/sessions（模拟被删除）', !fs.existsSync(from) && fs.existsSync(to), to, `from 仍存在=${fs.existsSync(from)}，to 存在=${fs.existsSync(to)}`);
    const before = await api('target-session', { mode: MODE, targetKind: 'agent', targetId: Z, presetId: PRESET });
    note('G.targetSessionAfterMove', before);
    expect('G-2 B8 移除后查询 target-session(Z)：接口正常返回 null（不报错）', before.ok && before.value === null,
      'null', `ok=${before.ok} value=${short(before.value)} error=${short(before.error)}`);
    const r = await openTarget('agent', Z, { label: 'G-open-Z-after-removal' });
    expect('G-3 B8 再打开 Z：卡片成功、显示「新建会话」、sessionId ≠ 旧会话', r.ok && !r.reused && r.sessionId && r.sessionId !== SZ,
      `${r.sessionId}（旧 ${SZ}）`, r.ok && r.sessionId === SZ ? `仍复用了旧会话 ${SZ}：说明该会话还在 DSH 进程内存里（重启后被打开过）。重启 DSH 后立即重跑 G` : `ok=${r.ok} reused=${r.reused} sid=${r.sessionId} ${short(r.error, 300)}`);
    const t = readTarget('agent', Z);
    expect('G-4 B8 target-session(Z) 更新为新会话', t.exists && t.json.sessionId === r.sessionId && r.sessionId !== SZ, JSON.stringify(targetFields(t)), JSON.stringify(targetFields(t)));
    const szAfter = readBinding(SZ);
    expect('G-5 B8 旧会话的 bindings 文件仍在且未被改写', szAfter.exists && szAfter.sha256 === szBinding.sha256, rel(bindingPath(SZ)), `exists=${szAfter.exists} sha 相同=${szAfter.sha256 === szBinding.sha256}`);
    const r2 = await openTarget('agent', Z, { label: 'G-reopen-Z' });
    expect('G-6 B8 再次打开 Z 复用新会话', r2.ok && r2.reused && r2.sessionId === r.sessionId, r2.sessionId, `ok=${r2.ok} reused=${r2.reused} sid=${r2.sessionId}`);
    note('G.ids', { oldSZ: SZ, newSZ: r.sessionId });
  } finally {
    if (fs.existsSync(from)) fail('G-7 B8 恢复旧会话目录', `原位置 ${from} 已被重新创建，未覆盖；备份在 ${to}，需人工比对后处理`);
    else { fs.renameSync(to, from); restored = true; }
    if (restored) expect('G-7 B8 旧会话目录已移回原处（不丢数据）', fs.existsSync(from) && !fs.existsSync(to), from, `from=${fs.existsSync(from)} to=${fs.existsSync(to)}`);
    note('G.restore', { restored, from, to });
  }
}

// ================================================================== 任务 C1（业务运行加固）
const RUNS_TERMINAL = new Set(['completed', 'failed', 'cancelled', 'interrupted', 'stopped']);
const C1_STATE_FILE = path.join(RESULTS, 'c1-restart-state.json');
async function workflowFile(name) {
  const wid = await workflowIdByName(name);
  const rev = (await trainingContext()).candidateRevision;
  const files = (await must('assets', { mode: MODE, revisionId: rev }))?.files || {};
  const p = `workflows/${wid}.json`;
  if (typeof files[p] !== 'string') throw new Error(`候选中没有 ${p}`);
  return { wid, path: p, rev, text: files[p], json: JSON.parse(files[p]) };
}
async function writeWorkflow(p, json, reason) {
  const rev = (await trainingContext()).candidateRevision;
  return api('apply-changes', { mode: MODE, requestId: requestId('c1'), baseRevision: rev, reason, changes: [{ path: p, content: `${JSON.stringify(json, null, 2)}\n` }] });
}
async function restoreWorkflow(orig, label) {
  const now = await workflowFile(W_NAME);
  if (now.text === orig.text) return true;
  const rev = (await trainingContext()).candidateRevision;
  const r = await api('apply-changes', { mode: MODE, requestId: requestId('c1-restore'), baseRevision: rev, reason: `verify-b-host ${label}：恢复工作流原内容`, changes: [{ path: orig.path, content: orig.text }] });
  const after = await workflowFile(W_NAME);
  note(`${label}.restore`, { ok: r.ok, error: r.error, restored: after.text === orig.text });
  return after.text === orig.text;
}
async function waitRun(runId, { timeoutMs = 15 * 60000, until = run => RUNS_TERMINAL.has(String(run?.status || '').toLowerCase()) } = {}) {
  const deadline = Date.now() + timeoutMs; let run;
  for (;;) {
    const r = await api('runs', { runId }); run = r.value?.run || r.value;
    if (run && until(run)) return run;
    if (Date.now() > deadline) throw new Error(`等待运行 ${runId} 超时，最后状态 ${run?.status}`);
    await sleep(2000);
  }
}
async function startBusinessFromPage(label) {
  await clickTarget('workflow', W_NAME);
  await sleep(300);
  await trainer.eval(`(()=>{const b=document.querySelector('button[data-exec="business"]');if(b&&!b.classList.contains('active'))b.click();return true})()`);
  const before = await trainer.eval(`document.querySelector('#run-id').textContent`);
  await clickId('run');
  const text = await trainer.waitFor(`(()=>{const t=document.querySelector('#run-id').textContent;return /^framework-[A-Za-z0-9-]+ · /.test(t)&&t!==${JSON.stringify(before)}?t:null})()`,
    { timeoutMs: 60000, label: `${label}：页面出现新的业务运行 ID` });
  const runId = text.match(/^(framework-[A-Za-z0-9-]+)/)[1];
  const r = await api('runs', { runId }); const run = r.value?.run || r.value;
  note(`run.${label}.start`, { runId, executionMode: run?.executionMode ?? null, status: run?.status ?? null });
  console.log(`  · ${label}: ${runId}`);
  return runId;
}

async function stepK() {
  console.log('\n[K] C1-1：旧 TM109 业务流水线入口已断开');
  const src = fs.readFileSync(path.join(ROOT, 'docs/prototypes/agent-trainer-repair-prototype.html'), 'utf8');
  expect('K-1 页面「运行」不再分流到旧业务流水线', !src.includes('return runBusinessPipeline()'), '源码中已无 return runBusinessPipeline()', '页面源码仍含 return runBusinessPipeline()');
  const wf = await workflowFile(W_NAME);
  const rev0 = wf.rev;
  const withLegacy = { ...wf.json, businessPipeline: { workflowId: 'tm109-input-sync', workflowRevision: 'r1', testItems: ['TM109'], schematicProfileId: 'schematic-expert', dftProfileId: 'dft-expert' } };
  const r = await writeWorkflow(wf.path, withLegacy, 'verify-b-host K：确认带 businessPipeline 的工作流被拒绝');
  const rev1 = (await trainingContext()).candidateRevision;
  note('K.legacyWrite', { ok: r.ok, error: r.error, rev0, rev1 });
  expect('K-2 保存带 businessPipeline 的工作流被服务端拒绝，候选 revision 不变', !r.ok && rev1 === rev0 && /businessPipeline/.test(JSON.stringify(r.error)),
    short(r.error), `ok=${r.ok} revision ${rev0}→${rev1} error=${short(r.error)}`);
  if (r.ok) await restoreWorkflow(wf, 'K');
  const over = { ...wf.json, steps: wf.json.steps.map((st, i) => i === 0 ? { ...st, timeoutMs: 1800001 } : st) };
  const r2 = await writeWorkflow(wf.path, over, 'verify-b-host K：确认单步超时超过 30 分钟被拒绝');
  const rev2 = (await trainingContext()).candidateRevision;
  note('K.overLimit', { ok: r2.ok, error: r2.error });
  expect('K-3 单步超时 1800001 ms（超过 30 分钟）被服务端拒绝', !r2.ok && rev2 === rev0, short(r2.error), `ok=${r2.ok} error=${short(r2.error)}`);
  if (r2.ok) await restoreWorkflow(wf, 'K');
  const max = { ...wf.json, steps: wf.json.steps.map((st, i) => i === 0 ? { ...st, timeoutMs: 1800000 } : st) };
  const r3 = await writeWorkflow(wf.path, max, 'verify-b-host K：确认单步超时 30 分钟可保存');
  note('K.atLimit', { ok: r3.ok, error: r3.error });
  expect('K-4 单步超时 1800000 ms（30 分钟）可以保存', r3.ok, '已保存', short(r3.error));
  const back = await restoreWorkflow(wf, 'K');
  expect('K-5 工作流已恢复原内容', back, 'ok', '恢复失败，见证据 K.restore');
}

async function stepT() {
  console.log('\n[T] C1-2：步骤卡片上的「超时（分钟）」');
  const orig = await workflowFile(W_NAME);
  try {
    await reloadHostAndTrainer('T');
    await clickTarget('workflow', W_NAME);
    await sleep(500);
    const inputs = await trainer.eval(`[...document.querySelectorAll('input[data-step-timeout]')].map(i=>({index:i.dataset.stepTimeout,value:i.value,min:i.min,max:i.max,disabled:i.disabled}))`);
    note('T.inputs', inputs);
    const expectMinutes = orig.json.steps.map(st => String(Math.round((st.timeoutMs ?? 120000) / 60000)));
    expect('T-1 每个步骤卡片都有超时输入框，显示当前值（分钟），范围 1~30', inputs.length === orig.json.steps.length && inputs.every((x, i) => x.value === expectMinutes[i] && x.min === '1' && x.max === '30' && !x.disabled),
      JSON.stringify(inputs), `输入框 ${JSON.stringify(inputs)}，期望值 ${JSON.stringify(expectMinutes)}`);
    const setValue = async (index, value) => trainer.eval(`(()=>{const i=document.querySelector('input[data-step-timeout="${index}"]');if(!i)return false;i.value=${JSON.stringify(String(value))};i.dispatchEvent(new Event('change',{bubbles:true}));return true})()`);
    await setValue(0, 12);
    let saved = null;
    for (let k = 0; k < 40 && !saved; k++) { await sleep(500); const w = await workflowFile(W_NAME); if (w.json.steps[0]?.timeoutMs === 720000) saved = w; }
    expect('T-2 第 1 步改为 12 分钟后保存为 timeoutMs=720000，其他步骤不变', !!saved && saved.json.steps.slice(1).every((st, i) => (st.timeoutMs ?? null) === (orig.json.steps[i + 1].timeoutMs ?? null)),
      '720000', `保存结果 ${short(saved?.json?.steps?.map(st => st.timeoutMs))}`);
    const revBefore = (await trainingContext()).candidateRevision;
    await setValue(0, 31);
    await sleep(2500);
    const toast = await trainer.eval(`document.querySelector('#toast')?.textContent||''`);
    const revAfter = (await trainingContext()).candidateRevision;
    const shown = await trainer.eval(`document.querySelector('input[data-step-timeout="0"]')?.value`);
    note('T.invalid', { toast, revBefore, revAfter, shown });
    expect('T-3 输入 31 分钟被页面拒绝：提示「超时需为 1~30 分钟」、不保存、输入框恢复为 12', toast.includes('超时需为 1~30 分钟') && revAfter === revBefore && shown === '12', toast, `toast=${toast} revision ${revBefore}→${revAfter} 输入框=${shown}`);
  } finally {
    const back = await restoreWorkflow(orig, 'T');
    expect('T-4 工作流已恢复原内容', back, 'ok', '恢复失败，见证据 T.restore');
  }
}

async function stepH() {
  console.log('\n[H] C1-2：步骤超时真正生效，提示写明是哪一步');
  const orig = await workflowFile(W_NAME);
  const firstStep = orig.json.steps[0];
  try {
    const tiny = { ...orig.json, steps: orig.json.steps.map((st, i) => i === 0 ? { ...st, timeoutMs: 1000 } : st) };
    const w = await writeWorkflow(orig.path, tiny, 'verify-b-host H：第 1 步超时临时设为 1 秒');
    if (!w.ok) throw new Error(`临时设置 1 秒超时失败：${short(w.error)}`);
    await reloadHostAndTrainer('H');
    const runId = await startBusinessFromPage('H-run-timeout');
    const run = await waitRun(runId, { timeoutMs: 5 * 60000 });
    const stepErr = run.steps?.[0]?.error || null;
    note('H.run', { runId, status: run.status, error: run.error ?? null, step0: { status: run.steps?.[0]?.status, error: stepErr } });
    expect('H-1 运行以 failed 结束，错误码 STEP_TIMEOUT', run.status === 'failed' && run.error?.code === 'STEP_TIMEOUT', `${run.status} ${run.error?.code}`, `${run.status} ${short(run.error)}`);
    expect('H-2 错误信息写明第几步、stepId、agentId 和超时时长', new RegExp(`第 1 步 ${firstStep.stepId}（${firstStep.agentId}）超过\\s*\\S.*未完成`).test(run.error?.message || ''),
      run.error?.message, `message=${run.error?.message}`);
    const pageErr = await trainer.waitFor(`document.querySelector('#run-error')?.textContent.includes(${JSON.stringify(firstStep.stepId)})?document.querySelector('#run-error').textContent:null`, { timeoutMs: 30000, label: '#run-error 显示超时信息' }).catch(e => e.message);
    const runEnabled = await trainer.eval(`!document.querySelector('#run').disabled`);
    note('H.page', { pageErr, runEnabled });
    expect('H-3 页面 #run-error 显示该超时信息', typeof pageErr === 'string' && pageErr.includes(firstStep.stepId) && !pageErr.startsWith('等待超时'), pageErr, pageErr);
    expect('H-4 超时后「运行」按钮可再次点击（不被挡住）', runEnabled === true, 'enabled', 'disabled');
  } finally {
    const back = await restoreWorkflow(orig, 'H');
    expect('H-5 工作流已恢复原内容', back, 'ok', '恢复失败，见证据 H.restore');
  }
}

async function stepI() {
  console.log('\n[I] C1-4：业务运行进行中刷新页面，能接回');
  await reloadHostAndTrainer('I');
  const runId = await startBusinessFromPage('I-run');
  const first = (await api('runs', { runId })).value;
  await trainer.reload();
  await waitTrainerReady(trainer);
  const resumed = await trainer.waitFor(`(()=>{const t=document.querySelector('#run-id').textContent;return t.startsWith(${JSON.stringify(runId)})?t:null})()`, { timeoutMs: 30000, label: '刷新后 #run-id 显示同一运行' }).catch(e => e.message);
  const blocked = await trainer.eval(`document.querySelector('#run').disabled`);
  const run = await waitRun(runId);
  const finalText = await trainer.waitFor(`(()=>{const t=document.querySelector('#run-id').textContent;return t.startsWith(${JSON.stringify(runId)})&&/ · (已完成|失败|已停止)$/.test(t)?t:null})()`, { timeoutMs: 60000, label: '刷新后页面跟到运行结束' }).catch(e => e.message);
  note('I', { runId, statusAtReload: (first?.run || first)?.status, resumed, blockedWhileRunning: blocked, apiFinal: run.status, finalText, executionMode: run.executionMode });
  expect('I-1 页面发起的是新框架 BUSINESS_ONLY 运行', run.executionMode === 'BUSINESS_ONLY', run.executionMode, `executionMode=${run.executionMode}`);
  expect('I-2 刷新后页面自动接回同一运行', typeof resumed === 'string' && resumed.startsWith(runId), resumed, resumed);
  expect('I-3 接回期间「运行」按钮处于禁用（防止重复运行）', run.status !== 'completed' || blocked === true || /已完成/.test(String(resumed)), `disabled=${blocked}`, `disabled=${blocked}`);
  expect('I-4 页面跟到运行结束，且与接口状态一致', run.status === 'completed' && typeof finalText === 'string' && finalText.endsWith('已完成'), finalText, `api=${run.status} page=${finalText}`);
}

async function stepJ1() {
  console.log('\n[J1] C1-5（第一段）：发起业务运行并暂停，等待重启 DSH');
  await reloadHostAndTrainer('J1');
  const runId = await startBusinessFromPage('J1-run');
  const c = await api('control', { mode: MODE, runId, action: 'pause', requestId: requestId('J1-pause') });
  let run;
  try { run = await waitRun(runId, { timeoutMs: 5 * 60000, until: r => ['paused', ...RUNS_TERMINAL].includes(String(r?.status)) }); } catch (e) { run = { status: e.message }; }
  note('J1', { runId, control: c, status: run.status });
  expect('J1-1 运行进入 paused（非终态，模拟「DSH 重启时运行未结束」）', run.status === 'paused', run.status, `状态=${run.status} control=${short(c)}`);
  fs.mkdirSync(RESULTS, { recursive: true });
  fs.writeFileSync(C1_STATE_FILE, JSON.stringify({ runId, pausedAt: new Date().toISOString() }, null, 2));
  console.log(`  · 已记录 ${rel(C1_STATE_FILE)}。现在重启 DSH，然后运行 --steps J2`);
}

async function stepJ2() {
  console.log('\n[J2] C1-5（第二段）：DSH 重启后，未结束的运行被标为已中断，页面不被挡住');
  const st = readJson(C1_STATE_FILE);
  if (!st?.runId) throw new Error(`找不到 ${rel(C1_STATE_FILE)}，请先运行 --steps J1 并重启 DSH`);
  const run = (await api('runs', { runId: st.runId })).value;
  const r = run?.run || run;
  note('J2.run', { runId: st.runId, status: r?.status, error: r?.error ?? null });
  expect('J2-1 重启后该运行为 interrupted，错误码 HOST_RESTARTED', r?.status === 'interrupted' && r?.error?.code === 'HOST_RESTARTED', `${r?.status} ${r?.error?.code}`, `${r?.status} ${short(r?.error)}`);
  await clickTarget('workflow', W_NAME);
  await sleep(1500);
  const runEnabled = await trainer.eval(`!document.querySelector('#run').disabled`);
  const runText = await trainer.eval(`document.querySelector('#run-id').textContent`);
  note('J2.page', { runEnabled, runText });
  expect('J2-2 页面没有接回已中断的运行，「运行」按钮可用', runEnabled === true && !runText.startsWith(st.runId + ' · 运行中'), `enabled，#run-id=${runText}`, `enabled=${runEnabled} #run-id=${runText}`);
  const newId = await startBusinessFromPage('J2-rerun');
  const nr = await waitRun(newId);
  expect('J2-3 重新发起的业务运行正常完成', nr.status === 'completed', `${newId} completed`, `${newId} ${nr.status}`);
}

// ------------------------------------------------------------------ main
const STEP_FNS = { A: stepA, B: stepB, C: stepC, D: stepD, E: stepE, F: stepF, G: stepG, K: stepK, T: stepT, H: stepH, I: stepI, J1: stepJ1, J2: stepJ2 };
console.log(`任务 B 宿主验收 · ${BASE} · 仓库 ${ROOT} · 步骤 ${STEPS.join(',')}\n`);
let fatal = null;
try {
  const pre = await preflight();
  pass('P-0 预检：DSH 可用、无进行中运行、X 有固定会话', `S2=${pre.S2}`);
  await startBrowser();
  pass('P-1 独立浏览器已打开宿主与工作台', `${evidence.chrome.version} · nativeHost=${hostId}`);
  for (const step of STEPS) {
    if (!STEP_FNS[step]) { skip(`步骤 ${step}`, '未知步骤'); continue; }
    try { await STEP_FNS[step](await preflight()); }
    catch (error) { fail(`${step}-X 步骤 ${step} 中断`, error.message); note(`${step}.fatal`, { error: error.message, shots: await shots(`${step}-fatal`) }); }
  }
} catch (error) { fatal = error; fail('P-X 预检或浏览器启动失败', error.message); }
finally {
  evidence.endedAt = new Date().toISOString();
  let merged = readJson(EVIDENCE_FILE, null);
  if (!merged || typeof merged !== 'object' || !merged.byStep) merged = { byStep: {} };
  for (const s of STEPS) merged.byStep[s] = evidence;
  merged.latest = evidence;
  fs.mkdirSync(RESULTS, { recursive: true });
  fs.writeFileSync(EVIDENCE_FILE, JSON.stringify(merged, null, 2));
  console.log(`\n证据已写入 ${rel(EVIDENCE_FILE)}；截图目录 ${rel(SHOTS)}`);
  if (!flag('keep-open')) { try { await host?.close(); await trainer?.close(); } catch { /* ignore */ } await closeChrome(browser); }
  else console.log(`浏览器保持打开（--keep-open），调试端口 ${PORT}，profile ${browser?.profileDir}`);
  summary(path.join(RESULTS, `verify-b-host-${STEPS.join('')}.json`));
  if (fatal) process.exitCode = 1;
}
