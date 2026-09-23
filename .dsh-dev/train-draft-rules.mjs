/**
 * Dev-only: apply the first RULE-LEVEL training change to both expert drafts.
 *
 * The change turns each golden case from a declaration into something
 * re-runnable: the case declares the gate command it must survive, and the draft
 * evaluation executes it. This came out of the first-batch loop, where the DFT
 * artifacts were only provably correct once the review was re-bound to them and
 * the gate was re-run — a case nobody can re-run proves very little.
 *
 * Run from the repo root: node .dsh-dev/train-draft-rules.mjs
 */
import fs from 'node:fs';
import path from 'node:path';

const ROOT = path.resolve('.');
const changes = [];

function patchJson(relative, mutate) {
  const file = path.join(ROOT, relative);
  const value = JSON.parse(fs.readFileSync(file, 'utf8'));
  const before = JSON.stringify(value);
  mutate(value);
  if (JSON.stringify(value) === before) {
    changes.push(`${relative}: already up to date`);
    return;
  }
  fs.writeFileSync(file, `${JSON.stringify(value, null, 2)}\n`, 'utf8');
  changes.push(`${relative}: updated`);
}

function appendOnce(relative, marker, block) {
  const file = path.join(ROOT, relative);
  const text = fs.readFileSync(file, 'utf8');
  // The marker MUST appear verbatim inside `block`, otherwise this is not
  // idempotent and every re-run appends the rule again (which happened: the
  // first marker was a phrase that the block never contained).
  if (!block.includes(marker)) {
    throw new Error(`appendOnce marker ${JSON.stringify(marker)} does not appear in the block for ${relative} — refusing to write a non-idempotent rule`);
  }
  if (text.includes(marker)) {
    changes.push(`${relative}: already up to date`);
    return;
  }
  fs.writeFileSync(file, `${text.trimEnd()}\n\n${block.trimEnd()}\n`, 'utf8');
  changes.push(`${relative}: updated`);
}

patchJson('team/expert-profiles/ptc-dft-expert/cases/TM106/expected.json', (value) => {
  value.verification = {
    command: 'python scripts/validate_dft_outputs.py --tm TM106',
    expectExit: 0,
    expectContains: '"status": "ready"',
    rule: 'A golden case must survive its own gate: the evaluation re-runs this command and requires the declared exit code and status. A case that cannot be re-run is a claim, not evidence.',
  };
});

patchJson('team/expert-profiles/ptc-schematic-expert/cases/TM106/expected.json', (value) => {
  value.verification = {
    command: 'python scripts/validate_schematic_outputs.py',
    expectExit: 0,
    expectContains: '"status": "ready"',
    rule: 'A golden case must survive its own gate: the evaluation re-runs this command and requires the declared exit code and status.',
  };
});

appendOnce(
  'team/expert-profiles/ptc-dft-expert/instructions.md',
  '## The rule added by training round 1',
  `## The rule added by training round 1

A golden case is only worth something if someone else can re-run it. Every case
in \`cases/\` declares the gate command it must survive (\`verification\`), and the
draft evaluation executes that command and requires its declared exit code and
status text. So: after you change any DFT artifact, the bound semantic review must
be re-bound and the gate re-run — an artifact set whose review still points at the
previous hashes is stale even when every value looks right.`,
);

appendOnce(
  'team/expert-profiles/ptc-schematic-expert/instructions.md',
  '## The rule added by training round 1',
  `## The rule added by training round 1

A golden case is only worth something if someone else can re-run it. Every case
in \`cases/\` declares the gate command it must survive (\`verification\`), and the
draft evaluation executes that command and requires its declared exit code and
status text. So: whenever the TXT/JSON pair or the receipt changes, every sha256
inside \`schematic-receipt.json\` must be re-bound before the gate is believed.`,
);

appendOnce(
  'team/expert-profiles/ptc-dft-expert/CHANGELOG.md',
  '## training round 1',
  `## training round 1 (draft)

- Rule change: the TM106 case now declares an executable \`verification\` block
  (\`python scripts/validate_dft_outputs.py --tm TM106\`, exit 0, \`"status": "ready"\`)
  and the draft evaluation runs it. The instructions state the re-binding rule that
  the first-batch loop exposed: a review still pointing at pre-refresh hashes makes
  the whole artifact set stale.`,
);

appendOnce(
  'team/expert-profiles/ptc-schematic-expert/CHANGELOG.md',
  '## training round 1',
  `## training round 1 (draft)

- Rule change: the TM106 case now declares an executable \`verification\` block
  (\`python scripts/validate_schematic_outputs.py\`, exit 0, \`"status": "ready"\`)
  and the draft evaluation runs it. The instructions state that every sha256 in the
  receipt must be re-bound whenever a TXT/JSON pair changes.`,
);

console.log(changes.join('\n'));
