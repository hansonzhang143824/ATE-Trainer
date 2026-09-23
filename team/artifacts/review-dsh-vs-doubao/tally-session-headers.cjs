// Adversarial verification helper: tally session-log creation headers.
// Reads zstd session logs read-only; writes nothing except stdout.
const fs = require('node:fs');
const path = require('node:path');
const z = require('node:zlib');

const manifestFile = path.join(__dirname, 'session-manifest.txt');
const manifest = fs.readFileSync(manifestFile, 'utf8')
  .split(/\r?\n/)
  .filter(Boolean)
  .map(line => {
    const i = line.indexOf('|');
    return { slug: line.slice(0, i), file: line.slice(i + 1) };
  });

function headerOf(file) {
  const buf = z.zstdDecompressSync(fs.readFileSync(file));
  const s = buf.toString('utf8');
  const i = s.indexOf('\n');
  return JSON.parse(s.slice(0, i < 0 ? s.length : i));
}

function tallyFor(slug) {
  const rows = [];
  for (const entry of manifest.filter(m => m.slug === slug)) {
    try {
      const h = headerOf(entry.file);
      rows.push({
        dir: path.basename(path.dirname(entry.file)),
        origin: h.origin || '(none)',
        depth: h.delegationDepth === undefined ? '-' : String(h.delegationDepth),
        preset: h.agentPreset || '(none)',
        parent: h.parentSession ? 'child' : 'root',
      });
    } catch (e) {
      rows.push({ dir: path.basename(path.dirname(entry.file)), origin: 'ERROR', depth: '-', preset: e.message.slice(0, 60), parent: '-' });
    }
  }
  return rows;
}

const slugs = [...new Set(manifest.map(m => m.slug))];

let grand = 0;
const perSlug = {};
const originTally = {};
const presetTally = {};
const depthTally = {};
const parentTally = {};
for (const slug of slugs) {
  const rows = tallyFor(slug);
  perSlug[slug] = rows.length;
  grand += rows.length;
  for (const r of rows) {
    originTally[r.origin] = (originTally[r.origin] || 0) + 1;
    presetTally[r.preset] = (presetTally[r.preset] || 0) + 1;
    depthTally[r.depth] = (depthTally[r.depth] || 0) + 1;
    parentTally[r.parent] = (parentTally[r.parent] || 0) + 1;
  }
}
console.log('GRAND_TOTAL_SESSIONS', grand);
console.log('PER_SLUG', JSON.stringify(perSlug));
console.log('ORIGIN', JSON.stringify(originTally));
console.log('PRESET', JSON.stringify(presetTally));
console.log('DEPTH', JSON.stringify(depthTally));
console.log('PARENT', JSON.stringify(parentTally));

const target = '--D-Newtest-DSH-ATE-Coding-Plat--';
const rows = tallyFor(target);
console.log('ATE_SLUG_ROWS', rows.length);
console.log('ATE_SLUG_ORIGIN', JSON.stringify(rows.reduce((a, r) => (a[r.origin] = (a[r.origin] || 0) + 1, a), {})));
console.log('ATE_SLUG_PRESET', JSON.stringify(rows.reduce((a, r) => (a[r.preset] = (a[r.preset] || 0) + 1, a), {})));
console.log('ATE_SLUG_DEPTH', JSON.stringify(rows.reduce((a, r) => (a[r.depth] = (a[r.depth] || 0) + 1, a), {})));
console.log('ATE_SLUG_PARENT', JSON.stringify(rows.reduce((a, r) => (a[r.parent] = (a[r.parent] || 0) + 1, a), {})));

// The parent session of THIS reviewer session, for preset comparison.
const mine = 'a1098db7-0d47-4d8e-b0bc-9e38e0c5eb54';
const mineFile = manifest.find(m => m.file.includes(mine)).file;
const myHeader = headerOf(mineFile);
console.log('MY_HEADER', JSON.stringify(myHeader));
if (myHeader.parentSession) {
  const p = myHeader.parentSession.replace(/^session-/, '');
  const entry = manifest.find(m => m.file.includes(p));
  console.log('PARENT_FOUND', Boolean(entry));
  if (entry) console.log('PARENT_HEADER', JSON.stringify(headerOf(entry.file)));
}
// Effective default preset check: distinct presets seen in the ATE slug.
console.log('DISTINCT_PRESETS', JSON.stringify(Object.keys(presetTally)));

// Newest sessions: which preset does the CURRENT configuration actually produce?
const all = manifest.map(m => {
  const h = headerOf(m.file);
  return { slug: m.slug, id: h.id, preset: h.agentPreset || '(none)', origin: h.origin || 'root', createdAt: h.createdAt, depth: h.delegationDepth === undefined ? '-' : h.delegationDepth };
});
console.log('NEWEST_12', JSON.stringify(all.sort((a, b) => b.createdAt - a.createdAt).slice(0, 12).map(r => `${new Date(r.createdAt).toISOString().slice(0, 10)} ${r.preset} ${r.origin} d${r.depth}`)));
const byDay = {};
for (const r of all) {
  const day = new Date(r.createdAt).toISOString().slice(0, 10);
  byDay[day] = byDay[day] || {};
  byDay[day][r.preset] = (byDay[day][r.preset] || 0) + 1;
}
for (const day of Object.keys(byDay).sort()) console.log('DAY', day, JSON.stringify(byDay[day]));


