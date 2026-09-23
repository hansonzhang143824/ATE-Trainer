import fs from 'node:fs';
import crypto from 'node:crypto';
import { implementationScope } from 'file:///D:/Newtest/DSH/ATE-Coding-Flow/plugins/dsh-ptc-material-boundary/lib/implementation-contract.js';
const root = 'D:/Newtest/DSH/ATE-Coding-Flow';
const dir = root + '/team/artifacts/dali-20260921-080849-tm106-tm108-tm425';
const want = fs.readFileSync(dir + '/descriptor-TM106.txt', 'utf8').trim();
const cand = fs.readFileSync(dir + '/candidate-TM106.txt', 'utf8').trim();
if (cand !== want) { console.log('CANDIDATE MISMATCH: len ' + cand.length + ' vs ' + want.length);
  for (let i = 0; i < 10; i++) { const c = cand.slice(i * 500, (i + 1) * 500); const w = want.slice(i * 500, (i + 1) * 500);
    const ok = c === w; console.log('chunk' + String(i).padStart(2, '0') + ': ' + (ok ? 'OK' : 'BAD'));
    if (!ok) { const j = [...c].findIndex((ch, k) => ch !== w[k]); console.log('  first diff at chunk offset ' + j); console.log('  cand: ' + JSON.stringify(c.slice(Math.max(0, j - 30), j + 40))); console.log('  want: ' + JSON.stringify(w.slice(Math.max(0, j - 30), j + 40))); } }
  process.exit(2); }
console.log('bytes identical: ' + cand.length);
const agent = { id: 'precheck', session: { events: [{ type: 'subagent/descriptor', data: { label: cand } }] } };
const scope = implementationScope(agent, root);
if (scope && scope.error) { console.log('SCOPE REJECTED: ' + scope.error); process.exit(3); }
console.log('SCOPE ACCEPTED for trial ' + scope.trial + ' family=' + scope.recipe.family + ' relays=' + scope.recipe.functionalRelays.join(','));
