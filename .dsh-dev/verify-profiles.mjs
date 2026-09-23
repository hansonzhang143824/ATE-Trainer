/**
 * Dev-only: verify every published expert profile resolves through the real
 * dispatcher, and that no published snapshot has drifted from its manifest.
 *
 * Run: node .dsh-dev/verify-profiles.mjs [workspaceRoot]
 */
import fs from 'node:fs';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

const root = path.resolve(process.argv[2] ?? '.');
const modulePath = path.join(root, 'plugins', 'dsh-ptc-material-boundary', 'lib', 'dispatch-profile.js');
const { resolvePublishedProfile } = await import(pathToFileURL(modulePath).href);
const { runtimeLabelFor, executionClassForProfile } = await import(
  pathToFileURL(path.join(root, 'plugins', 'dsh-ptc-material-boundary', 'lib', 'expert-policy-registry.js')).href
);

const profilesRoot = path.join(root, 'team', 'expert-profiles');
let failures = 0;
for (const profileId of fs.readdirSync(profilesRoot).sort()) {
  const status = JSON.parse(fs.readFileSync(path.join(profilesRoot, profileId, 'status.json'), 'utf8'));
  const resolved = resolvePublishedProfile(root, profileId);
  const published = status.publishedVersion;
  const versions = fs.readdirSync(path.join(profilesRoot, profileId, 'versions')).sort();
  if (!resolved.ok) {
    failures += 1;
    console.log(`${profileId}: REFUSED — ${resolved.reason}`);
    continue;
  }
  const expectedLabel = runtimeLabelFor(resolved.executionClass);
  const labelOk = resolved.runtimeLabel === expectedLabel;
  if (!labelOk) failures += 1;
  console.log([
    `${profileId}: published ${published} (history ${(status.history ?? []).map((h) => h.version).join(', ')})`,
    `resolved version ${resolved.version}, class ${resolved.executionClass} (registry maps ${executionClassForProfile(profileId)})`,
    `label ${JSON.stringify(resolved.runtimeLabel)} ${labelOk ? '== registry' : '!= registry'}`,
    `manifest digest ${resolved.manifest.digest.slice(0, 16)}…, snapshot files verified: ${Object.keys(resolved.manifest.files).length}`,
    `older versions present: ${versions.filter((v) => v !== resolved.version).join(', ') || '(none)'}`,
  ].join('\n  '));
}
console.log(failures === 0 ? 'ALL PROFILES OK' : `${failures} PROBLEM(S)`);
process.exit(failures === 0 ? 0 : 1);
