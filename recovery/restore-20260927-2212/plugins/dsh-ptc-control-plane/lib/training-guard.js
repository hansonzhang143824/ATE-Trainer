import crypto from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';
import { trainingAddressBook, trainingDftCommands } from './training-paths.js';
import { verifyTrainingPolicySync } from './training-materials.js';

const LABEL_PREFIX = 'PTC training dft expert ';
const DENIED = 'PTC training execution boundary: this child may access only its assigned training DFT input, products and verification paths.';
const NON_MATERIAL_TOOLS = new Set(['run_code', 'report', 'structured_output']);
const REVOKED = new Set();
const runKey = (root, runId) => `${path.resolve(root).toLowerCase()}|${runId}`;
export function revokeTrainingRun(workspaceRoot, runId) { REVOKED.add(runKey(workspaceRoot, runId)); }

function canonical(value) {
  if (Array.isArray(value)) return value.map(canonical);
  if (value && typeof value === 'object') {
    return Object.fromEntries(Object.keys(value).sort().map((key) => [key, canonical(value[key])]));
  }
  return value;
}

export function receiptDigest(receipt) {
  const { digest: _ignored, ...unsigned } = receipt;
  return crypto.createHash('sha256').update(JSON.stringify(canonical(unsigned))).digest('hex');
}

export function signTrainingReceipt(receipt) {
  return { ...receipt, digest: receiptDigest(receipt) };
}

export function verifyTrainingReceipt(receipt) {
  try { trainingAddressBook(receipt?.runId); } catch { return false; }
  return Boolean(receipt && receipt.schemaVersion === 1 && receipt.kind === 'ptc-training-dispatch'
    && typeof receipt.runId === 'string' && typeof receipt.label === 'string'
    && receipt.profileId === 'ptc-dft-expert' && Array.isArray(receipt.testItems)
    && receipt.testItems.length > 0 && receipt.testItems.every((tm) => typeof tm === 'string' && /^TM[0-9]+$/.test(tm))
    && receipt.label === trainingDispatchLabel(receipt.runId, receipt.testItems)
    && /^[a-f0-9]{64}$/.test(receipt.digest ?? '') && receipt.digest === receiptDigest(receipt));
}

function readReceipts(workspaceRoot) {
  const runs = path.join(workspaceRoot, 'Training_Materials', 'runs');
  let names;
  try { names = fs.readdirSync(runs); } catch { return []; }
  const receipts = [];
  for (const name of names) {
    const file = path.join(runs, name, 'dispatch.json');
    try {
      const receipt = JSON.parse(fs.readFileSync(file, 'utf8').replace(/^\uFEFF/, ''));
      receipts.push({ file, receipt, valid: verifyTrainingReceipt(receipt) && receipt.runId === name && safeAncestors(file) });
    } catch {}
  }
  return receipts;
}

function labelOf(agent) {
  const label = agent?.session?.events?.findLast?.((event) => event?.type === 'subagent/descriptor')?.data?.label;
  return typeof label === 'string' ? label : undefined;
}

function resolveIdentity(workspaceRoot, agent) {
  const label = labelOf(agent);
  const agentId = typeof agent?.id === 'string' ? agent.id : undefined;
  const all = readReceipts(workspaceRoot).filter(({ receipt }) => (typeof label === 'string' && label.length > 0 && receipt?.label === label)
    || (agentId && receipt?.childSessionId === agentId));
  if (!all.length && (typeof label !== 'string' || !label.startsWith(LABEL_PREFIX))) return { kind: 'unrelated' };
  if (all.length !== 1 || !all[0].valid) return { kind: 'mismatch', reason: 'missing, ambiguous or invalid training dispatch receipt' };
  const receipt = all[0].receipt;
  if (REVOKED.has(runKey(workspaceRoot, receipt.runId))) return { kind: 'mismatch', reason: 'training execution revoked in host memory; tool access revoked' };
  if (receipt.executionStatus === 'closed') return { kind: 'mismatch', reason: 'training execution has ended; tool access revoked' };
  if (typeof receipt.childSessionId !== 'string' || !receipt.childSessionId) {
    return { kind: 'mismatch', reason: 'training child identity is not yet bound' };
  }
  if (receipt.childSessionId !== agentId || receipt.label !== label) {
    return { kind: 'mismatch', reason: 'training dispatch receipt names a different child session' };
  }
  return { kind: 'training', receipt };
}

