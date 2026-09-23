import fs from 'node:fs';
import { implementationScope } from 'file:///D:/Newtest/DSH/ATE-Coding-Flow/plugins/dsh-ptc-material-boundary/lib/implementation-contract.js';
const root = 'D:/Newtest/DSH/ATE-Coding-Flow';
const dir = root + '/team/artifacts/dali-20260921-080849-tm106-tm108-tm425';
const want = fs.readFileSync(dir + '/descriptor-TM108.txt', 'utf8').trim();
const cand = fs.readFileSync(dir + '/candidate-TM108.txt', 'utf8').trim();
if (cand !== want) { console.log('CANDIDATE MISMATCH: len ' + cand.length + ' vs ' + want.length);
  let i = 0; const n = Math.min(cand.length, want.length); while (i < n && cand[i] === want[i]) i++;
  console.log('first diff at ' + i); console.log('cand: ' + JSON.stringify(cand.slice(Math.max(0,i-40), i+60))); console.log('want: ' + JSON.stringify(want.slice(Math.max(0,i-40), i+60)));
  process.exit(2); }
console.log('bytes identical: ' + cand.length);
const agent = { id: 'precheck', session: { events: [{ type: 'subagent/descriptor', data: { label: cand } }] } };
const scope = implementationScope(agent, root);
if (scope && scope.error) { console.log('SCOPE REJECTED: ' + scope.error); process.exit(3); }
console.log('SCOPE ACCEPTED trial=' + scope.trial + ' family=' + scope.recipe.family + ' relays=' + scope.recipe.functionalRelays.join(','));
