import sys,io,os,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'APPLY-TM600-TM601.md'); t=open(p,'rb').read().decode('utf-8-sig')
# refresh the payload hash rows to the t29 revision
import re
t2=re.sub(r'\| `implementation-payload-TM600-TM601\.cpp` \| \*\*[^|]+\| \*\*`[0-9a-f]+`\*\* \|',
 '| `implementation-payload-TM600-TM601.cpp` | **38147 B** | **`272667f3f79393b6b1365237c7ac01bed7a527d2984d53d1d5ae6804515057c0`** |', t)
if t2==t:
    # fall back: locate the table row dynamically
    for line in t.split('\n'):
        if 'implementation-payload-TM600-TM601.cpp' in line and '|' in line: print('row found:',line[:120])
t2=t2.replace('`73b511b7…`','`272667f3…`').replace('73b511b775beda61cc91ea41fdc5358e53579fb4e32cc553bf47792667fea19e','272667f3f79393b6b1365237c7ac01bed7a527d2984d53d1d5ae6804515057c0')
open(p,'wb').write(t2.encode('utf-8'))
r=open(p,'rb').read()
print('APPLY doc %d B / %s'%(len(r),hashlib.sha256(r).hexdigest()))
print('contains current payload hash:','272667f3' in r.decode('utf-8'))
print('compare-before-write block kept:','THE TREE HAS ALREADY BEEN WRITTEN' in r.decode('utf-8'))