function safeAncestors(file) {
  let cursor = path.resolve(file);
  try {
    while (true) {
      const part = path.basename(cursor);
      if (part && (/^(?:con|prn|aux|nul|com[1-9]|lpt[1-9])(?:\.|$)/i.test(part)
          || /[. ]$/.test(part) || /[<>:"|?*]/.test(part))) return false;
      try {
        const stat = fs.lstatSync(cursor);
        if (stat.isSymbolicLink() || (stat.isFile() && stat.nlink > 1)) return false;
      } catch (error) { if (error.code !== 'ENOENT') return false; }
      const parent = path.dirname(cursor);
      if (parent === cursor) return true;
      cursor = parent;
    }
  } catch { return false; }
}

function realTarget(raw, cwd, existing) {
  if (typeof raw !== 'string' || raw.trim() === '') return null;
  const absolute = path.resolve(cwd, raw);
  if (!safeAncestors(absolute)) return null;
  try {
    if (existing || fs.existsSync(absolute)) return fs.realpathSync.native(absolute);
    let parent = path.dirname(absolute);
    const suffix = [path.basename(absolute)];
    while (!fs.existsSync(parent)) {
      const next = path.dirname(parent);
      if (next === parent) return null;
      suffix.unshift(path.basename(parent));
      parent = next;
    }
    return path.join(fs.realpathSync.native(parent), ...suffix);
  } catch { return null; }
}

function trainingDftDecision(exec, workspaceRoot, receipt) {
  if (!safeAncestors(workspaceRoot)) return DENIED;
  if (NON_MATERIAL_TOOLS.has(exec.name)) return undefined;
  try {
    if (!/^[a-f0-9]{64}$/.test(receipt.materialCacheKey ?? '')) return DENIED;
    verifyTrainingPolicySync(workspaceRoot, receipt.runId, receipt.materialCacheKey);
  } catch (error) { return `${DENIED} Frozen policy check failed: ${error.message}`; }
  const args = exec.arguments ?? {};
  const scope = new Set(receipt.testItems);
  const address = trainingAddressBook(receipt.runId);
  const root = fs.realpathSync.native(workspaceRoot);
  const same = (a, b) => process.platform === 'win32' ? a?.toLowerCase() === b?.toLowerCase() : a === b;
  const exactPhysical = (relative, exists = false) => same(realTarget(relative, root, exists), path.resolve(root, relative));
  if (!exactPhysical(address.runRoot, true) || !exactPhysical(address.workbook, true)) return DENIED;
  if (exec.name === 'pwsh') {
    const command = typeof args.command === 'string' ? args.command.trim() : '';
    if (args.workdir || args.run_in_background || args.sandbox_permissions) return DENIED;
    const sha = /--expected-sha ([a-f0-9]{64})(?: |$)/.exec(command)?.[1] ?? '0'.repeat(64);
    const permitted = [...scope].some((tm) => {
      if (!['dft-meta.json', 'dft-conditions.yaml', 'dft-semantic-review.json'].every((name) => exactPhysical(`${address.dftRoot}/${tm}/${name}`))) return false;
      return Object.values(trainingDftCommands(address, tm, sha)).includes(command);
    });
    return permitted ? undefined : DENIED;
  }
  if (exec.name !== 'read' && exec.name !== 'write') return DENIED;
  const cwd = exec.agent?.session?.header?.cwd ?? workspaceRoot;
  const target = realTarget(args.file_path, cwd, exec.name === 'read');
  if (target === null) return DENIED;
  const outputNames = new Set(['dft-meta.json', 'dft-conditions.yaml', 'dft-semantic-review.json']);
  const outputAllowed = [...scope].some((tm) => [...outputNames].some((name) => same(target, path.resolve(root, `${address.dftRoot}/${tm}/${name}`))));
  const verification = path.resolve(root, address.verificationRoot);
  const namedTms = (path.basename(target).match(/TM[0-9]+/gi) ?? []).map((tm) => tm.toUpperCase());
  const verificationAllowed = same(path.dirname(target), verification) && /^dft-[A-Za-z0-9._-]+\.json$/.test(path.basename(target))
    && namedTms.length > 0 && namedTms.every((tm) => scope.has(tm));
  const inputAllowed = [address.workbook, address.sourceView, address.special, address.rules, address.instructions]
    .some((file) => same(target, path.resolve(root, file)));
  if (exec.name === 'read') return inputAllowed || outputAllowed || verificationAllowed ? undefined : DENIED;
  return outputAllowed || verificationAllowed ? undefined : DENIED;
}

export function trainingGuardDecision(exec, workspaceRoot) {
  const identity = resolveIdentity(path.resolve(workspaceRoot), exec.agent);
  if (identity.kind === 'unrelated') return undefined;
  if (identity.kind === 'mismatch') return `PTC training execution identity: ${identity.reason}.`;
  return trainingDftDecision(exec, path.resolve(workspaceRoot), identity.receipt);
}

export function trainingDispatchLabel(runId, testItems) {
  return `${LABEL_PREFIX}[${testItems.join(',')}] ${runId}`;
}
