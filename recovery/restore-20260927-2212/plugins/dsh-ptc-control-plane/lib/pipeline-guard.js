import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { assertSafeRunPath } from './run-context.js';
import { receiptDigest, signTrainingReceipt } from './training-guard.js';
import { trainingAddressBook } from './training-paths.js';

const PREFIX = 'PTC training stage ';
const REVOKED = new Set();
const STAGE_FOLDERS = {
  STRATEGY: 'strategy', METHOD: 'method', RULE_REVIEW_METHOD: 'review',
  IMPLEMENTATION: 'implementation', RULE_REVIEW_IMPLEMENTATION: 'review', COMPILE: 'compile',
};
const key = (root, id) => `${path.resolve(root).toLowerCase()}|${id}`;
const same = (a, b) => process.platform === 'win32' ? a.toLowerCase() === b.toLowerCase() : a === b;
const inside = (file, directory) => {
  const relative = path.relative(directory, file);
  return relative === '' || (relative !== '..' && !relative.startsWith(`..${path.sep}`) && !path.isAbsolute(relative));
};
const readJson = file => JSON.parse(fs.readFileSync(file, 'utf8').replace(/^\uFEFF/, ''));

export function stageDispatchLabel(runId, stage, role) { return `${PREFIX}${runId} ${stage} ${role}`; }
export function revokeStageDispatch(root, dispatchId) { REVOKED.add(key(root, dispatchId)); }
export function signStageReceipt(value) { return signTrainingReceipt(value); }

/** A restarted host never inherits an old child's still-open authority. */
export function reconcileStageReceipts(workspaceRoot) {
  const root = path.resolve(workspaceRoot);
  const closed = [];
  let runs;
  try { runs = fs.readdirSync(assertSafeRunPath(root, 'Training_Materials/runs')); } catch { return closed; }
  for (const runId of runs) {
    let directory, names;
    try {
      directory = assertSafeRunPath(root, path.join(trainingAddressBook(runId).runRoot, 'receipts'));
      names = fs.readdirSync(directory);
    } catch { continue; }
    for (const name of names.filter(name => name.endsWith('.json'))) {
      try {
        const file = assertSafeRunPath(root, path.join(directory, name));
        const receipt = readJson(file);
        if (receipt.kind !== 'ptc-training-stage' || receipt.runId !== runId || receipt.digest !== receiptDigest(receipt)) continue;
        revokeStageDispatch(root, receipt.dispatchId);
        if (receipt.executionStatus === 'closed') continue;
        const temporary = `${file}.${crypto.randomUUID()}.tmp`;
        fs.writeFileSync(temporary, JSON.stringify(signStageReceipt({ ...receipt, executionStatus: 'closed',
          closeReason: 'host_restart', closedAt: new Date().toISOString() }), null, 2) + '\n', { flag: 'wx' });
        try { fs.renameSync(temporary, file); } finally { if (fs.existsSync(temporary)) fs.unlinkSync(temporary); }
        closed.push(receipt.dispatchId);
      } catch { /* Missing/corrupt receipts remain denied by the live guard. */ }
    }
  }
  return closed;
}

function validReceipt(root, file, receipt) {
  trainingAddressBook(receipt.runId);
  if (receipt.schemaVersion !== 1 || receipt.kind !== 'ptc-training-stage'
      || receipt.digest !== receiptDigest(receipt) || !Array.isArray(receipt.testItems)
      || !receipt.testItems.length || receipt.testItems.some(tm => !/^TM\d+$/.test(tm))
      || !/^[a-z][a-z0-9-]{1,63}$/.test(receipt.role)
      || receipt.dispatchId !== `${receipt.runId}:${receipt.stage}:${receipt.role}:1`
      || receipt.label !== stageDispatchLabel(receipt.runId, receipt.stage, receipt.role)) return false;
  const runRoot = path.join(root, trainingAddressBook(receipt.runId).runRoot);
  if (!same(path.dirname(file), path.join(runRoot, 'receipts'))) return false;
  const registryFile = assertSafeRunPath(root, path.join(runRoot, 'pipeline-registry.json'));
  const registry = readJson(registryFile);
  if (receipt.registryDigest !== crypto.createHash('sha256').update(fs.readFileSync(registryFile)).digest('hex')) return false;
  const context = readJson(assertSafeRunPath(root, path.join(runRoot, 'run.json')));
  if (context.mode !== 'training' || context.runId !== receipt.runId || context.releaseId !== null) return false;
  const materials = readJson(assertSafeRunPath(root, path.join(runRoot, 'pipeline-material-manifest.json')));
  if (materials.runId !== receipt.runId || materials.pipelineCacheKey !== receipt.pipelineCacheKey
      || materials.ownerProfiles?.[receipt.role] !== receipt.profileId
      || JSON.stringify([...materials.testItems].sort()) !== JSON.stringify([...receipt.testItems].sort())) return false;
  const profileRelative = materials.addressBook?.profileRoots?.[receipt.profileId];
  if (typeof profileRelative !== 'string') return false;
  const profile = assertSafeRunPath(root, path.join(root, profileRelative, 'instructions.md'));
  if (!inside(profile, path.join(runRoot, 'profiles'))) return false;
  const profileEntry = materials.files?.find(entry => same(path.resolve(root, entry.snapshotPath), profile));
  if (!profileEntry || profileEntry.sha256 !== receipt.profileSha256
      || crypto.createHash('sha256').update(fs.readFileSync(profile)).digest('hex') !== receipt.profileSha256) return false;
  const definition = registry.stages?.[receipt.stage];
  if (!registry.stateMachine?.includes(receipt.stage) || !definition) return false;
  const allowedRole = receipt.stage === 'INPUT_SYNC'
    ? ['dft-expert', 'schematic-expert'].includes(receipt.role) : definition.owner === receipt.role;
  return allowedRole && receipt.gate === definition.gate;
}

