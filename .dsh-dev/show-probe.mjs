/**
 * Dev-only: print the child's own words from the dispatch probe record, so a
 * finding quotes the agent's report verbatim instead of my paraphrase.
 *
 * Run: node .dsh-dev/show-probe.mjs [path-to-probe-json]
 */
import fs from 'node:fs';

const file = process.argv[2] ?? '.dsh-dev/oneshot-probe.json';
const record = JSON.parse(fs.readFileSync(file, 'utf8'));
console.log(`mode=${record.mode} dispatched=${record.dispatched} stopReason=${record.settled?.stopReason}`);
console.log(`child=${record.receipt?.childSessionId} version=${record.receipt?.profileVersion} label=${record.receipt?.label}`);
/** The record stores blocks as JSON that may be encoded more than once. */
function unwrap(value) {
  let current = value;
  for (let depth = 0; depth < 3; depth += 1) {
    if (Array.isArray(current)) return current;
    if (typeof current !== 'string') return undefined;
    try {
      current = JSON.parse(current);
    } catch {
      return undefined;
    }
  }
  return Array.isArray(current) ? current : undefined;
}

const blocks = unwrap(record.settled?.output);
if (blocks === undefined) {
  console.log(`[raw] ${String(record.settled?.output).slice(0, 2000)}`);
  process.exit(0);
}
for (const block of blocks) {
  if (block?.type === 'text') console.log(`[text] ${block.text}`);
  else if (block?.type === 'reasoning') console.log(`[reasoning] ${block.text}`);
  else if (block?.type === 'tool-call') console.log(`[tool-call ${block.name}] ${String(block.arguments).slice(0, 600)}`);
}

