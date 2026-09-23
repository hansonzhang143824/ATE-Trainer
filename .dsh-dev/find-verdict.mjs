/**
 * Dev-only: pull a child's verdict out of its persisted session log.
 *
 * The probe record stores only a 600-character excerpt of the child's output, so
 * the authoritative answer has to come from the session itself. This prints every
 * keyword hit with surrounding context.
 *
 * Run: node .dsh-dev/find-verdict.mjs "<session dir>" REFUSED ALLOWED
 */
import fs from 'node:fs';
import path from 'node:path';
import zlib from 'node:zlib';

const ZSTD_MAGIC = Buffer.from([0x28, 0xb5, 0x2f, 0xfd]);
function decompressAll(file) {
  const buffer = fs.readFileSync(file);
  const starts = [];
  for (let at = buffer.indexOf(ZSTD_MAGIC); at !== -1; at = buffer.indexOf(ZSTD_MAGIC, at + 4)) starts.push(at);
  if (starts.length === 0) return buffer.toString('utf8');
  const parts = [];
  for (let index = 0; index < starts.length; index += 1) {
    const from = starts[index];
    const to = index + 1 < starts.length ? starts[index + 1] : buffer.length;
    parts.push(zlib.zstdDecompressSync(buffer.subarray(from, to)).toString('utf8'));
  }
  return parts.join('');
}

const [dir, ...keywords] = process.argv.slice(2);
if (!dir) {
  console.error('usage: node find-verdict.mjs "<session dir>" [keyword...]');
  process.exit(2);
}
const text = decompressAll(path.join(dir, 'session.jsonl.zstd'));
for (const keyword of keywords.length > 0 ? keywords : ['REFUSED', 'ALLOWED']) {
  console.log(`=== ${keyword} ===`);
  let at = text.indexOf(keyword);
  let hits = 0;
  while (at !== -1 && hits < 4) {
    console.log(`  …${text.slice(Math.max(0, at - 220), at + 260).replace(/\\n/g, ' ').replace(/\s+/g, ' ')}…`);
    hits += 1;
    at = text.indexOf(keyword, at + keyword.length);
  }
  if (hits === 0) console.log('  (no hit)');
}
