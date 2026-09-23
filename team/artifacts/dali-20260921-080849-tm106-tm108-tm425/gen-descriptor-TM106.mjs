import { createImplementationDescriptor } from 'file:///D:/Newtest/DSH/ATE-Coding-Flow/plugins/dsh-ptc-material-boundary/lib/implementation-contract.js';
import fs from 'node:fs';
const root = 'D:/Newtest/DSH/ATE-Coding-Flow';
const rel = 'team/artifacts/dali-20260921-080849-tm106-tm108-tm425/tm106/method/tm106-test-method-contract.json';
fs.writeFileSync(root + '/team/artifacts/dali-20260921-080849-tm106-tm108-tm425/descriptor-TM106.txt', createImplementationDescriptor(root, rel) + '\n', 'utf8');
console.log('written, length=' + createImplementationDescriptor(root, rel).length);
