import crypto from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';

const CONTRACT_PREFIX = 'team/artifacts/';
const IMPLEMENTATION_LABEL = /^PTC implementation expert \[(TM\d+)\] contract=([^#]+)#([a-f0-9]{64}) recipe=([A-Za-z0-9_-]+)$/;

function sha256(bytes) { return crypto.createHash('sha256').update(bytes).digest('hex'); }
function inside(candidate, root) {
  const relative = path.relative(root, candidate);
  return relative === '' || (relative !== '..' && !relative.startsWith(`..${path.sep}`) && !path.isAbsolute(relative));
}
function stable(value) {
  if (Array.isArray(value)) return value.map(stable);
  if (value && typeof value === 'object') return Object.fromEntries(Object.keys(value).sort().map((key) => [key, stable(value[key])]));
  return value;
}
function encoded(value) { return Buffer.from(JSON.stringify(stable(value))).toString('base64url'); }
function decode(value) {
  try { return JSON.parse(Buffer.from(value, 'base64url').toString('utf8')); } catch { return null; }
}
function relativeContract(root, contractPath) { return path.relative(root, contractPath).split(path.sep).join('/'); }
function selectedSources(boundary) {
  if (boundary?.sourceTablesByEndpoint && typeof boundary.sourceTablesByEndpoint === 'object') return Object.values(boundary.sourceTablesByEndpoint).filter((x) => typeof x === 'string' && x);
  return (boundary?.allocations || []).filter((row) => row?.selectionState === 'SELECTED').map((row) => row.sourceTable).filter((x) => typeof x === 'string' && x);
}
function selectedRelays(boundary) {
  if (Array.isArray(boundary?.setOnRelayUnion)) return boundary.setOnRelayUnion.map((x) => String(x));
  if (Array.isArray(boundary?.functionalRelayIds)) return boundary.functionalRelayIds.map((x) => String(x));
  return [...new Set((boundary?.allocations || []).flatMap((row) => (row?.functionalRelays || []).filter((relay) => relay?.state === 'ON').map((relay) => String(relay.id))))];
}

/** Derive the only implementation recipe permitted by a signed method contract. */
export function deriveImplementationRecipe(contract, contractPath, root) {
  const errors = [];
  const tm = contract?.tm;
  const family = contract?.methodFamily;
  const boundary = contract?.resourceBoundary;
  const measurement = contract?.measurementPlan;
  const shutdown = contract?.powerDownPlan;
  if (!/^TM\d+$/.test(tm || '')) errors.push('tm');
  if (!['direct_measurement', 'scan', 'trim'].includes(family)) errors.push('methodFamily');
  const sourceTables = selectedSources(boundary);
  if (!sourceTables.length) errors.push('resourceBoundary.sourceTables');
  const functionalRelays = selectedRelays(boundary);
  if (!functionalRelays.length) errors.push('resourceBoundary.functionalRelays');
  if (!measurement || typeof measurement !== 'object') errors.push('measurementPlan');
  if (!shutdown || typeof shutdown !== 'object' || !(Array.isArray(shutdown.actions) || Array.isArray(shutdown.normalSequence))) errors.push('powerDownPlan');
  const registerWrites = boundary?.registerConfiguration?.orderedWrites || boundary?.registerDelta || [];
  if (!Array.isArray(registerWrites)) errors.push('resourceBoundary.registerConfiguration');
  const recipe = {
    version: 1,
    tm,
    methodContractPath: relativeContract(root, contractPath),
    methodContractSha256: sha256(fs.readFileSync(contractPath)),
    family,
    sourceTables,
    functionalRelays,
    relaySettleMs: 3,
    registerWrites,
    measurement,
    shutdown: { plan: shutdown, zeroBeforeRelayOff: true },
  };
  if (family === 'scan') {
    const sweeps = measurement?.sweeps;
    if (!Array.isArray(sweeps) || !sweeps.length) errors.push('measurementPlan.sweeps');
    recipe.sweeps = sweeps || [];
  }
  if (family === 'trim') {
    const trim = measurement?.trimExecution;
    const callback = trim?.callback;
    const treg = trim?.treg;
    if (!trim?.required || !trim?.node || !trim?.executeCallPrefix) errors.push('measurementPlan.trimExecution');
    if (!callback?.sourcePath || !callback?.symbol || !callback?.measurementSourceTable || callback?.resultUnit !== 'mV') errors.push('measurementPlan.trimExecution.callback');
    if (!treg?.sourcePath || !treg?.key || !Number.isFinite(treg?.targetMillivolts) || !Number.isFinite(treg?.stepCount) || !treg?.i2cAddress || !treg?.bitRange) errors.push('measurementPlan.trimExecution.treg');
    recipe.trim = trim;
  }
  return { recipe, errors };
}

export function createImplementationDescriptor(root, contractPath) {
  const absolute = path.resolve(root, contractPath);
  const bytes = fs.readFileSync(absolute);
  const contract = JSON.parse(bytes.toString('utf8'));
  const { recipe, errors } = deriveImplementationRecipe(contract, absolute, root);
  if (errors.length) throw new Error(`implementation contract incomplete: ${errors.join(', ')}`);
  return `PTC implementation expert [${recipe.tm}] contract=${recipe.methodContractPath}#${recipe.methodContractSha256} recipe=${encoded(recipe)}`;
}

/** Validate the Hook descriptor and return its exact allowed recipe/scope. */
export function implementationScope(agent, root) {
  const label = agent?.session?.events?.findLast((event) => event.type === 'subagent/descriptor')?.data?.label;
  const match = typeof label === 'string' ? IMPLEMENTATION_LABEL.exec(label) : null;
  if (!match) return null;
  const [, tm, relative, contractSha, token] = match;
  if (!relative.startsWith(CONTRACT_PREFIX) || relative.includes('..')) return { error: 'implementation descriptor contract path is outside team/artifacts' };
  const contractPath = path.resolve(root, relative);
  if (!inside(contractPath, path.resolve(root, 'team', 'artifacts')) || !fs.existsSync(contractPath)) return { error: 'implementation descriptor contract is missing' };
  let contract;
  try { contract = JSON.parse(fs.readFileSync(contractPath, 'utf8')); } catch { return { error: 'implementation descriptor contract is unreadable' }; }
  const { recipe, errors } = deriveImplementationRecipe(contract, contractPath, root);
  if (contract?.tm !== tm || errors.length) return { error: `implementation contract incomplete: ${errors.join(', ') || 'tm mismatch'}` };
  if (recipe.methodContractSha256 !== contractSha) return { error: 'implementation descriptor contract hash is stale' };
  const sentRecipe = decode(token);
  if (JSON.stringify(stable(sentRecipe)) !== JSON.stringify(stable(recipe))) return { error: 'implementation descriptor recipe does not match signed contract' };
  const trial = path.dirname(path.dirname(contractPath));
  return { recipe, contractPath, trial, sourceFiles: new Set([
    'D:/PROJECT6-DALI/ForCodexDebug/source/test.cpp',
    'D:/PROJECT6-DALI/ForCodexDebug/source/sub.cpp',
    'D:/PROJECT6-DALI/ForCodexDebug/source/Pin_Channel_define.h',
    'D:/PROJECT6-DALI/ForCodexDebug/source/StdAfx.h',
    'D:/PROJECT6-DALI/ForCodexDebug/NU1201.treg',
  ].map((value) => path.resolve(value))) };
}

export function isImplementationLabel(label) { return typeof label === 'string' && (label.startsWith('PTC implementation expert') || label === 'ate-implementer'); }
