
import fs from 'node:fs';
import path from 'node:path';
import zlib from 'node:zlib';
const DIR = 'C:/Users/nvt10241/.dsh/sessions/--D-Newtest-DSH-ATE-Coding-Flow--';
const SID = process.argv[2];
function decompress(p) {
  const buf = fs.readFileSync(p); const parts = []; let idx = 0;
  while (idx < buf.length - 4) {
    if (buf.readUInt32LE(idx) !== 0xFD2FB528) { idx += 1; continue; }
    let end = buf.length;
    for (let j = idx + 4; j < buf.length - 3; j++) { if (buf.readUInt32LE(j) === 0xFD2FB528) { end = j; break; } }
    try { parts.push(zlib.zstdDecompressSync(buf.subarray(idx, end))); } catch {}
    idx = end;
  }
  return Buffer.concat(parts).toString('utf8');
}
const ev = decompress(path.join(DIR, SID, 'session.jsonl.zstd')).split('\n').filter(l=>l.trim())
  .map(l => { try { return JSON.parse(l); } catch { return null; } }).filter(Boolean);
const t = (ms) => { const d = new Date(ms + 8*3600*1000); return d.toISOString().slice(11,23); };
const s = (ms) => ms < 1000 ? ms + 'ms' : (ms/1000).toFixed(1) + 's';
const t0 = ev[0].createdAt;
let last = null;
console.log('session start ' + t(t0));
for (const o of ev) {
  const time = o.time ?? o.time0 ?? o.createdAt;
  if (o.type === 'turn/start') console.log(t(time) + ' | TURN ' + o.data.turn + ' START  (+' + s(time - t0) + ')');
  else if (o.type === 'turn/end') console.log(t(time) + ' | TURN ' + o.data.turn + ' END reason=' + JSON.stringify(o.data.reason) + '  (+' + s(time - t0) + ')');
  else if (o.type === 'step/start') { last = { start: time, turn: o.data.turn, step: o.data.step }; console.log('  ' + t(time) + ' | step ' + o.data.step + ' start'); }
  else if (o.type === 'step/end') console.log('  ' + t(time) + ' | step end ' + s(time - (last?.start ?? time)));
  else if (o.type === 'tool/call') {
    let a = {}; try { a = JSON.parse(o.data.arguments || '{}'); } catch {}
    console.log('    ' + t(time) + ' | CALL ' + o.data.name + ' :: ' + String(a.description || a.file_path || '').slice(0, 70));
  }
  else if (o.type === 'tool/code-dispatch') {
    const a = o.data.arguments || {};
    const label = a.description || a.file_path || a.pattern || (Array.isArray(a.queries) ? a.queries[0] : '') || (a.command ? String(a.command).slice(0,50) : '');
    console.log('      ' + t(time) + '   inner:' + o.data.name + ' err=' + (o.data.isError===true) + ' :: ' + String(label).slice(0, 70));
  }
  else if (o.type === 'tool/result') {
    const cid = o.data.message?.source?.callId;
    console.log('    ' + t(time) + ' | RESULT ' + cid);
  }
}
console.log('--- now ' + t(Date.now()) + ' ---');
