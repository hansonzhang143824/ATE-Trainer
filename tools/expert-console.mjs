#!/usr/bin/env node
// PTC 专家控制台桥接服务：面板 ⇄ 本地脚本/资产 ⇄ DSH web API
// 用法：node tools/expert-console.mjs   →  http://127.0.0.1:4090
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { spawn } from 'node:child_process';
import zlib from 'node:zlib';

const ROOT = path.resolve(import.meta.dirname, '..');            // ATE-Coding-Flow
const PROFILES = path.join(ROOT, 'team', 'expert-profiles');
const ARTIFACTS = path.join(ROOT, 'team', 'artifacts');
const PANEL_DIR = path.join(ROOT, 'team', 'ptc');
const AGENTS_MD = path.join(ROOT, 'AGENTS.md');
const STAGE_REGISTRY = path.join(PANEL_DIR, 'ptc_stage_registry.json');
const BINDINGS = path.join(ROOT, 'Training_Materials', '_expert_bindings.json');
const CAPT_BACKUP_DIR = path.join(PANEL_DIR, '.captain-config-backups');
const DSH = process.env.DSH_BASE || 'http://127.0.0.1:3080';
const DSH_SESSIONS_DIR = 'C:/Users/nvt10241/.dsh/sessions/--D-Newtest-DSH-ATE-Coding-Flow--';
const PORT = Number(process.env.PORT || 4090);
const TRAINER_CWD = ROOT;
const TRAINER_SYSTEM = `你是 PTC 专家团队的训练师(Trainer)。用户会丢给你流程图、领域知识、执行问题、吐槽等非结构化材料。
你的任务：把材料拆解成原子知识点，为每条判断（1）归属哪个专家角色（2）落盘位置（3）写入形式，产出"训练提案"。
可用的落盘位置与形式：
- instructions.md（行为规则：该专家遇到 X 应该怎么做）
- profile.yaml（边界修改：可读/可写路径等）
- cases/<TM>/（金标准案例断言）
- output-contract.schema.json（产物合同字段）
- scripts/（需要新脚本时给伪代码方案，标注"建议"）
专家角色清单（显示名=角色ID，提案中的专家字段一律用显示名）：DFT_Expert=ptc-dft-expert、Schematic_Expert=ptc-schematic-expert、Strategic_Expert=strategy-expert、Method_Expert=method-expert、Review_Expert=rule-reviewer、Implement_Expert=ate-implementer、Compile_Expert=compile-diagnostician、Evolution_Expert=evolution-expert。
涉及上下游交接的问题要在提案里注明影响两个专家。
回复格式：先一句话总结材料，然后逐条列出提案，每条格式：
[编号] (专家 | 落盘位置 | 形式) 内容描述 —— 依据
不确定的地方明确标注"待确认"，不要编造。`;

const log = (...a) => console.log(`[${new Date().toISOString().slice(11, 19)}]`, ...a);
const readJson = (p) => { try { return JSON.parse(fs.readFileSync(p, 'utf-8').replace(/^\uFEFF/, '')); } catch { return null; } };
const send = (res, code, data) => { res.writeHead(code, { 'Content-Type': 'application/json; charset=utf-8' }); res.end(JSON.stringify(data)); };
const body = (req) => new Promise((ok) => { let b = ''; req.on('data', (c) => (b += c)); req.on('end', () => { try { ok(JSON.parse(b || '{}')); } catch { ok({}); } }); });

// ---------- 状态聚合 ----------
function expertState() {
  const out = [];
  for (const name of fs.readdirSync(PROFILES)) {
    const dir = path.join(PROFILES, name);
    if (!fs.statSync(dir).isDirectory()) continue;
    const st = readJson(path.join(dir, 'status.json')) || {};
    out.push({
      profileId: name,
      publishedVersion: st.publishedVersion || null,
      draftVerdict: st.draftEvaluation?.verdict || null,
      draftClean: st.draftEvaluation?.assetDigest === st.manifestDigest,
      caseCount: st.draftEvaluation?.caseCount ?? 0,
      history: (st.history || []).map((h) => ({ version: h.version, publishedAt: h.publishedAt })),
    });
  }
  return out;
}

