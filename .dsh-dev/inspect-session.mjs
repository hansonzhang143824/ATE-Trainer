/**
 * Dev-only session inspector.
 *
 * Two traps this handles, both of which silently produce a WRONG answer:
 *   1. DSH persists sessions as zstd-compressed JSONL and appends one FRAME per
 *      flush. `zstdDecompressSync` and the decompress stream stop after the
 *      first frame, so the naive read returns a bare session header and zero
 *      events — which looks like "no evidence" instead of "did not read it".
 *      Frames are split on the zstd magic and decompressed individually.
 *   2. The interesting identity fields are nested in per-event `data`, so the
 *      census must run over every JSONL record, not over a top-level array.
 *
 * Run: node .dsh-dev/inspect-session.mjs "<session dir>" [needle...]
 */
import fs from 'node:fs';
import path from 'node:path';
import zlib from 'node:zlib';

const ZSTD_MAGIC = Buffer.from([0x28, 0xb5, 0x2f, 0xfd]);

function decompressAll(file) {
  const buffer = fs.readFileSync(file);
  const starts = [];
  for (let at = buffer.indexOf(ZSTD_MAGIC); at !== -1; at = buffer.indexOf(ZSTD_MAGIC, at + 4)) starts.push(at);
  if (starts.length === 0) return { text: buffer.toString('utf8'), frames: 0 };
  const parts = [];
  for (let index = 0; index < starts.length; index += 1) {
    const from = starts[index];
    const to = index + 1 < starts.length ? starts[index + 1] : buffer.length;
    parts.push(zlib.zstdDecompressSync(buffer.subarray(from, to)).toString('utf8'));
  }
  return { text: parts.join(''), frames: starts.length };
}

const [dir, ...needles] = process.argv.slice(2);
if (!dir) {
  console.error('usage: node inspect-session.mjs "<session dir>" [needle...]');
  process.exit(2);
}
const file = path.join(dir, 'session.jsonl.zstd');
const { text, frames } = decompressAll(file);
const records = text.split(/\r?\n/).filter(Boolean).map((line) => {
  try {
    return JSON.parse(line);
  } catch {
    return { type: '(unparsable)', raw: line.slice(0, 160) };
  }
});

console.log(`dir: ${path.basename(dir)}   zstd frames: ${frames}   records: ${records.length}`);
const header = records.find((record) => record.type === 'session');
if (header) console.log(`session header: id=${header.id} cwd=${header.cwd} delegationDepth=${header.delegationDepth}`);

const counts = new Map();
for (const record of records) {
  const type = record.type ?? '(no type)';
  counts.set(type, (counts.get(type) ?? 0) + 1);
}
console.log('--- record census ---');
for (const [type, count] of [...counts].sort((a, b) => b[1] - a[1])) console.log(`  ${String(count).padStart(4)}  ${type}`);

const identityRecords = records.filter((record) => /subagent|descriptor/i.test(record.type ?? ''));
console.log(`--- subagent/descriptor records: ${identityRecords.length} ---`);
for (const record of identityRecords.slice(0, 8)) console.log(JSON.stringify(record).slice(0, 700));

for (const needle of needles) {
  console.log(`--- needle ${JSON.stringify(needle)} ---`);
  const hits = records.filter((record) => JSON.stringify(record).includes(needle));
  console.log(`records containing it: ${hits.length}`);
  for (const hit of hits.slice(0, 4)) console.log(`  ${JSON.stringify(hit).slice(0, 1500)}`);
}
