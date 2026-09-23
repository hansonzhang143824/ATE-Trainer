import fs from 'node:fs';
import crypto from 'node:crypto';
const root = 'D:/Newtest/DSH/ATE-Coding-Flow';
const dir = root + '/team/artifacts/dali-20260921-080849-tm106-tm108-tm425';
const d = fs.readFileSync(dir + '/descriptor-TM106.txt', 'utf8').trim();
const N = 10, size = Math.ceil(d.length / N);
for (let i = 0; i < N; i++) {
  const chunk = d.slice(i * size, (i + 1) * size);
  fs.writeFileSync(dir + '/descriptor-TM106.chunk' + String(i).padStart(2, '0') + '.txt', chunk, 'utf8');
  console.log('chunk' + String(i).padStart(2, '0') + ' len=' + chunk.length + ' sha8=' + crypto.createHash('sha256').update(chunk).digest('hex').slice(0, 8));
}
console.log('total=' + d.length);