function batchState() {
  let dirs = [];
  try { dirs = fs.readdirSync(ARTIFACTS).filter((d) => /^dali-/.test(d)); } catch {}
  dirs.sort((a, b) => fs.statSync(path.join(ARTIFACTS, b)).mtimeMs - fs.statSync(path.join(ARTIFACTS, a)).mtimeMs);
  // 回执：解析 JSON，按 mtime 倒序（批次目录可能还没落盘，回执先写）
  const R = path.join(ARTIFACTS, 'dispatch-receipts');
  let receipts = [];
  try {
    receipts = fs.readdirSync(R).filter((f) => f.endsWith('.json')).map((f) => {
      const j = readJson(path.join(R, f)) || {};
      const mtimeMs = fs.statSync(path.join(R, f)).mtimeMs;
      return { f, mtimeMs, j };
    }).sort((a, b) => b.mtimeMs - a.mtimeMs);
  } catch {}
  const newestReceipt = receipts.find((r) => r.j.runId) || null;
  // 当前批次 = 最新目录与最新回执 runId 中较新者
  let batchId = dirs[0] || null;
  let batchMs = dirs.length ? fs.statSync(path.join(ARTIFACTS, dirs[0])).mtimeMs : 0;
  if (newestReceipt && newestReceipt.mtimeMs > batchMs) { batchId = newestReceipt.j.runId; batchMs = newestReceipt.mtimeMs; }
  if (!batchId) return null;
  let state = '?';
  const handoff = readJson(path.join(ARTIFACTS, batchId, 'advance-handoff.json')) || {};
  if (handoff.state) state = handoff.state;
  // 本批专家状态：回执 + 子会话活跃度（session 文件 mtime 距今）
  const specialists = [];
  for (const r of receipts) {
    const j = r.j;
    if (j.runId !== batchId) continue;
    let child = null;
    if (j.childSessionId) {
      try {
        const st = fs.statSync(path.join(DSH_SESSIONS_DIR, j.childSessionId, 'session.jsonl.zstd'));
        child = { sessionId: j.childSessionId, size: st.size, lastWrite: new Date(st.mtimeMs).toISOString(), activeMs: Date.now() - st.mtimeMs };
      } catch { child = { sessionId: j.childSessionId, size: 0, lastWrite: null, activeMs: Infinity }; }
    }
    specialists.push({
      profileId: j.profileId, profileVersion: j.profileVersion, label: j.label,
      executionClass: j.executionClass, stage: j.stage, targetTms: j.targetTms || [],
      dispatchedAt: j.dispatchedAt || j.createdAt, child,
    });
  }
  if (state === '?' && specialists.length) state = specialists[0].stage || '?';
  return { batchId, state, stage: state, receipts: receipts.filter((r) => r.j.runId === batchId).map((r) => r.f.replace(/\.json$/, '')), specialists };
}

async function dshOnline() {
  try { const c = new AbortController(); setTimeout(() => c.abort(), 1500); const r = await fetch(DSH + '/', { signal: c.signal }); return r.status > 0; } catch { return false; }
}

