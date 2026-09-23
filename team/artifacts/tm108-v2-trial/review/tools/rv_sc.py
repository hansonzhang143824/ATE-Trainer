import json,hashlib,os
R=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\tm108-v2-trial\review'
SC=r'D:\PROJECT6-DALI\ForCodexDebug\..\..\Newtest\DSH\ATE-Coding-Plat\team\artifacts\tm108-v2-trial\implementation\t7-selfcheck.md'
SC=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\tm108-v2-trial\implementation\t7-selfcheck.md'
b=open(SC,'rb').read(); h=hashlib.sha256(b).hexdigest()
print('t7-selfcheck.md now: %d B  %s' % (len(b), h))
pj=os.path.join(R,'t8-review-findings.json'); s=open(pj,'rb').read().decode('utf-8')
a='"selfChecksCount": 13, "openItemsCount": 15 }'
assert s.count(a)==1, s.count(a)
new='"%s"' % 'SELF'
s=s.replace(a, '"selfChecksCount": 13, "openItemsCount": 15, "t7SelfcheckMd": { "sha256_plaintext": "%s", "bytes": %d, "mtimeLocal": "2026-09-17 21:42:27", "stateAsReviewed": "a13ef000e6305b20e2316262aeece15403afff16ba58a3b08ce2c49f98dac2db (18594 B)" } }' % (h, len(b)), 1)
json.loads(s)
open(pj,'wb').write(s.encode('utf-8'))
print('JSON patched, bytes=%d' % os.path.getsize(pj))
pm=os.path.join(R,'t8-review-findings.md'); t=open(pm,'rb').read().decode('utf-8')
a2='| manifest | `a4f5286d…556`, 25688 B | **`58c54c48…78e`, 41935 B, mtime `21:41:13`** |'
assert t.count(a2)==1
t=t.replace(a2, a2+'\n> | `t7-selfcheck.md` | `a13ef000…2db`, 18594 B | **`%s…`, %d B, mtime `21:42:27`** |' % (h[:12], len(b)),1)
a3='The manifest was observed at **three** sizes/hashes inside this window (`a4f5286d…` → `26171fca…` → `58c54c48…`).'
assert t.count(a3)==1
t=t.replace(a3, a3+' The self-check artifact was rewritten too, from 18594 B to %d B.' % len(b),1)
open(pm,'wb').write(t.encode('utf-8'))
print('MD patched, bytes=%d' % os.path.getsize(pm))
d=json.loads(open(pj,'rb').read().decode('utf-8'))
print('FINAL: status=%s findings=%d risks=%d gates=%d inputs=%d' % (d['reviewStatus'],len(d['findings']),len(d['residualRisks']),len(d['gateResults']),len(d['reviewedInputs'])))
print('  blocking:', [f['id'] for f in d['findings'] if f.get('blocking')])
