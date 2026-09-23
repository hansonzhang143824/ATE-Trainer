// Planned-deletion runner for DSH sessions. Reuses the installed
// dsh-session-manager scan/delete so the SAME validation the GUI panel applies
// (id whitelist, workspace slug, path containment, current-session refusal,
// trash recoverability) governs this script too.
//
// Usage (dry-run is the default; nothing is deleted without --yes):
//   node delete-sessions.mjs --ids session-aaa,session-bbb
//   node delete-sessions.mjs --title "some title substring"
//   node delete-sessions.mjs --workspace --D-Newtest-DSH-ATE-Coding-Plat--
//   node delete-sessions.mjs --ids ... --mode permanent --yes
import { pathToFileURL } from 'node:url';
import { appendFile, writeFile, mkdir } from 'node:fs/promises';
import path from 'node:path';

const PLUGIN = 'C:/Users/nvt10241/.dsh/plugins/dsh-session-manager/lib/index.js';
const OUT_DIR = 'D:/Newtest/DSH/ATE-Coding-Plat/team/artifacts/session-cleanup';

const { scanSessions, deleteSessions } = await import(pathToFileURL(PLUGIN).href);

const argv = process.argv.slice(2);
function flag(name) {
  const i = argv.indexOf(`--${name}`);
  return i === -1 ? undefined : (argv[i + 1] ?? '');
}
const idsArg = flag('ids');
const titleArg = flag('title');
const workspaceArg = flag('workspace');
const mode = flag('mode') === 'permanent' ? 'permanent' : 'trash';
const confirmed = argv.includes('--yes');

const scan = await scanSessions();
let selected = scan.sessions;

if (idsArg) {
  const want = new Set(idsArg.split(',').map((s) => s.trim()).filter(Boolean));
  selected = selected.filter((s) => want.has(s.id));
} else if (titleArg !== undefined && titleArg !== '') {
  const needle = titleArg.toLowerCase();
  selected = selected.filter((s) => String(s.title).toLowerCase().includes(needle));
} else if (workspaceArg) {
  selected = selected.filter((s) => s.workspace === workspaceArg);
} else {
  console.log(JSON.stringify({
    error: 'no selector given: pass --ids, --title, or --workspace',
    usage: 'node delete-sessions.mjs --ids <id,id> | --title <substr> | --workspace <slug> [--mode trash|permanent] [--yes]',
  }, null, 2));
  process.exit(2);
}

const protectedRows = selected.filter((s) => s.current);
const rows = selected.filter((s) => !s.current);
const plan = {
  scannedAt: new Date().toISOString(),
  mode,
  confirmed,
  selector: { ids: idsArg ?? null, title: titleArg ?? null, workspace: workspaceArg ?? null },
  selected: rows.map((s) => ({ id: s.id, workspace: s.workspace, title: s.title, sizeBytes: s.sizeBytes })),
  selectedCount: rows.length,
  selectedBytes: rows.reduce((a, s) => a + s.sizeBytes, 0),
  refusedCurrent: protectedRows.map((s) => s.id),
};

await mkdir(OUT_DIR, { recursive: true });
const stamp = new Date().toISOString().replace(/[:.]/g, '-');

if (!confirmed) {
  plan.result = 'DRY-RUN (nothing deleted; add --yes to execute)';
  await writeFile(path.join(OUT_DIR, `delete-plan-${stamp}.json`), JSON.stringify(plan, null, 2), 'utf8');
  console.log(JSON.stringify(plan, null, 2));
  process.exit(0);
}

if (rows.length === 0) {
  console.log(JSON.stringify({ ...plan, result: 'nothing to delete' }, null, 2));
  process.exit(0);
}

const workspaces = Object.fromEntries(rows.map((s) => [s.id, s.workspace]));
const result = await deleteSessions({ ids: rows.map((s) => s.id), workspaces, mode });
plan.result = result;
await writeFile(path.join(OUT_DIR, `delete-result-${stamp}.json`), JSON.stringify(plan, null, 2), 'utf8');
await appendFile(path.join(OUT_DIR, 'deletions.log'),
  `${plan.scannedAt}\t${mode}\tdeleted=${result.deleted}\tfailed=${result.failed}\tbytes=${result.freedBytes}\n`, 'utf8');
console.log(JSON.stringify({
  mode: result.mode,
  deleted: result.deleted,
  failed: result.failed,
  freedMiB: +(result.freedBytes / 1048576).toFixed(1),
  trashDir: result.results.find((r) => r.ok && r.trashDir)?.trashDir ?? null,
  failures: result.results.filter((r) => !r.ok).map((r) => ({ id: r.id, error: r.error })),
  logPath: path.join(OUT_DIR, `delete-result-${stamp}.json`),
}, null, 2));
