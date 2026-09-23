// Read-only session inventory for a planned deletion. Reuses the installed
// dsh-session-manager scan (same validation and identity data the GUI panel uses).
// Writes only into this artifact directory. Deletes nothing.
import { pathToFileURL } from 'node:url';
import { writeFile, mkdir } from 'node:fs/promises';
import { readFileSync } from 'node:fs';
import zlib from 'node:zlib';
import path from 'node:path';

const PLUGIN = 'C:/Users/nvt10241/.dsh/plugins/dsh-session-manager/lib/index.js';
const OUT_DIR = path.dirname(new URL(import.meta.url).pathname.replace(/^\//, '').replace(/\//g, path.sep));

const { scanSessions } = await import(pathToFileURL(PLUGIN).href);

const data = await scanSessions();

function headerOf(file) {
  try {
    const buf = zlib.zstdDecompressSync(readFileSync(file));
    const s = buf.toString('utf8');
    const i = s.indexOf('\n');
    return JSON.parse(s.slice(0, i < 0 ? s.length : i));
  } catch {
    return null;
  }
}

const rows = [];
for (const s of data.sessions) {
  const file = path.join(data.sessionsRoot, s.workspace, s.id, 'session.jsonl.zstd');
  const h = headerOf(file);
  rows.push({
    id: s.id,
    workspace: s.workspace,
    workspacePath: s.workspacePath,
    title: s.title,
    sizeBytes: s.sizeBytes,
    current: s.current === true,
    origin: h?.origin ?? '(header-unreadable)',
    kind: h?.parentSession ? 'subagent' : 'top-level',
    depth: h?.delegationDepth ?? null,
    preset: h?.agentPreset ?? null,
    createdAtIso: h?.createdAt ? new Date(h.createdAt).toISOString() : null,
  });
}

const byWorkspace = {};
for (const r of rows) {
  const w = (byWorkspace[r.workspace] ??= { sessions: 0, subagent: 0, bytes: 0, current: 0 });
  w.sessions += 1;
  w.bytes += r.sizeBytes;
  if (r.kind === 'subagent') w.subagent += 1;
  if (r.current) w.current += 1;
}

const totalBytes = rows.reduce((a, r) => a + r.sizeBytes, 0);
const summary = {
  scannedAt: new Date().toISOString(),
  sessionsRoot: data.sessionsRoot,
  currentSessionId: process.env.DSH_SESSION_ID ?? null,
  total: rows.length,
  totalBytes,
  subagentSessions: rows.filter((r) => r.kind === 'subagent').length,
  perWorkspace: byWorkspace,
  candidateScopes: {
    allExceptCurrent: {
      count: rows.filter((r) => !r.current).length,
      bytes: rows.filter((r) => !r.current).reduce((a, r) => a + r.sizeBytes, 0),
    },
    ateWorkspaceExceptCurrent: {
      count: rows.filter((r) => !r.current && r.workspace === '--D-Newtest-DSH-ATE-Coding-Plat--').length,
      bytes: rows.filter((r) => !r.current && r.workspace === '--D-Newtest-DSH-ATE-Coding-Plat--').reduce((a, r) => a + r.sizeBytes, 0),
    },
    subagentOnlyExceptCurrent: {
      count: rows.filter((r) => !r.current && r.kind === 'subagent').length,
      bytes: rows.filter((r) => !r.current && r.kind === 'subagent').reduce((a, r) => a + r.sizeBytes, 0),
    },
  },
};

await mkdir(OUT_DIR, { recursive: true });
const stamp = new Date().toISOString().replace(/[:.]/g, '-');
const jsonPath = path.join(OUT_DIR, `dry-run-${stamp}.json`);
await writeFile(jsonPath, JSON.stringify({ summary, sessions: rows }, null, 2), 'utf8');

const md = [];
md.push(`# 会话删除 dry-run 清单（${summary.scannedAt}）`);
md.push('');
md.push(`- 会话根目录：\`${summary.sessionsRoot}\``);
md.push(`- 当前会话（受保护，永不可删）：\`${summary.currentSessionId}\``);
md.push(`- 磁盘会话总数：**${summary.total}**，合计 **${(totalBytes / 1048576).toFixed(1)} MiB**；其中子 agent 子会话 **${summary.subagentSessions}** 条`);
md.push('');
md.push('## 按工作区');
md.push('');
md.push('| 工作区 slug | 会话数 | 其中子 agent | 占用 MiB |');
md.push('|---|---:|---:|---:|');
for (const [slug, w] of Object.entries(byWorkspace).sort((a, b) => b[1].sessions - a[1].sessions)) {
  md.push(`| ${slug} | ${w.sessions} | ${w.subagent} | ${(w.bytes / 1048576).toFixed(1)} |`);
}
md.push('');
md.push('## 可选范围（均排除当前会话）');
md.push('');
md.push('| 范围 | 条数 | 占用 MiB |');
md.push('|---|---:|---:|');
for (const [k, v] of Object.entries(summary.candidateScopes)) {
  md.push(`| ${k} | ${v.count} | ${(v.bytes / 1048576).toFixed(1)} |`);
}
md.push('');
md.push('## 全部会话明细');
md.push('');
md.push('| id | 工作区 | 标题 | 类型 | 预设 | 创建时间 | MiB |');
md.push('|---|---|---|---|---|---|---:|');
for (const r of rows.sort((a, b) => (b.createdAtIso ?? '').localeCompare(a.createdAtIso ?? ''))) {
  md.push(`| ${r.id}${r.current ? ' **(当前)**' : ''} | ${r.workspace} | ${String(r.title).replace(/\|/g, '/')} | ${r.kind}${r.depth !== null ? ` d${r.depth}` : ''} | ${r.preset ?? '-'} | ${r.createdAtIso ?? '-'} | ${(r.sizeBytes / 1048576).toFixed(2)} |`);
}
const mdPath = path.join(OUT_DIR, `dry-run-${stamp}.md`);
await writeFile(mdPath, md.join('\n'), 'utf8');

console.log(JSON.stringify({
  jsonPath,
  mdPath,
  total: summary.total,
  totalMiB: +(totalBytes / 1048576).toFixed(1),
  subagentSessions: summary.subagentSessions,
  current: summary.currentSessionId,
  perWorkspace: Object.fromEntries(Object.entries(byWorkspace).map(([k, v]) => [k, `${v.sessions} (sub ${v.subagent}, ${(v.bytes / 1048576).toFixed(1)} MiB)`])),
  candidateScopes: summary.candidateScopes,
}, null, 2));
