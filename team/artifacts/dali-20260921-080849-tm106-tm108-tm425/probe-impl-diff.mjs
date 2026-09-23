import { createImplementationDescriptor } from 'file:///D:/Newtest/DSH/ATE-Coding-Flow/plugins/dsh-ptc-material-boundary/lib/implementation-contract.js';
import fs from 'node:fs';
const root = 'D:/Newtest/DSH/ATE-Coding-Flow';
const rel = 'team/artifacts/dali-20260921-080849-tm106-tm108-tm425/tm106/method/tm106-test-method-contract.json';
const regen = createImplementationDescriptor(root, rel);
const registryLabel = fs.readFileSync(root + '/team/artifacts/dali-20260921-080849-tm106-tm108-tm425/last-impl-label.txt', 'utf8').trim();
const note = JSON.parse(fs.readFileSync(root + '/team/artifacts/dali-20260921-080849-tm106-tm108-tm425/implementation-dispatch-TM106.json', 'utf8'));
const sent = note.descriptor;
console.log('lens: regen=' + regen.length + ' registry=' + registryLabel.length + ' sentNote=' + sent.length);
function firstDiff(a, b) { let i = 0; const n = Math.min(a.length, b.length); while (i < n && a[i] === b[i]) i++; return i; }
function show(tag, a, b) { const i = firstDiff(a, b); console.log(tag + ' first diff at ' + i + ' (lens ' + a.length + ' vs ' + b.length + ')');
  console.log('  A: ' + JSON.stringify(a.slice(Math.max(0, i - 50), i + 70)));
  console.log('  B: ' + JSON.stringify(b.slice(Math.max(0, i - 50), i + 70))); }
console.log('regen === sentNote:', regen === sentNote(regen, sent));
function sentNote(x, y){ return y; }
if (regen !== sent) show('regen vs sentNote', regen, sent);
if (sent !== registryLabel) show('sentNote vs registry', sent, registryLabel);
if (regen !== registryLabel) show('regen vs registry', regen, registryLabel);
try { const token = /recipe=([A-Za-z0-9_-]+)$/.exec(sent)[1];
  const decoded = Buffer.from(token, 'base64url').toString('utf8');
  JSON.parse(decoded); console.log('sentNote token decodes: OK');
} catch (e) { console.log('sentNote token decode/parse FAILS: ' + e.message.slice(0, 120)); }
try { const token = /recipe=([A-Za-z0-9_-]+)$/.exec(regen)[1];
  JSON.parse(Buffer.from(token, 'base64url').toString('utf8')); console.log('regen token decodes: OK');
} catch (e) { console.log('regen token decode FAILS: ' + e.message.slice(0, 120)); }
