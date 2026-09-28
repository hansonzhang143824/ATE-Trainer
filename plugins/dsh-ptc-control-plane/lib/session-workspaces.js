import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { assertSafeRunPath } from './run-context.js';
import { loadTrainingRelease } from './training-release.js';
import { loadWorkflowTemplateRelease } from './workflow-template-release.js';

export const PTC_PROFILE_IDS = Object.freeze([
  'ptc-dft-expert', 'ptc-schematic-expert', 'strategy-expert', 'method-expert',
  'rule-reviewer', 'ate-implementer', 'compile-diagnostician', 'evolution-expert',
]);

const PROFILE_SET = new Set(PTC_PROFILE_IDS);
const ID = /^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$/;

function createWorkspaceDirectory(root, relativePath) {
  const target = assertSafeRunPath(root, path.join(root, relativePath));
  fs.mkdirSync(target, { recursive: true });
  const checked = assertSafeRunPath(root, target);
  const stat = fs.lstatSync(checked);
  if (!stat.isDirectory() || stat.isSymbolicLink()) throw new Error('session workspace is not a safe directory');
  return checked;
}

function ensureWorkflowInstructions(root, directory, profileIds) {
  const file = assertSafeRunPath(root, path.join(directory, 'AGENTS.md'));
  if (fs.existsSync(file)) {
    const stat = fs.lstatSync(file);
    if (!stat.isFile() || stat.isSymbolicLink()) throw new Error('workflow instructions are not a safe file');
    return;
  }
  const instructions = [
    '# PTC workflow training session',
    '',
    'This DSH conversation is SMOKE_ONLY. Ordered Agent IDs: ' + profileIds.join(' -> ') + '.',
    'A chat answer is not an orchestration run or a Captain-verified receipt.',
    'The PTC control panel owns execution. An arbitrary ordered smoke template must be explicitly saved and frozen before execution; the legacy PTC buttons separately support the DFT + schematic pilot and complete eight-Agent chain.',
    'For a simple 1+2 JSON question, immediately answer {"answer":3} with a JSON number; do not dispatch Agents or call tools.',
    'Discuss workflow improvements here, but do not claim they are active until candidate rules are saved, verified, frozen and published through the control panel.',
    'Do not read private TM109 business materials, run business gates, or modify published versions from this session.',
    '',
  ].join('\n');
  try { fs.writeFileSync(file, instructions, { flag: 'wx' }); }
  catch (error) { if (error?.code !== 'EEXIST') throw error; }
}

/** Derive DSH workspaces from a closed set of PTC mode identities. */
export function resolvePtcSessionWorkspace(workspaceRoot, input) {
  const root = path.resolve(workspaceRoot);
  if (!input || typeof input !== 'object' || Array.isArray(input) || typeof input.mode !== 'string') {
    throw new Error('session workspace request must include a mode');
  }

  if (input.mode === 'agent') {
    if (Object.keys(input).sort().join('|') !== 'mode|profileId' || !PROFILE_SET.has(input.profileId)) {
      throw new Error('agent session workspace requires one PTC profile id');
    }
    const directory = assertSafeRunPath(root, path.join(root, 'team', 'expert-profiles', input.profileId));
    if (!fs.statSync(directory).isDirectory()) throw new Error('agent profile workspace is missing');
    return { mode: 'agent', profileId: input.profileId, path: directory };
  }

  if (input.mode === 'workflow') {
    if (Object.keys(input).sort().join('|') !== 'mode|profileIds' || !Array.isArray(input.profileIds)
        || input.profileIds.length < 1 || input.profileIds.length > PTC_PROFILE_IDS.length
        || input.profileIds.some(id => !PROFILE_SET.has(id))
        || new Set(input.profileIds).size !== input.profileIds.length) {
      throw new Error('workflow session workspace requires unique PTC profile ids');
    }
    const profileIds = [...input.profileIds];
    const key = crypto.createHash('sha256').update(`workflow-v2\n${profileIds.join('\n')}`, 'utf8').digest('hex');
    const directory = createWorkspaceDirectory(root, path.join('Training_Materials', 'session-workspaces', `workflow-${key}`));
    ensureWorkflowInstructions(root, directory, profileIds);
    return { mode: 'workflow', profileIds, key, path: directory };
  }

  if (input.mode === 'publish') {
    if (Object.keys(input).sort().join('|') !== 'mode') throw new Error('publish session workspace accepts no overrides');
    const directory = createWorkspaceDirectory(root, path.join('Training_Materials', 'session-workspaces', 'publish-review'));
    return { mode: 'publish', path: directory };
  }

  if (input.mode === 'engineering') {
    if (Object.keys(input).sort().join('|') !== 'mode|releaseId'
        || typeof input.releaseId !== 'string' || !ID.test(input.releaseId)
        || /[. ]$/.test(input.releaseId) || /^(?:con|prn|aux|nul|com[1-9]|lpt[1-9])(?:\.|$)/i.test(input.releaseId)) {
      throw new Error('engineering session workspace requires a safe release id');
    }
    const bundleDigest = input.releaseId.startsWith('workflow-release-')
      ? loadWorkflowTemplateRelease(root, input.releaseId).manifestSha256
      : loadTrainingRelease({ workspaceRoot: root, releaseId: input.releaseId }).manifest.bundleDigest;
    const directory = createWorkspaceDirectory(root,
      path.join('publish', 'session-workspaces', 'engineering', input.releaseId));
    return { mode: 'engineering', releaseId: input.releaseId, bundleDigest, path: directory };
  }

  throw new Error('unsupported PTC session mode');
}