// ---------- 脚本执行 ----------
function runScript(args, timeoutMs = 300_000) {
  return new Promise((resolve) => {
    const p = spawn('python', args, { cwd: ROOT });
    let out = '', err = '', done = false;
    const t = setTimeout(() => { if (!done) { done = true; p.kill(); resolve({ exitCode: -1, stdout: out, stderr: err + '\n[timeout]' }); } }, timeoutMs);
    p.stdout.on('data', (c) => (out += c)); p.stderr.on('data', (c) => (err += c));
    p.on('close', (code) => { if (!done) { done = true; clearTimeout(t); resolve({ exitCode: code, stdout: out, stderr: err }); } });
  });
}
const nextVersion = (v) => 'v' + (Number(String(v || 'v0').replace(/^v/, '')) + 1);

  // ---------- Captain 职责配置 ----------
  function captainAgmdSection() {
    const txt = fs.readFileSync(AGENTS_MD, 'utf-8').replace(/\r\n/g, '\n');
    const m = txt.match(/\n## Captain entry\n([\s\S]*?)(?=\n## )/);
    if (!m) throw new Error('AGENTS.md 中找不到 ## Captain entry 节');
    return { full: txt, section: m[1].replace(/^\n+|\n+$/g, '') };
  }
  function backupFile(p) {
    fs.mkdirSync(CAPT_BACKUP_DIR, { recursive: true });
    const bak = path.join(CAPT_BACKUP_DIR, path.basename(p) + '.' + new Date().toISOString().replace(/[:.]/g, '-') + '.bak');
    fs.copyFileSync(p, bak);
    return path.relative(ROOT, bak);
  }

// ---------- 地址簿（单 profile + 模式切根：training=Training_Materials，delivery=项目根） ----------
function bindingsDoc() {
  const b = readJson(BINDINGS);
  if (!b || !Array.isArray(b.experts)) return null;
  return b;
}
function addressBook(mode) {
  const b = bindingsDoc();
  if (!b) return { mode: 'training', root: 'Training_Materials', text: '【地址簿不可用：_expert_bindings.json 读取失败】' };
  const m = mode && b.modes?.[mode] ? mode : (b.activeMode || 'training');
  const root = b.modes?.[m]?.root || 'Training_Materials';
  const rel = (p) => String(p || '').replace(/^Training_Materials/, root);
  const lines = b.experts.map((e) =>
    `- ${e.displayName || e.name}（${e.profileId || e.name}｜${e.stage || '?'}）：读 ${rel(e.reads)}；写 ${rel(e.writes)}；校验 ${rel(e.verification)}` + (e.note ? `；注：${e.note}` : '')
  );
  return { mode: m, root, text: `【地址簿（当前模式=${m}，根=${root}）——所有专家按以下地址读写校验，禁止自行换目录】\n` + lines.join('\n') };
}

// ---------- 训练写入（幂等） ----------
function trainRule(profileId, rule, source) {
  const dir = path.join(PROFILES, profileId);
  if (!fs.existsSync(dir)) return { ok: false, error: `unknown profile ${profileId}` };
  const id = crypto.createHash('sha256').update(rule.trim()).digest('hex').slice(0, 8);
  const insPath = path.join(dir, 'instructions.md');
  const ins = fs.readFileSync(insPath, 'utf-8');
  if (ins.includes(`ptc-console:rule id=${id}`)) return { ok: true, deduped: true, id };
  const stamp = new Date().toISOString().slice(0, 10);
  fs.writeFileSync(insPath, ins.replace(/\s*$/, '') + `\n\n<!-- ptc-console:rule id=${id} src=${(source || 'console').slice(0, 40)} -->\n- ${rule.trim()}\n`);
  const chPath = path.join(dir, 'CHANGELOG.md');
  const ch = fs.existsSync(chPath) ? fs.readFileSync(chPath, 'utf-8') : '';
  fs.writeFileSync(chPath, ch.replace(/\s*$/, '') + `\n\n## Training round ${stamp} (console)\n- rule ${id}: ${rule.trim().slice(0, 120)}\n- 出处: ${source || 'console'}\n`);
  return { ok: true, id };
}

// ---------- Trainer（DSH 会话桥） ----------
const trainer = { sessionId: null, lastReply: null, pending: false, promptAt: 0 };
const TRAINER_STATE = path.join(PANEL_DIR, '.trainer-session.json');
try { const t = JSON.parse(fs.readFileSync(TRAINER_STATE, 'utf-8')); if (t.sessionId) { trainer.sessionId = t.sessionId; log('trainer session restored:', t.sessionId); } } catch {}

async function dshCall(method, payload) {
  const r = await fetch(DSH + '/api/' + method, {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ type: 'client-request', rpcId: crypto.randomUUID(), method, payload }),
  });
  return { status: r.status, text: await r.text() };
}

async function ensureTrainerSession() {
  if (trainer.sessionId) return trainer.sessionId;
  const r = await dshCall('session.create', { cwd: TRAINER_CWD });
  const m = JSON.parse(r.text);
  const sid = m.sessionId || m.result?.value?.sessionId;
  if (!sid) throw new Error('session.create failed: ' + r.text.slice(0, 200));
  trainer.sessionId = sid;
  try { fs.writeFileSync(TRAINER_STATE, JSON.stringify({ sessionId: sid, at: new Date().toISOString() })); } catch {}
  await dshCall('session.prompt', { sessionId: sid, mode: 'queue', content: [{ type: 'text', text: TRAINER_SYSTEM }] });
  log('trainer session created:', m.sessionId);
  return m.sessionId;
}