/** Additional deny-only guard for generic pipeline children, separate from DFT. */
export function pipelineGuardDecision(exec, workspaceRoot) {
  const root = path.resolve(workspaceRoot);
  const label = exec.agent?.session?.events?.findLast?.(event => event?.type === 'subagent/descriptor')?.data?.label;
  const id = exec.agent?.id;
  const matches = [];
  try {
    const runs = assertSafeRunPath(root, path.join(root, 'Training_Materials/runs'));
    for (const runId of fs.readdirSync(runs)) {
      let files;
      try { files = fs.readdirSync(assertSafeRunPath(root, path.join(runs, runId, 'receipts'))); } catch { continue; }
      for (const name of files.filter(name => name.endsWith('.json'))) {
        try {
          const file = assertSafeRunPath(root, path.join(runs, runId, 'receipts', name));
          const receipt = readJson(file);
          if ((typeof label === 'string' && label.length > 0 && receipt.label === label)
            || (typeof id === 'string' && id.length > 0 && receipt.childSessionId === id)) matches.push({ file, receipt });
        } catch {}
      }
    }
  } catch {}
  if (!matches.length && !String(label ?? '').startsWith(PREFIX)) return undefined;
  const denied = 'PTC pipeline training boundary: missing, closed, mismatched or out-of-scope stage authority';
  if (matches.length !== 1) return denied;
  const { receipt, file } = matches[0];
  try {
    if (!validReceipt(root, file, receipt) || REVOKED.has(key(root, receipt.dispatchId))
        || receipt.executionStatus === 'closed' || !receipt.childSessionId
        || receipt.childSessionId !== id || receipt.label !== label) return denied;
    if (['run_code', 'report', 'structured_output'].includes(exec.name)) return undefined;
    // The host runs gates and deterministic source parsers. Generic stage
    // children cannot turn free-form shell commands into filesystem authority.
    if (!['read', 'write'].includes(exec.name)) return denied;
    const runRoot = path.join(root, trainingAddressBook(receipt.runId).runRoot);
    const cwd = exec.agent?.session?.header?.cwd ?? root;
    const target = assertSafeRunPath(root, path.resolve(cwd, exec.arguments?.file_path ?? ''));
    const inFolder = name => inside(target, path.join(runRoot, name));
    const sourceRole = receipt.stage === 'INPUT_SYNC';
    const readAllowed = sourceRole ? ['input', 'input-sync/schematic'].some(inFolder)
      : ['input', 'input-sync', 'knowledge', 'rules', 'register', 'profiles', 'vs-project', 'vs-baseline'].some(inFolder)
      || receipt.testItems.some(tm => inFolder(`trials/${tm.toLowerCase()}`));
    if (exec.name === 'read') return readAllowed ? undefined : denied;
    if (sourceRole) return denied;
    const folder = STAGE_FOLDERS[receipt.stage];
    const stageOutput = folder && receipt.testItems.some(tm => inFolder(`trials/${tm.toLowerCase()}/${folder}`))
      && /\.(json|md|txt|yaml)$/i.test(target)
      && (receipt.stage !== 'RULE_REVIEW_METHOD' || path.basename(target).startsWith('method-'))
      && (receipt.stage !== 'RULE_REVIEW_IMPLEMENTATION' || path.basename(target).startsWith('implementation-'));
    const sourceWrite = receipt.stage === 'IMPLEMENTATION' && inFolder('vs-project')
      && /\.(cpp|h|hpp|spec|treg)$/i.test(target) && fs.existsSync(target);
    return stageOutput || sourceWrite ? undefined : denied;
  } catch { return denied; }
}
