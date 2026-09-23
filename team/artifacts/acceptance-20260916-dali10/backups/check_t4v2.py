import sys,io,os,hashlib,time,json
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
for n in ['test-plan.json','test-plan.v1.json','test-plan-tm600-tm601-measurement-excerpt.md','schematic-ir-sensing.json']:
    p=os.path.join(d,n)
    if not os.path.exists(p): print('%-52s ABSENT'%n); continue
    raw=open(p,'rb').read()
    print('%-52s %7d B %s mtime=%s'%(n,len(raw),hashlib.sha256(raw).hexdigest(),time.strftime('%H:%M:%S',time.localtime(os.path.getmtime(p)))))
print()
p=os.path.join(d,'test-plan.json')
J=json.loads(open(p,'rb').read().decode('utf-8-sig'))
print('test-plan revision now:',J.get('revision'))