// ---------- Trainer 回复回收（轮询会话文件） ----------
function readTrainerReply() {
  if (!trainer.sessionId || !trainer.promptAt) return null;
  const dir = 'C:/Users/nvt10241/.dsh/sessions/--D-Newtest-DSH-ATE-Coding-Flow--/' + trainer.sessionId;
  const p = path.join(dir, 'session.jsonl.zstd');
  let buf;
  try { buf = fs.readFileSync(p); } catch { return null; }
  // 多帧 zstd 解压
  const MAGIC = Buffer.from([0x28, 0xB5, 0x2F, 0xFD]);
  const parts = []; let pos = 0;
  while (pos < buf.length) {
    const idx = buf.indexOf(MAGIC, pos);
    if (idx < 0) { parts.push(buf.slice(pos)); break; }
    if (idx > pos) parts.push(buf.slice(pos, idx));
    const next = buf.indexOf(MAGIC, idx + 4);
    const end = next < 0 ? buf.length : next;
    try { parts.push(zlib.zstdDecompressSync(buf.slice(idx, end))); } catch { /* 帧未写完，跳过 */ }
    pos = end;
  }
  let txt = '';
  try { txt = Buffer.concat(parts).toString('utf8'); } catch { return null; }
  let lastMsg = null, lastEnd = 0;
  for (const line of txt.split('\n')) {
    if (!line.trim()) continue;
    let ev; try { ev = JSON.parse(line); } catch { continue; }
    const t = ev.time || 0;
    if (t <= trainer.promptAt) continue;
    if (ev.type === 'assistant/message') {
      const texts = (ev.data?.message?.content || []).filter((c) => c.type === 'text').map((c) => c.text);
      if (texts.length) lastMsg = { at: new Date(t).toISOString(), text: texts.join('\n') };
    }
    if (ev.type === 'turn/end') lastEnd = t;
  }
  if (lastMsg && lastEnd > trainer.promptAt) { trainer.pending = false; trainer.lastReply = lastMsg; }
  return lastMsg;
}

// ---------- Captain 交付会话桥（面板开批入口） ----------
const captain = { sessionId: null, lastReply: null, pending: false, promptAt: 0 };
const CAPT_SESSION_STATE = path.join(PANEL_DIR, '.captain-session.json');
try { const c = JSON.parse(fs.readFileSync(CAPT_SESSION_STATE, 'utf-8')); if (c.sessionId) { captain.sessionId = c.sessionId; log('captain session restored:', c.sessionId); } } catch {}

async function ensureCaptainSession() {
  if (captain.sessionId) return captain.sessionId;
  const r = await dshCall('session.create', { cwd: TRAINER_CWD, agentPreset: 'ate-ptc' });
  const m = JSON.parse(r.text);
  const sid = m.sessionId || m.result?.value?.sessionId;
  if (!sid) throw new Error('session.create failed: ' + r.text.slice(0, 200));
  captain.sessionId = sid;
  try { fs.writeFileSync(CAPT_SESSION_STATE, JSON.stringify({ sessionId: sid, at: new Date().toISOString() }, null, 2)); } catch {}
  log('captain session created:', sid);
  return sid;
}

function readCaptainReply() {
  if (!captain.sessionId) return null;
  const dir = 'C:/Users/nvt10241/.dsh/sessions/--D-Newtest-DSH-ATE-Coding-Flow--/' + captain.sessionId;
  const p = path.join(dir, 'session.jsonl.zstd');
  let buf;
  try { buf = fs.readFileSync(p); } catch { return null; }
  // 多帧 zstd 解压
  const MAGIC = Buffer.from([0x28, 0xB5, 0x2F, 0xFD]);
  const parts = []; let pos = 0;
  while (pos < buf.length) {
    const idx = buf.indexOf(MAGIC, pos);
    if (idx < 0) { parts.push(buf.slice(pos)); break; }
    if (idx > pos) parts.push(buf.slice(pos));
    const next = buf.indexOf(MAGIC, idx + 4);
    const end = next < 0 ? buf.length : next;
    try { parts.push(zlib.zstdDecompressSync(buf.slice(idx, end))); } catch { /* 帧未写完，跳过 */ }
    pos = end;
  }
  let txt = '';
  try { txt = Buffer.concat(parts).toString('utf8'); } catch { return null; }
  let lastMsg = null, lastEnd = 0, hookReason = null;
  for (const line of txt.split('\n')) {
    if (!line.trim()) continue;
    let ev; try { ev = JSON.parse(line); } catch { continue; }
    const t = ev.time || 0;
    if (t <= (captain.promptAt || 0)) continue;
    if (ev.type === 'assistant/message') {
      const texts = (ev.data?.message?.content || []).filter((c) => c.type === 'text').map((c) => c.text);
      if (texts.length) lastMsg = { at: new Date(t).toISOString(), text: texts.join('\n') };
    }
    if (ev.type === 'turn/end') {
      lastEnd = t;
      const rr = ev.data?.reason?.reason;
      if (rr?.kind === 'hook') hookReason = rr.reason;
    }
  }
  // hook 直接派发时 turn 无 assistant 消息：用 hook 原因当回复，避免 pending 挂死
  if (!lastMsg && lastEnd > captain.promptAt && hookReason) {
    lastMsg = { at: new Date(lastEnd).toISOString(), text: 'Captain（hook 直接派发，本轮无对话回复）：' + hookReason };
  }
  if (lastMsg && lastEnd > captain.promptAt) { captain.pending = false; captain.lastReply = lastMsg; }
  return lastMsg;
}

