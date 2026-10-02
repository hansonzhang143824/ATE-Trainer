// Shared helpers for Agent Trainer acceptance scripts (Claude, 2026-10-02).
// Node >= 18 (global fetch). Run from the repo root: D:\Newtest\DSH\ATE-Coding-Flow
import fs from 'node:fs';
import path from 'node:path';
import { randomUUID, createHash } from 'node:crypto';

export const BASE = process.env.TRAINER_BASE || 'http://127.0.0.1:3080';
export const ROOT = path.resolve(process.env.TRAINER_ROOT || process.cwd());
export const PROJECT_ID = 'agent-trainer';
export const PROJECT_DIR = path.join(ROOT, 'Training_Materials/framework/projects', PROJECT_ID);
export const CONTROL_DIR = path.join(ROOT, 'Training_Materials/framework/control');
export const LEDGER = 'contracts/agent-ids.json';
export const ID_RE = /^[A-Za-z0-9][A-Za-z0-9_-]{0,127}$/;
export const RESERVED_RE = /^(con|prn|aux|nul|com[1-9]|lpt[1-9])$/i;
export const validId = id => typeof id === 'string' && ID_RE.test(id) && !RESERVED_RE.test(id);
export const sha256 = text => createHash('sha256').update(text).digest('hex');
export const requestId = tag => `verify-${tag}-${randomUUID()}`;

/** POST /api/ptc-control/trainer/<op>. Returns {ok, value, error, status}. Never throws on API errors. */
export async function api(op, body) {
  const res = await fetch(`${BASE}/api/ptc-control/trainer/${op}`, {
    method: 'POST', headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
    body: JSON.stringify({ projectId: PROJECT_ID, ...body }),
  });
  const payload = await res.json().catch(() => ({}));
  const ok = res.ok && payload.ok !== false;
  return { ok, status: res.status, value: ok ? (Object.hasOwn(payload, 'value') ? payload.value : payload) : undefined, error: ok ? null : (payload.error || { message: `HTTP ${res.status}` }) };
}
export async function must(op, body) {
  const r = await api(op, body);
  if (!r.ok) throw new Error(`${op} failed: ${r.error?.code || ''} ${r.error?.message || ''}`);
  return r.value;
}
export async function context(mode = 'training') { return must('context', { mode }); }
export async function assets(mode = 'training', revisionId) { return must('assets', { mode, ...(revisionId ? { revisionId } : {}) }); }

export function parseLedger(content) {
  let data; try { data = JSON.parse(content); } catch { return { ok: false, why: 'JSON 无法解析' }; }
  if (!data || data.schemaVersion !== 1) return { ok: false, why: 'schemaVersion !== 1' };
  if (!Array.isArray(data.allocated)) return { ok: false, why: 'allocated 不是数组' };
  const bad = data.allocated.filter(id => !validId(id));
  if (bad.length) return { ok: false, why: `非法 ID: ${bad.slice(0, 5).join(', ')}` };
  if (new Set(data.allocated).size !== data.allocated.length) return { ok: false, why: '存在重复 ID' };
  return { ok: true, data };
}

export function walk(dir, out = []) {
  if (!fs.existsSync(dir)) return out;
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const p = path.join(dir, entry.name);
    if (entry.isDirectory()) walk(p, out); else if (entry.isFile()) out.push(p);
  }
  return out;
}
export const rel = p => path.relative(ROOT, p).split(path.sep).join('/');
export const readJson = (p, fallback = undefined) => { try { return JSON.parse(fs.readFileSync(p, 'utf8')); } catch { return fallback; } };

// ---- reporting ----
const results = [];
export function record(id, status, detail = '') { results.push({ id, status, detail }); const tag = { PASS: '✔ PASS', FAIL: '✘ FAIL', SKIP: '- SKIP', WARN: '! WARN' }[status] || status; console.log(`${tag}  ${id}${detail ? `  —  ${detail}` : ''}`); }
export const pass = (id, d) => record(id, 'PASS', d);
export const fail = (id, d) => record(id, 'FAIL', d);
export const skip = (id, d) => record(id, 'SKIP', d);
export const warn = (id, d) => record(id, 'WARN', d);
export async function check(id, fn) { try { const r = await fn(); if (r === undefined || r === true) pass(id); else if (typeof r === 'string') pass(id, r); } catch (e) { fail(id, e.message); } }
export function summary(file) {
  const count = s => results.filter(r => r.status === s).length;
  console.log(`\n结果：PASS ${count('PASS')} · FAIL ${count('FAIL')} · WARN ${count('WARN')} · SKIP ${count('SKIP')}`);
  if (file) { fs.mkdirSync(path.dirname(file), { recursive: true }); fs.writeFileSync(file, JSON.stringify({ at: new Date().toISOString(), base: BASE, root: ROOT, results }, null, 2)); console.log(`结果已写入 ${rel(file)}`); }
  process.exitCode = count('FAIL') ? 1 : 0;
}
export const assert = (cond, msg) => { if (!cond) throw new Error(msg); };
export const args = new Set(process.argv.slice(2));
