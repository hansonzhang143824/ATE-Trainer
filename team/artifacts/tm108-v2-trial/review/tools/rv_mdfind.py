import re,os
pm=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\tm108-v2-trial\review\t8-review-findings.md'
t=open(pm,'rb').read().decode('utf-8')
for m in re.finditer(r'.*manifest \|.*', t):
    print(repr(m.group(0)))
print('---')
i=t.find('### ⚠ REVISION DRIFT')
print('drift block present:', i>=0)
if i>=0: print(repr(t[i:i+700]))
