P=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\tm108-v2-trial\review\t8-review-findings.md'
t=open(P,'rb').read().decode('utf-8')
cands = [
 '### C12 — the `K17` closed-state requirement',
 'method/bst-sw-phase-check.md',
 '**No executable line of `test.cpp` needs to change to close `RF-01`.**',
 '### C11 — the `logPlan` raw-context question',
 '**Routing note** — this is explicitly **not** returned to `ate-implementer`',
 '| `RR-11` | low |',
 '| `G-11` |',
 'does not hand off downstream',
 '**CONFIRMED for test.cpp',
 'CONCLUSION: the implementer',
 '**Conclusion:** no existing primitive was missed',
]
for c in cands:
    print('%3d  %s' % (t.count(c), c))
print()
# show the exact C11 block end and RR-11 row and G-11 row
import re
for pat in [r'### C11 —.*?(?=\n### C12)', r'\| `RR-11` \|.*', r'\| `G-11` \|.*', r'\| `method/bst-sw-phase-check\.md` \|.*']:
    m=re.search(pat,t,re.S)
    print('---',pat[:30],'---')
    print(repr(m.group(0)[:400]) if m else 'NOT FOUND')
