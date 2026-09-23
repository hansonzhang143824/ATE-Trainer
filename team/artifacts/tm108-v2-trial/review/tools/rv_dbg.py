import json
P=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\tm108-v2-trial\review\t8-review-findings.json'
t=open(P,'rb').read().decode('utf-8')
lines=t.split('\n')
print('line 322 length:', len(lines[321]))
print('--- context around col 6481 of line 322 ---')
print(repr(lines[321][6400:6560]))
print('--- col 6481 abs char context ---')
c=32636
print(repr(t[c-120:c+120]))
