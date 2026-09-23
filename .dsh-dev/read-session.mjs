/**
 * Dev-only session reader. DSH persists each session as a zstd-compressed JSONL
 * (`session.jsonl.zstd`); this prints its event census and the identity-bearing
 * events so a claim about "the child the parent dispatched is the child the
 * guard sees" can be checked against the record instead of asserted.
 *
 * Run: node .dsh-dev/read-session.mjs "<session dir>"
 */
import fs from 'node:fs';
import path from 'node:path';
import zlib from 'node:zlib';

const dir = process.argv[2];
if (!dir) {
  console.error('usage: node read-session.mjs "<session dir>"');
  process.exit(2);
}
const file = path.join(dir, 'session.jsonl.zstd');
if (!fs.existsSync(file)) {
  console.error(`no session.jsonl.zstd in ${dir}`);
  process.exit(2);
}
const raw = zlib.zstdDecompressSync(fs.readFileSync(file)).toString('utf8');
const events = raw.split(/\r?\n/).filter(Boolean).map((line) => {
  try {
    return JSON.parse(line);
  } catch {
    return { type: '(unparsable)', raw: line.slice(0, 120) };
  }
});

console.log(`dir: ${path.basename(dir)}   events: ${events.length}`);
const counts = new Map();
for (const event of events) {
  const type = event.type ?? '(no type)';
  counts.set(type, (counts.get(type) ?? 0) + 1);
}
for (const [type, count] of [...counts].sort((a, b) => b[1] - a[1])) {
  console.log(`  ${String(count).padStart(4)}  ${type}`);
}

const interesting = events.filter((event) => /subagent|header/i.test(event.type ?? ''));
console.log(`--- identity-bearing events: ${interesting.length} ---`);
for (const event of interesting.slice(0, 10)) {
  console.log(JSON.stringify(event).slice(0, 700));
}
