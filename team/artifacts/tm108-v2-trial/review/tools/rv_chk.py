import re
P=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\tm108-v2-trial\review\t8-review-findings.json'
t=open(P,'rb').read().decode('utf-8')
for m in re.finditer(r'CONFIRMED[^"]{0,80}', t):
    print('HIT:', repr(m.group(0)))
print('---- anchors check ----')
anchors = [
 'CONCLUSION: the implementer',
 "No executable line of test.cpp needs to change to close RF-01.",
 '(and no other is named by R-LOG at rules-registry.md:37). See RF-01.',
 'The hash-bound facts are unaffected." }\n  ],',
 'and \'the quantities are in the comments\' is NOT accepted by this review as satisfying a logPlan record."',
 'I also found the same rule fails on the failure path',
 '  "reviewStatus": "needs-revision",',
 'role-charter-precedence',
]
for a in anchors:
    print('%3d  %s' % (t.count(a), repr(a[:70])))
