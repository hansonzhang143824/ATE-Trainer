// Read-only: link session headers by parentSession to test whether AgentTeams
// members correspond to real independent DSH sessions (own logs = own agents).
const fs = require('node:fs');
const path = require('node:path');
const z = require('node:zlib');

const manifestFile = path.join(__dirname, 'session-manifest.txt');
const manifest = fs.readFileSync(manifestFile, 'utf8').split(/\r?\n/).filter(Boolean).map(line => {
  const i = line.indexOf('|');
  return { slug: line.slice(0, i), file: line.slice(i + 1) };
});

const headers = manifest.map(m => {
  const buf = z.zstdDecompressSync(fs.readFileSync(m.file));
  const s = buf.toString('utf8');
  const i = s.indexOf('\n');
  try {
    return { slug: m.slug, file: m.file, header: JSON.parse(s.slice(0, i < 0 ? s.length : i)) };
  } catch (e) {
    return { slug: m.slug, file: m.file, header: { id: path.basename(path.dirname(m.file)), parseError: e.message } };
  }
});

console.log('TOTAL_LOGS', headers.length);
const withParent = headers.filter(h => h.header.parentSession);
console.log('WITH_PARENT', withParent.length);

// Fan-out: children per parent session.
const kids = {};
for (const h of withParent) {
  const p = h.header.parentSession;
  kids[p] = kids[p] || [];
  kids[p].push(h);
}
const parents = Object.entries(kids).sort((a, b) => b[1].length - a[1].length);
console.log('DISTINCT_PARENTS', parents.length);
console.log('TOP_PARENTS', JSON.stringify(parents.slice(0, 6).map(([p, c]) => `${p}: ${c.length} children`)));

// AgentTeams captains recorded in on-disk team state.
const captains = [
  'session-10f58ee1-2083-4191-ab60-df64101fbb1e', // retired-context/.../ate-dali-acceptance
];
for (const c of captains) {
  const children = kids[c] || [];
  console.log(`CAPTAIN ${c} CHILDREN ${children.length}`);
  for (const ch of children) {
    console.log('   child', ch.header.id, 'preset=' + (ch.header.agentPreset || '-'), 'depth=' + ch.header.delegationDepth, 'created=' + new Date(ch.header.createdAt).toISOString());
  }
}
const liveTeams = ['D:\\Newtest\\DSH\\ATE-Coding-Plat\\.agent-teams\\ate-v2-idle\\team.json'];
for (const f of liveTeams) {
  if (!fs.existsSync(f)) { console.log('MISSING', f); continue; }
  const t = JSON.parse(fs.readFileSync(f, 'utf8'));
  console.log('LIVE_TEAM', t.name, 'captainSessionId=' + t.captainSessionId, 'members=' + t.members.length, 'tasks=' + t.tasks.length);
  console.log('   member keys', t.members[0] ? Object.keys(t.members[0]).join(',') : '(none)');
  const children = kids[t.captainSessionId] || [];
  console.log('   CHILDREN_OF_LIVE_CAPTAIN', children.length);
  for (const ch of children) console.log('   child', ch.header.id, 'preset=' + (ch.header.agentPreset || '-'), 'created=' + new Date(ch.header.createdAt).toISOString());
}

// Any header field that names a member/team?
const fieldNames = new Set();
for (const h of headers) for (const k of Object.keys(h.header)) fieldNames.add(k);
console.log('HEADER_FIELDS', JSON.stringify([...fieldNames]));
