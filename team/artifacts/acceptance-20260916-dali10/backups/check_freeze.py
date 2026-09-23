import sys,io,os,hashlib,json
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
for n in ['test-plan.json','test-plan.v1.json','setup-contract.json']:
    p=os.path.join(d,n)
    if not os.path.exists(p): print('%-28s ABSENT'%n); continue
    raw=open(p,'rb').read()
    print('%-24s %7d B %s'%(n,len(raw),hashlib.sha256(raw).hexdigest()))
p=os.path.join(d,'test-plan.json')
J=json.loads(open(p,'rb').read().decode('utf-8-sig'))
print('test-plan revision:',str(J.get('revision'))[:90])
print()
print("captain's freeze claim: v3 = 121694 B / 2e93a46c54c79b9028940840f6cf162d15304f89df3c3e88dd5fdea5f5061eda")