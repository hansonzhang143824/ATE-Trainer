import fs from 'node:fs';
import path from 'node:path';

/**
 * Training-mode write allowlist, sourced from the same address book the
 * trainer sessions consume: Training_Materials/_expert_bindings.json.
 *
 * Fail-closed by design: any load or validation problem voids the entry and
 * the caller keeps the legacy profileRoot-only boundary. A bindings entry may
 * never grant paths outside the session workspace, nor inside
 * team/expert-profiles, plugins/ or scripts/ (privilege escalation).
 */
const PREFIX_BY_PROFILE = {
  'ptc-dft-expert': 'dft-',
  'ptc-schematic-expert': 'schematic-',
};
const FORBIDDEN_DIRS = [
  path.join('team', 'expert-profiles'),
  'plugins',
  'scripts',
];

const cache = new Map(); // session workspace -> { mtimeMs, value }

export function loadTrainingBindings(cwd, profileId) {
  const root = path.resolve(cwd);
  const file = path.join(root, 'Training_Materials', '_expert_bindings.json');
  let mtimeMs = 0;
  let raw;
  try {
    mtimeMs = fs.statSync(file).mtimeMs;
    raw = fs.readFileSync(file, 'utf8');
  } catch (e) {
    return remember(root, mtimeMs, null, `bindings unreadable (${e.code || e.message})`);
  }
  const hit = cache.get(root);
  if (hit && hit.mtimeMs === mtimeMs) return hit.value;
  let doc;
  try { doc = JSON.parse(raw.replace(/^\uFEFF/, '')); } catch { return remember(root, mtimeMs, null, 'bindings JSON parse failed'); }
  if (doc.schemaVersion !== 2) return remember(root, mtimeMs, null, `bindings schemaVersion ${doc.schemaVersion} !== 2`);
  const expert = Array.isArray(doc.experts) ? doc.experts.find((e) => e && e.profileId === profileId) : null;
  if (!expert) return remember(root, mtimeMs, null, `no bindings entry for ${profileId}`);
  const writes = resolveInside(root, expert.writes);
  const verification = resolveInside(root, expert.verification);
  if (!writes || !verification) return remember(root, mtimeMs, null, `bindings entry for ${profileId} grants a forbidden path`);
  return remember(root, mtimeMs, { writes, verification, prefix: PREFIX_BY_PROFILE[profileId] || null }, null);
}

function resolveInside(root, rel) {
  if (typeof rel !== 'string' || !rel.trim()) return null;
  const abs = path.resolve(root, rel);
  const up = path.relative(root, abs);
  if (up.startsWith('..') || path.isAbsolute(up)) return null; // escapes the session workspace
  for (const dir of FORBIDDEN_DIRS) {
    const forbidden = path.resolve(root, dir);
    if (abs === forbidden || abs.startsWith(forbidden + path.sep)) return null;
  }
  return abs;
}

function remember(root, mtimeMs, entry, reason) {
  const value = { entry, reason };
  cache.set(root, { mtimeMs, value });
  return value;
}
