import { implementationScope, deriveImplementationRecipe, createImplementationDescriptor } from 'file:///D:/Newtest/DSH/ATE-Coding-Flow/plugins/dsh-ptc-material-boundary/lib/implementation-contract.js';
import fs from 'node:fs';
const root = 'D:/Newtest/DSH/ATE-Coding-Flow';
const label = fs.readFileSync(root + '/team/artifacts/dali-20260921-080849-tm106-tm108-tm425/last-impl-label.txt', 'utf8').trim();
console.log('label len', label.length);
const agent = { id: 'probe', session: { events: [{ type: 'subagent/descriptor', data: { label } }] } };
const scope = implementationScope(agent, root);
console.log('SCOPE:', scope && scope.error ? 'REJECTED: ' + scope.error : 'ACCEPTED (trial=' + scope.trial + ')');
const token = /recipe=([A-Za-z0-9_-]+)$/.exec(label)[1];
const rel = /contract=([^#]+)#/.exec(label)[1];
const abs = fs.realpathSync.native(root + '/' + rel);
const contract = JSON.parse(fs.readFileSync(abs, 'utf8'));
const { recipe: fresh } = deriveImplementationRecipe(contract, abs, root);
function stable(v){ if (Array.isArray(v)) return v.map(stable); if (v && typeof v === 'object') return Object.fromEntries(Object.keys(v).sort().map(k=>[k, stable(v[k])])); return v; }
const sent = JSON.parse(Buffer.from(token, 'base64url').toString('utf8'));
const a = JSON.stringify(stable(sent)), b = JSON.stringify(stable(fresh));
console.log('sent len', a.length, '| fresh len', b.length, '| equal', a === b);
if (a !== b) { let i = 0; while (i < Math.min(a.length, b.length) && a[i] === b[i]) i++;
  console.log('first diff at index', i);
  console.log('sent :', JSON.stringify(a.slice(Math.max(0, i - 70), i + 90)));
  console.log('fresh:', JSON.stringify(b.slice(Math.max(0, i - 70), i + 90))); }
const regenerated = createImplementationDescriptor(root, rel);
console.log('regenerated descriptor identical to registry label:', regenerated === label);
if (regenerated !== label) { console.log('regen len', regenerated.length); let i = 0; while (i < Math.min(regenerated.length, label.length) && regenerated[i] === label[i]) i++; console.log('first diff at', i); console.log('regen:', JSON.stringify(regenerated.slice(Math.max(0,i-60), i+90))); console.log('label:', JSON.stringify(label.slice(Math.max(0,i-60), i+90))); }
