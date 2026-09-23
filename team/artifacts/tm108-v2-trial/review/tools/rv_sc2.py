import os,hashlib,json
R=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\tm108-v2-trial\review'
SC=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\tm108-v2-trial\implementation\t7-selfcheck.md'
b=open(SC,'rb').read(); h=hashlib.sha256(b).hexdigest()
pm=os.path.join(R,'t8-review-findings.md'); t=open(pm,'rb').read().decode('utf-8')
key='41935 B, mtime 21:41:13** |'
assert t.count(key)==1, t.count(key)
i=t.index(key); j=t.index('\n', i)
row='\n> | `t7-selfcheck.md` | `a13ef000...`, 18594 B | **`%s...`, %d B, mtime 21:42:27** |' % (h[:12], len(b))
t=t[:j]+row+t[j:]
a3='The manifest was observed at **three** sizes/hashes inside this window'
assert t.count(a3)==1
i2=t.index(a3); j2=t.index('\n', i2)
seg=t[i2:j2]
t=t[:j2]+' The self-check artifact was rewritten as well, from 18594 B to %d B.' % len(b)+t[j2:]
open(pm,'wb').write(t.encode('utf-8'))
print('MD fixed: bytes=%d lines=%d' % (os.path.getsize(pm), t.count(chr(10))+1))
print('  selfcheck row present:', 't7-selfcheck.md' in t)
d=json.loads(open(os.path.join(R,'t8-review-findings.json'),'rb').read().decode('utf-8'))
print('JSON OK: status=%s findings=%d risks=%d gates=%d inputs=%d' % (d['reviewStatus'],len(d['findings']),len(d['residualRisks']),len(d['gateResults']),len(d['reviewedInputs'])))
print('  blocking:', [f['id'] for f in d['findings'] if f.get('blocking')])
print('  t7SelfcheckMd recorded:', 't7SelfcheckMd' in json.dumps(d))
print('  json bytes=%d' % os.path.getsize(os.path.join(R,'t8-review-findings.json')))
