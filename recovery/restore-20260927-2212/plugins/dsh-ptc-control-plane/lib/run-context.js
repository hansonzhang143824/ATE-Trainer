import fs from 'node:fs';
import path from 'node:path';

const RUN_ID = /^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$/;
const MODE = new Set(['training', 'delivery']);

function requireId(value, name) {
  if (typeof value !== 'string' || !RUN_ID.test(value) || /[. ]$/.test(value)
      || /^(?:con|prn|aux|nul|com[1-9]|lpt[1-9])(?:\.|$)/i.test(value)) {
    throw new Error(`${name} must match ${RUN_ID}`);
  }
  return value;
}

function requireMode(value) {
  if (!MODE.has(value)) throw new Error('mode must be training or delivery');
  return value;
}

function relative(root, absolute) {
  const result = path.relative(root, absolute);
  if (result === '' || (!result.startsWith(`..${path.sep}`) && result !== '..' && !path.isAbsolute(result))) {
    return result;
  }
  throw new Error(`path escapes the workspace: ${absolute}`);
}

function deepFreeze(value) {
  if (value && typeof value === 'object' && !Object.isFrozen(value)) {
    Object.freeze(value);
    for (const item of Object.values(value)) deepFreeze(item);
  }
  return value;
}

/** Validate lexical ownership and every existing ancestor without following links. */
export function assertSafeRunPath(workspaceRoot, candidatePath) {
  const root = path.resolve(workspaceRoot);
  if (typeof candidatePath !== 'string' || candidatePath.trim() === '') throw new Error('invalid run target path');
  const candidate = path.resolve(root, candidatePath);
  relative(root, candidate);
  let cursor = candidate;
  while (true) {
    const part = path.basename(cursor);
    if (part && (/[. ]$/.test(part) || /[<>:"|?*]/.test(part)
        || /^(?:con|prn|aux|nul|com[1-9]|lpt[1-9])(?:\.|$)/i.test(part))) throw new Error('unsafe Windows run path');
    try {
      const stat = fs.lstatSync(cursor);
      if (stat.isSymbolicLink()) throw new Error('run path contains a symbolic link or junction');
      if (stat.isFile() && stat.nlink > 1) throw new Error('run path contains a hard-linked file');
    } catch (error) { if (error.code !== 'ENOENT') throw error; }
    const parent = path.dirname(cursor);
    if (parent === cursor) break;
    cursor = parent;
  }
  return candidate;
}

function validateContext(root, context) {
  if (!context || typeof context !== 'object' || context.schemaVersion !== 1
      || typeof context.createdAt !== 'string' || !Number.isFinite(Date.parse(context.createdAt))) throw new Error('invalid run context identity');
  const expected = createRunContext(root, context);
  for (const key of ['mode', 'runId', 'releaseId', 'projectId', 'profileSource', 'orchestrationSource']) {
    if (context[key] !== expected[key]) throw new Error(`invalid run context ${key}`);
  }
  if (typeof context.artifactRoot !== 'string' || path.isAbsolute(context.artifactRoot)
      || context.artifactRoot.split(/[\\/]/).some((part) => part === '.' || part === '..')
      || !same(path.resolve(root, context.artifactRoot), path.resolve(root, expected.artifactRoot))) throw new Error('invalid run context artifactRoot');
  return expected;
}

/**
 * Build the immutable identity carried by one run.
 *
 * This object replaces the legacy process-wide `activeMode`. It contains no
 * mutable pointer: a delivery run keeps its release even after a newer release
 * becomes active, and a training run can never turn into a delivery run.
 */
export function createRunContext(workspaceRoot, input) {
  const root = path.resolve(workspaceRoot);
  assertSafeRunPath(root, root);
  const mode = requireMode(input?.mode);
  const runId = requireId(input?.runId, 'runId');
  const createdAt = typeof input?.createdAt === 'string' ? input.createdAt : new Date().toISOString();
  if (!Number.isFinite(Date.parse(createdAt))) throw new Error('invalid run createdAt');

  if (mode === 'training') {
    if (input?.releaseId !== undefined && input.releaseId !== null) {
      throw new Error('training runs cannot bind releaseId');
    }
    if (input?.projectId !== undefined && input.projectId !== null) {
      throw new Error('training runs cannot bind projectId');
    }
    const artifactRoot = path.join(root, 'Training_Materials', 'runs', runId);
    assertSafeRunPath(root, artifactRoot);
    return deepFreeze({
      schemaVersion: 1,
      runId,
      mode,
      createdAt,
      profileSource: 'draft',
      orchestrationSource: 'draft',
      artifactRoot: relative(root, artifactRoot),
      releaseId: null,
      projectId: null,
    });
  }

  const releaseId = requireId(input?.releaseId, 'releaseId');
  const projectId = requireId(input?.projectId, 'projectId');
  const artifactRoot = path.join(root, 'team', 'artifacts', runId);
  assertSafeRunPath(root, artifactRoot);
  return deepFreeze({
    schemaVersion: 1,
    runId,
    mode,
    createdAt,
    profileSource: `team/ptc/releases/${releaseId}/profiles`,
    orchestrationSource: `team/ptc/releases/${releaseId}/orchestration`,
    artifactRoot: relative(root, artifactRoot),
    releaseId,
    projectId,
  });
}

function same(a, b) { return process.platform === 'win32' ? a.toLowerCase() === b.toLowerCase() : a === b; }

function inside(candidate, directory) {
  const rel = path.relative(directory, candidate);
  return rel === '' || (rel !== '..' && !rel.startsWith(`..${path.sep}`) && !path.isAbsolute(rel));
}

/**
 * Coarse run-level write authority. Role-specific material guards remain more
 * restrictive and are evaluated afterwards; this function can only deny.
 */
export function runWriteDecision(workspaceRoot, context, candidatePath) {
  let root, candidate;
  try {
    root = path.resolve(workspaceRoot);
    validateContext(root, context);
    candidate = assertSafeRunPath(root, candidatePath);
  } catch (error) {
    return { allowed: false, reason: `run boundary: ${error.message}` };
  }

  const releaseRoot = path.join(root, 'team', 'ptc', 'releases');
  const segments = candidate.split(path.sep).map((segment) => process.platform === 'win32' ? segment.toLowerCase() : segment);
  if (inside(candidate, releaseRoot) || segments.includes('versions')) {
    return { allowed: false, reason: 'run boundary: release snapshots are immutable' };
  }

  const artifactRoot = path.resolve(root, context.artifactRoot);
  if (context.mode === 'training') {
    return inside(candidate, artifactRoot)
      ? { allowed: true }
      : { allowed: false, reason: `training boundary: write only ${context.artifactRoot}` };
  }

  const projectRoot = path.join(root, 'project', context.projectId);
  if (inside(candidate, artifactRoot) || inside(candidate, projectRoot)) return { allowed: true };
  return {
    allowed: false,
    reason: `delivery boundary: write only project/${context.projectId} or ${context.artifactRoot}`,
  };
}

export function persistRunContext(workspaceRoot, context) {
  const root = path.resolve(workspaceRoot);
  validateContext(root, context);
  const directory = assertSafeRunPath(root, context.artifactRoot);
  const file = assertSafeRunPath(root, path.join(directory, 'run.json'));
  fs.mkdirSync(directory, { recursive: true });
  if (fs.existsSync(file)) {
    const existing = fs.readFileSync(file, 'utf8');
    const wanted = `${JSON.stringify(context, null, 2)}\n`;
    if (existing !== wanted) throw new Error(`run context already exists with different content: ${file}`);
    return file;
  }
  // Exclusive final creation cannot replace a concurrently published identity.
  // A failed/partial write remains reserved and requires a fresh run ID.
  assertSafeRunPath(root, file);
  fs.writeFileSync(file, `${JSON.stringify(context, null, 2)}\n`, { encoding: 'utf8', flag: 'wx' });
  return file;
}
