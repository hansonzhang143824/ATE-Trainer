/**
 * Dev-only repair: the training script was not idempotent, so a re-run appended
 * the "training round 1" rule block a second time to both instructions.md files.
 * The published snapshots (captured before the duplication) are the correct
 * content, so the repair keeps exactly one block and proves the draft returns to
 * byte-identity with what was published.
 *
 * Run: node .dsh-dev/repair-duplicate-rule.mjs
 */
import fs from 'node:fs';
import path from 'node:path';

const ROOT = path.resolve('.');
const HEADING = '## The rule added by training round 1';

for (const profileId of ['ptc-dft-expert', 'ptc-schematic-expert']) {
  const directory = path.join(ROOT, 'team', 'expert-profiles', profileId);
  const file = path.join(directory, 'instructions.md');
  const text = fs.readFileSync(file, 'utf8');
  const first = text.indexOf(HEADING);
  if (first === -1) {
    console.log(`${profileId}: no rule block found, nothing to repair`);
    continue;
  }
  const second = text.indexOf(HEADING, first + HEADING.length);
  if (second === -1) {
    console.log(`${profileId}: exactly one rule block, nothing to repair`);
    continue;
  }
  const repaired = `${text.slice(0, second).trimEnd()}\n`;
  fs.writeFileSync(file, repaired, 'utf8');
  const version = JSON.parse(fs.readFileSync(path.join(directory, 'status.json'), 'utf8')).publishedVersion;
  const published = fs.readFileSync(path.join(directory, 'versions', version, 'instructions.md'), 'utf8');
  console.log([
    `${profileId}: removed the duplicate rule block`,
    `  bytes ${text.length} -> ${repaired.length}`,
    `  draft now identical to published ${version}: ${repaired === published}`,
  ].join('\n'));
}