// ---------- HTTP ----------
const MIME = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript', '.css': 'text/css', '.json': 'application/json', '.png': 'image/png' };
const server = http.createServer(async (req, res) => {
  const url = new URL(req.url, 'http://x');
  try {
    if (url.pathname === '/api/state') {
      return send(res, 200, { experts: expertState(), batch: batchState(), dsh: { base: DSH, online: await dshOnline() }, trainer: { sessionId: trainer.sessionId, pending: trainer.pending, hasReply: !!trainer.lastReply }, captain: { sessionId: captain.sessionId, pending: captain.pending, hasReply: !!captain.lastReply } });
    }
    if (url.pathname === '/api/receipts') {
      const b = batchState(); return send(res, 200, { receipts: b?.receipts || [] });
    }
    if (req.method === 'GET' && url.pathname === '/api/captain/config') {
      const { full, section } = captainAgmdSection();
      const registry = readJson(STAGE_REGISTRY);
      if (!registry) return send(res, 500, { error: 'ptc_stage_registry.json 读取失败' });
      return send(res, 200, { agmd: section, registry, stateMachine: registry.stateMachine });
    }
    if (req.method === 'POST' && url.pathname === '/api/captain/config') {
      const { agmd, registry } = await body(req);
      const done = [];
      if (typeof agmd === 'string' && agmd.trim()) {
        const clean = agmd.replace(/\r\n/g, '\n').replace(/^\n+|\n+$/g, '');
        if (/^##\s/m.test(clean)) return send(res, 400, { error: '行为规则里不能包含二级标题（## ）' });
        if (clean.length > 8000) return send(res, 400, { error: '文本过长（>8000）' });
        const { full } = captainAgmdSection();
        const bak = backupFile(AGENTS_MD);
        fs.writeFileSync(AGENTS_MD, full.replace(/\n## Captain entry\n[\s\S]*?(?=\n## )/, `\n## Captain entry\n\n${clean}\n`), 'utf-8');
        done.push(`AGENTS.md Captain entry 已更新（备份 ${bak}）`);
      }
      if (registry && typeof registry === 'object') {
        if (!Array.isArray(registry.stateMachine) || !registry.stages || typeof registry.stages !== 'object') {
          return send(res, 400, { error: 'registry 必须包含 stateMachine 数组和 stages 对象' });
        }
        const cur = readJson(STAGE_REGISTRY);
        if (JSON.stringify(registry.stateMachine) !== JSON.stringify(cur?.stateMachine)) {
          return send(res, 400, { error: 'stateMachine 顺序固定（AGENTS.md 约定），面板不提供改顺序' });
        }
        // 防空白行污染：面板按 stateMachine 渲染，原本不存在的终态（如 COMPLETE）
        // 全空时不写入 stages。
        for (const k of Object.keys(registry.stages)) {
          const st = registry.stages[k] || {};
          const blank = !String(st.owner || '').trim() && !String(st.gate || '').trim() && !(st.families || []).length && !(st.outputs || []).length;
          if (blank && !cur?.stages?.[k]) delete registry.stages[k];
        }
        const bak = backupFile(STAGE_REGISTRY);
        fs.writeFileSync(STAGE_REGISTRY, JSON.stringify(registry, null, 2) + '\n', 'utf-8');
        done.push(`ptc_stage_registry.json 已更新（备份 ${bak}）`);
      }
      if (!done.length) return send(res, 400, { error: '没有可保存的变更（agmd / registry）' });
      return send(res, 200, { ok: true, done });
    }
    if (req.method === 'POST' && url.pathname === '/api/batch/advance') {
      const { batchId } = await body(req);
      const b = batchState();
      const bid = batchId || b?.batchId;
      if (!bid) return send(res, 400, { error: 'no batch to advance' });
      const r = await runScript(['scripts/captain_delivery_entry.py', '--continue-batch', bid], 600_000);
      return send(res, 200, { batchId: bid, ...r });
    }
    if (req.method === 'POST' && url.pathname === '/api/evaluate') {
      const { profile } = await body(req);
      if (!profile) return send(res, 400, { error: 'profile required' });
      const r = await runScript(['scripts/evaluate_expert_profile.py', '--profile', profile, '--version', 'draft']);
      return send(res, 200, { ...r, verdict: /"verdict":\s*"pass"/.test(r.stdout) ? 'pass' : 'fail' });
    }
    if (req.method === 'POST' && url.pathname === '/api/publish') {
      const { profile } = await body(req);
      if (!profile) return send(res, 400, { error: 'profile required' });
      const st = readJson(path.join(PROFILES, profile, 'status.json'));
      const v = nextVersion(st?.publishedVersion);
      const r = await runScript(['scripts/publish_expert_profile.py', '--profile', profile, '--version', v]);
      return send(res, 200, { ...r, version: v });
    }
    if (req.method === 'POST' && url.pathname === '/api/roster') {
      const r = await runScript(['scripts/validate_expert_roster.py']);
      return send(res, 200, r);
    }
    if (req.method === 'POST' && url.pathname === '/api/train-rule') {
      const { profile, rule, source } = await body(req);
      if (!profile || !rule) return send(res, 400, { error: 'profile and rule required' });
      const w = trainRule(profile, rule, source);
      if (!w.ok) return send(res, 400, w);
      const ev = await runScript(['scripts/evaluate_expert_profile.py', '--profile', profile, '--version', 'draft']);
      return send(res, 200, { write: w, evaluation: { exitCode: ev.exitCode, verdict: /"verdict":\s*"pass"/.test(ev.stdout) ? 'pass' : 'fail', stdout: ev.stdout.slice(0, 4000), stderr: ev.stderr.slice(0, 2000) } });
    }
    if (req.method === 'POST' && url.pathname === '/api/proposal/apply') {
      const { profile, location, text, source } = await body(req);
      if (!profile || !text) return send(res, 400, { error: 'profile and text required' });
      const dir = path.join(PROFILES, profile);
      if (!fs.existsSync(dir)) return send(res, 400, { error: `unknown profile ${profile}` });
      const src = (source || 'trainer').slice(0, 60);
      const id = crypto.createHash('sha256').update((location + '|' + text).trim()).digest('hex').slice(0, 8);
      if (/instructions/i.test(location || '')) {
        const w = trainRule(profile, text, src);
        if (!w.ok) return send(res, 400, w);
        if (w.deduped) return send(res, 200, { ok: true, deduped: true, id, mode: 'instructions' });
        const ev = await runScript(['scripts/evaluate_expert_profile.py', '--profile', profile, '--version', 'draft']);
        return send(res, 200, { ok: true, id, mode: 'instructions', evaluation: { exitCode: ev.exitCode, verdict: /"verdict":\s*"pass"/.test(ev.stdout) ? 'pass' : 'fail', stdout: ev.stdout.slice(0, 4000), stderr: ev.stderr.slice(0, 2000) } });
      }
      // 非 instructions 落盘位置：暂存到 training-proposals.md 待人工执行（幂等）
      const stagePath = path.join(ARTIFACTS, 'training-proposals.md');
      let st2 = '';
      try { st2 = fs.readFileSync(stagePath, 'utf-8'); } catch {}
      if (st2.includes(`proposal id=${id}`)) return send(res, 200, { ok: true, deduped: true, id, mode: 'staged' });
      fs.writeFileSync(stagePath, st2.replace(/\s*$/, '') + `\n\n## Proposal ${id} (${new Date().toISOString().slice(0, 10)})\n- 专家: ${profile}\n- 落盘位置: ${location}\n- 形式: proposals\n- 出处: ${src}\n\n\`\`\`\n${text.trim()}\n\`\`\`\n`);
      return send(res, 200, { ok: true, id, mode: 'staged', file: 'team/artifacts/training-proposals.md' });
    }
    if (url.pathname === '/api/bindings/mode') {
      const b = bindingsDoc();
      if (!b) return send(res, 500, { error: '_expert_bindings.json 读取失败' });
      if (req.method === 'GET') return send(res, 200, { activeMode: b.activeMode || 'training', modes: b.modes || {}, book: addressBook() });
      const { mode } = await body(req);
      if (!b.modes?.[mode]) return send(res, 400, { error: 'unknown mode（training / delivery）' });
      b.activeMode = mode;
      fs.writeFileSync(BINDINGS, JSON.stringify(b, null, 2) + '\n', 'utf-8');
      return send(res, 200, { ok: true, activeMode: mode, book: addressBook(mode) });
    }
    if (req.method === 'POST' && url.pathname === '/api/trainer/send') {
      const { text, noAddressBook } = await body(req);
      if (!text) return send(res, 400, { error: 'text required' });
      if (!(await dshOnline())) return send(res, 502, { error: 'DSH web 不在线 (' + DSH + ')' });
      const sid = await ensureTrainerSession();
      const ab = noAddressBook ? null : addressBook();
      const full = ab ? ab.text + '\n\n' + text : text;
      const r = await dshCall('session.prompt', { sessionId: sid, mode: 'queue', content: [{ type: 'text', text: full }] });
      const ok = r.text.includes('"accepted":true') || r.text.includes('"ok":true');
      if (ok) { trainer.pending = true; trainer.lastReply = null; trainer.promptAt = Date.now(); }
      return send(res, 200, { sessionId: sid, dshStatus: r.status, accepted: ok, injected: !!ab, mode: ab?.mode || null, raw: r.text.slice(0, 300) });
    }
    if (url.pathname === '/api/trainer/poll') {
      const msg = trainer.pending ? readTrainerReply() : trainer.lastReply;
      return send(res, 200, { pending: trainer.pending, reply: msg || trainer.lastReply });
    }
    if (req.method === 'POST' && url.pathname === '/api/captain/send') {
      const { text } = await body(req);
      if (!text) return send(res, 400, { error: 'text required' });
      if (!(await dshOnline())) return send(res, 502, { error: 'DSH web 不在线 (' + DSH + ')' });
      // 首条开批消息必须带 TM 编号（对齐 captain-entry.js 的开批判定）
      if (!captain.sessionId && !/\bTM\s*\d+\b/iu.test(text)) return send(res, 400, { error: '首条开批消息必须包含 TM 编号（如 TM108）' });
      const sid = await ensureCaptainSession();
      const r = await dshCall('session.prompt', { sessionId: sid, mode: 'queue', content: [{ type: 'text', text }] });
      const ok = r.text.includes('"accepted":true') || r.text.includes('"ok":true');
      if (ok) { captain.pending = true; captain.lastReply = null; captain.promptAt = Date.now(); }
      return send(res, 200, { sessionId: sid, dshStatus: r.status, accepted: ok, raw: r.text.slice(0, 300) });
    }
    if (url.pathname === '/api/captain/poll') {
      // 服务重启后 promptAt 丢失：有会话但没缓存回复时也读一次会话文件
      const msg = (captain.pending || (captain.sessionId && !captain.lastReply)) ? readCaptainReply() : captain.lastReply;
    return send(res, 200, { pending: captain.pending, sessionId: captain.sessionId, reply: msg || captain.lastReply });
    }
    // 静态：/ → 面板
    let file = url.pathname === '/' ? '/prototype-expert-console.html' : url.pathname;
    const p = path.join(PANEL_DIR, path.normalize(file).replace(/^([/\\])+/, ''));
    if (p.startsWith(PANEL_DIR) && fs.existsSync(p) && fs.statSync(p).isFile()) {
      res.writeHead(200, { 'Content-Type': MIME[path.extname(p)] || 'application/octet-stream' });
      return res.end(fs.readFileSync(p));
    }
    send(res, 404, { error: 'not found' });
  } catch (e) { send(res, 500, { error: String(e) }); }
});

server.listen(PORT, '127.0.0.1', () => log(`expert-console on http://127.0.0.1:${PORT}  (ROOT=${ROOT})`));
