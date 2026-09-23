import { readFileSync, writeFileSync } from 'node:fs';
import { receiptDigest, verifyDispatchReceipt } from 'file:///D:/Newtest/DSH/ATE-Coding-Flow/plugins/dsh-ptc-material-boundary/lib/dispatch-receipt.js';
const path = "D:/Newtest/DSH/ATE-Coding-Flow/team/artifacts/dispatch-receipts/ptc-dft-expert-dali-20260921-080849-tm106-tm108-tm425-TM106-TM108-TM425-refresh-1.json";
const receipt = JSON.parse(readFileSync(path, 'utf8'));
receipt.childSessionId = 'a3ba4578-b366-43cb-a2fb-1831ac2c0869';
delete receipt.digest;
const digest = receiptDigest(receipt);
const check = verifyDispatchReceipt({ ...receipt, digest });
if (!check.ok) { console.error('INVALID: ' + check.errors.join('; ')); process.exit(2); }
receipt.digest = digest;
writeFileSync(path, JSON.stringify(receipt, null, 2) + '\n', 'utf8');
const reread = JSON.parse(readFileSync(path, 'utf8'));
const recheck = verifyDispatchReceipt(reread);
console.log(recheck.ok ? 'ON-DISK-VERIFY-OK digest=' + reread.digest + ' childSessionId=' + reread.childSessionId : 'ON-DISK-VERIFY-FAILED: ' + recheck.errors.join('; '));
if (!recheck.ok) process.exit(2);
