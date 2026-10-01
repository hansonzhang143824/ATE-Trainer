import fs from 'node:fs';
import path from 'node:path';
import { createHash, randomUUID } from 'node:crypto';
import { assetPath, validateProjectFiles } from './trainer-schema.js';

export const trainerSha = (value) => createHash('sha256').update(value).digest('hex');
export const trainerJson = (value) => `${JSON.stringify(value, null, 2)}\n`;
export function trainerFail(code, message, details) { throw Object.assign(new Error(message), { code, details }); }
export const AGENT_ID_LEDGER_PATH = 'contracts/agent-ids.json';
const trainerIdPattern = /^[A-Za-z0-9][A-Za-z0-9_-]{0,127}$/;
const reservedTrainerId = /^(con|prn|aux|nul|com[1-9]|lpt[1-9])$/i;
function isTrainerId(id) { return typeof id === 'string' && trainerIdPattern.test(id) && !reservedTrainerId.test(id); }
export function trainerId(id) {
  if (!isTrainerId(id)) trainerFail('TRAINER_INVALID_ID', 'invalid identifier');
  return id;
}
function inspectAgentIdLedger(content) {
  let value;
  try { value = JSON.parse(content); } catch { return { ok: false, reason: 'invalid JSON' }; }
  if (!value || typeof value !== 'object' || Array.isArray(value) || value.schemaVersion !== 1) return { ok: false, reason: 'schemaVersion must be 1' };
  if (!Array.isArray(value.allocated)) return { ok: false, reason: 'allocated must be an array' };
  const invalid = value.allocated.filter((id) => !isTrainerId(id));
  if (invalid.length) return { ok: false, reason: 'allocated contains invalid IDs', invalid };
  const duplicate = value.allocated.find((id, index) => value.allocated.indexOf(id) !== index);
  if (duplicate !== undefined) return { ok: false, reason: 'allocated contains duplicate IDs', duplicate };
  return { ok: true, data: { schemaVersion: 1, allocated: [...value.allocated] } };
}
export function parseAgentIdLedger(content) {
  const result = inspectAgentIdLedger(content);
  if (!result.ok) trainerFail('TRAINER_AGENT_ID_LEDGER_INVALID', `Agent ID ledger is invalid: ${result.reason}`, result);
  return result.data;
}
/** Check every existing ancestor; new paths may not escape through junctions. */
export function trainerSafe(root, ...parts) {
  const base = path.resolve(root); const target = path.resolve(base, ...parts); const rel = path.relative(base, target);
  if (rel === '..' || rel.startsWith(`..${path.sep}`) || path.isAbsolute(rel)) trainerFail('TRAINER_UNSAFE_PATH', 'path escapes root');
  let cursor = target;
  while (true) {
    try { const stat = fs.lstatSync(cursor); if (stat.isSymbolicLink() || (stat.isFile() && stat.nlink !== 1)) trainerFail('TRAINER_UNSAFE_PATH', 'links and hardlinks are forbidden'); }
    catch (e) { if (e.code !== 'ENOENT') throw e; }
    const parent = path.dirname(cursor); if (parent === cursor) break; cursor = parent;
  }
  return target;
}
export function trainerRead(root, ...parts) { return JSON.parse(fs.readFileSync(trainerSafe(root, ...parts), 'utf8')); }
export function trainerWrite(root, relative, data, { replace = false } = {}) {
  const target = trainerSafe(root, relative); fs.mkdirSync(path.dirname(target), { recursive: true }); trainerSafe(root, relative);
  if (!replace) { fs.writeFileSync(target, data, { flag: 'wx' }); return; }
  const temporary = `${target}.${randomUUID()}.tmp`;
  try { fs.writeFileSync(temporary, data, { flag: 'wx' }); trainerSafe(root, relative); fs.renameSync(temporary, target); }
  finally { if (fs.existsSync(temporary)) fs.unlinkSync(temporary); }
}
export function trainerLock(root, callback) {
  trainerSafe(root); fs.mkdirSync(root, { recursive: true });
  const lock = trainerSafe(root, '.trainer.lock'); let fd;
  try { fd = fs.openSync(lock, 'wx'); } catch (e) { if (e.code === 'EEXIST') trainerFail('TRAINER_BUSY', 'another project operation is in progress'); throw e; }
  try { return callback(); } finally { fs.closeSync(fd); fs.unlinkSync(lock); }
}
export const trainerProjectRoot = (root, projectId) => trainerSafe(root, 'Training_Materials', 'framework', 'projects', trainerId(projectId));
function check(files, { allowInvalidLedger = false } = {}) {
  const result = validateProjectFiles(files);
  // applyChanges reports the ledger-specific error after this structural check;
  // project initialization keeps the normal generic validation behavior.
  const errors = allowInvalidLedger ? result.errors.filter((entry) => entry.path !== AGENT_ID_LEDGER_PATH) : result.errors;
  if (errors.length) trainerFail('TRAINER_PROJECT_INVALID', 'candidate validation failed', errors);
  return { ...result, ok: true, errors };
}
function newAgentIds(base, next) {
  const ids = [];
  for (const p of Object.keys(next)) {
    const match = p.match(/^agents\/([^/]+)\/agent\.json$/);
    if (match && !Object.hasOwn(base, p)) ids.push(match[1]);
  }
  return [...new Set(ids)];
}
function ledgerOnlyChange(changes) { return changes.length === 1 && changes[0].path === AGENT_ID_LEDGER_PATH; }
function checkAgentIdLedger(base, next, changes) {
  const nextHasLedger = Object.hasOwn(next, AGENT_ID_LEDGER_PATH);
  const nextLedger = nextHasLedger ? parseAgentIdLedger(next[AGENT_ID_LEDGER_PATH]) : null;
  const baseHasLedger = Object.hasOwn(base, AGENT_ID_LEDGER_PATH);
  const newAgents = newAgentIds(base, next);
  if (!baseHasLedger) {
    if (newAgents.length) trainerFail('TRAINER_AGENT_ID_LEDGER_MISSING', 'Agent ID ledger must be initialized in a separate commit before creating Agents', { ids: newAgents });
    if (!ledgerOnlyChange(changes) || !nextLedger) trainerFail('TRAINER_AGENT_ID_LEDGER_MISSING', 'When the base has no Agent ID ledger, the only allowed commit is a standalone ledger initialization');
    return;
  }
  const baseInspection = inspectAgentIdLedger(base[AGENT_ID_LEDGER_PATH]);
  if (!baseInspection.ok) {
    if (ledgerOnlyChange(changes) && nextLedger) return;
    trainerFail('TRAINER_AGENT_ID_LEDGER_INVALID', 'Agent ID ledger is damaged; submit a standalone ledger repair first', baseInspection);
  }
  const baseLedger = baseInspection.data;
  if (!nextLedger) trainerFail('TRAINER_AGENT_ID_LEDGER_SHRINK', 'Agent ID ledger cannot be deleted');
  const baseIds = new Set(baseLedger.allocated); const nextIds = new Set(nextLedger.allocated);
  if (baseLedger.allocated.some((id) => !nextIds.has(id))) trainerFail('TRAINER_AGENT_ID_LEDGER_SHRINK', 'Agent ID ledger allocated entries are append-only');
  const reused = newAgents.filter((id) => baseIds.has(id));
  if (reused.length) trainerFail('TRAINER_AGENT_ID_REUSED', 'Agent ID was already allocated and cannot be reused', { ids: reused });
  const unregistered = newAgents.filter((id) => !nextIds.has(id));
  if (unregistered.length) trainerFail('TRAINER_AGENT_ID_UNREGISTERED', 'New Agent IDs must be registered in the same change set', { ids: unregistered });
}
function writeRevision(directory, revisionId, files, transaction = null) {
  const entries = [];
  for (const p of Object.keys(files).sort()) {
    const bytes = Buffer.from(files[p]);
    trainerWrite(directory, `revisions/${revisionId}/${p}`, bytes);
    entries.push({ path: p, size: bytes.length, sha256: trainerSha(bytes) });
  }
  trainerWrite(directory, `revisions/${revisionId}/revision.json`, trainerJson({ revisionId, files: entries, transaction }));
}
export function ensureTrainerProject(root, { projectId, seed } = {}) {
  const directory = trainerProjectRoot(root, projectId);
  return trainerLock(directory, () => {
    if (fs.existsSync(trainerSafe(directory, 'current.json'))) return readProject(root, { projectId });
    // A product project starts blank.  Synthetic fixtures are test material
    // and must be injected explicitly by a caller through `seed`; silently
    // creating one here would expose historical/demo Agents in the live
    // Trainer registry.
    const files = seed?.files ?? {}; check(files);
    const revisionId = `revision-${randomUUID()}`;
    writeRevision(directory, revisionId, files);
    const project = { projectId, schemaVersion: 1, runtimeApiVersion: 'trainer-api-v1' };
    trainerWrite(directory, 'project.json', trainerJson(project), { replace: true });
    trainerWrite(directory, 'current.json', trainerJson({ revisionId }), { replace: true });
    return readProject(root, { projectId });
  });
}
export function readAssets(root, { projectId, revisionId, paths } = {}) {
  const directory = trainerProjectRoot(root, projectId);
  revisionId ??= trainerRead(directory, 'current.json').revisionId; trainerId(revisionId);
  const manifest = trainerRead(directory, 'revisions', revisionId, 'revision.json');
  const files = Object.create(null);
  for (const entry of manifest.files) {
    if (!assetPath(entry.path)) trainerFail('TRAINER_INTEGRITY', 'invalid revision file path');
    const bytes = fs.readFileSync(trainerSafe(directory, 'revisions', revisionId, entry.path));
    if (bytes.length !== entry.size || trainerSha(bytes) !== entry.sha256) trainerFail('TRAINER_INTEGRITY', 'candidate file digest mismatch', { path: entry.path });
    if (!paths || paths.includes(entry.path)) files[entry.path] = bytes.toString('utf8');
  }
  if (paths?.some((p) => !Object.hasOwn(files, p))) trainerFail('TRAINER_ASSET_NOT_FOUND', 'requested asset not found');
  return { projectId, revisionId, files };
}
export function readProject(root, { projectId } = {}) {
  const project = trainerRead(trainerProjectRoot(root, projectId), 'project.json');
  const { revisionId, files } = readAssets(root, { projectId });
  const agents = []; const workflows = [];
  for (const [p, content] of Object.entries(files)) {
    if (/^agents\/[^/]+\/agent.json$/.test(p)) { const a = JSON.parse(content); agents.push({ agentId: a.agentId, name: a.name, revisionId }); }
    if (/^workflows\/[^/]+\.json$/.test(p)) { const w = JSON.parse(content); workflows.push({ workflowId: w.workflowId, name: w.name ?? w.workflowId, revisionId }); }
  }
  return { ...project, revisionId, agents, workflows };
}
export function readChangeSet(root, { projectId, changeSetId } = {}) { return trainerRead(trainerProjectRoot(root, projectId), 'changes', `${trainerId(changeSetId)}.json`); }
export function applyChanges(root, input) {
  const { projectId, requestId, baseRevision, changes, reason, linkedRunId = null } = input;
  trainerId(requestId); trainerId(baseRevision);
  if (!Array.isArray(changes) || !changes.length || typeof reason !== 'string' || !reason.trim()) trainerFail('TRAINER_INVALID_CHANGE', 'changes and reason required');
  const directory = trainerProjectRoot(root, projectId);
  const fingerprint = trainerSha(trainerJson({ baseRevision, changes, reason, linkedRunId }));
  return trainerLock(directory, () => {
    const current = trainerRead(directory, 'current.json');
    // Finish the previous committed transaction before another one can replace
    // its pointer. This keeps replay durable even after a receipt-write failure.
    if (current.requestId && !fs.existsSync(trainerSafe(directory, `requests/${trainerId(current.requestId)}.json`))) {
      const prior = readChangeSet(root, { projectId, changeSetId: current.changeSetId });
      trainerWrite(directory, `requests/${current.requestId}.json`, trainerJson({ fingerprint: current.fingerprint, result: prior.result }));
    }
    const receiptPath = `requests/${requestId}.json`;
    if (fs.existsSync(trainerSafe(directory, receiptPath))) {
      const receipt = trainerRead(directory, receiptPath);
      if (receipt.fingerprint !== fingerprint) trainerFail('TRAINER_REQUEST_CONFLICT', 'requestId reused with different content');
      return receipt.result;
    }
    // The current pointer is the commit point. Recover the receipt after a crash
    // between pointer replacement and receipt persistence without applying twice.
    if (current.requestId === requestId) {
      if (current.fingerprint !== fingerprint) trainerFail('TRAINER_REQUEST_CONFLICT', 'requestId reused with different content');
      const change = readChangeSet(root, { projectId, changeSetId: current.changeSetId });
      return change.result;
    }
    if (current.revisionId !== baseRevision) trainerFail('TRAINER_REVISION_CONFLICT', 'candidate changed; reload before saving', { expected: baseRevision, actual: current.revisionId });
    const { files } = readAssets(root, { projectId, revisionId: baseRevision }); const diff = []; const seen = new Set();
    for (const change of changes) {
      if (!assetPath(change.path) || seen.has(change.path) || (change.content !== null && typeof change.content !== 'string')) trainerFail('TRAINER_INVALID_CHANGE', 'invalid or duplicate change path/content');
      seen.add(change.path);
      const before = files[change.path];
      if (change.content === null) delete files[change.path]; else files[change.path] = change.content;
      if (before !== change.content && !(before === undefined && change.content === null)) diff.push({ path: change.path, oldSha256: before === undefined ? null : trainerSha(Buffer.from(before)), newSha256: change.content === null ? null : trainerSha(Buffer.from(change.content)), before: before ?? null, after: change.content, kind: change.path.startsWith('contracts/') || change.path.startsWith('tests/') ? 'validation' : 'asset' });
    }
    const validation = check(files, { allowInvalidLedger: true });
    checkAgentIdLedger(readAssets(root, { projectId, revisionId: baseRevision }).files, files, changes);
    const revisionId = diff.length ? `revision-${randomUUID()}` : baseRevision; const changeSetId = `change-${randomUUID()}`;
    const result = { projectId, revisionId, changeSetId, diff, validation };
    if (diff.length) writeRevision(directory, revisionId, files, { requestId, fingerprint, changeSetId });
    trainerWrite(directory, `changes/${changeSetId}.json`, trainerJson({ schemaVersion: 1, projectId, changeSetId, baseRevision, appliedRevision: revisionId, requestId, reason, linkedRunId, result }));
    trainerWrite(directory, 'current.json', trainerJson({ revisionId, changeSetId, requestId, fingerprint }), { replace: true });
    trainerWrite(directory, receiptPath, trainerJson({ fingerprint, result }));
    return result;
  });
}
