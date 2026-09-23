import { createImplementationDescriptor } from 'file:///D:/Newtest/DSH/ATE-Coding-Flow/plugins/dsh-ptc-material-boundary/lib/implementation-contract.js';
for (const tm of ['tm106', 'tm108']) {
  const rel = 'team/artifacts/dali-20260921-080849-tm106-tm108-tm425/' + tm + '/method/' + tm + '-test-method-contract.json';
  try { console.log(tm.toUpperCase() + ' DESCRIPTOR: ' + createImplementationDescriptor('D:/Newtest/DSH/ATE-Coding-Flow', rel)); }
  catch (e) { console.log(tm.toUpperCase() + ' ERROR: ' + e.message); }
}
