import sys,io,os,json,hashlib,re
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
pay=open(os.path.join(d,'implementation-payload-TM600-TM601.cpp'),'rb').read()
u=pay.decode('utf-8-sig'); c=re.sub(r'//.*$','',u,flags=re.M)
print('payload %d B / %s'%(len(pay),hashlib.sha256(pay).hexdigest()))
print('  delay_ms(1)=%d  delay_ms(2)=%d  -> settle question: %s'%(c.count('delay_ms(1)'),c.count('delay_ms(2)'),'ALREADY 1 ms' if c.count('delay_ms(1)')==6 and c.count('delay_ms(2)')==0 else 'NEEDS WORK'))
print()
for n,claim in [('test-plan.json','166099/1925250d'),('test-plan-tm600-tm601-measurement-excerpt.md','8423/9554d4d6'),('setup-contract.json','329115/295d483a')]:
    p=os.path.join(d,n); r=open(p,'rb').read()
    print('  %-52s live %7d B / %s  (t4 claim %s)'%(n,len(r),hashlib.sha256(r).hexdigest()[:16],claim))
print()
m=json.loads(open(os.path.join(d,'implementation-manifest.json'),'rb').read().decode('utf-8-sig'))
fi=m.get('frozenInputs',{})
for k,v in fi.items():
    if isinstance(v,dict) and 'sha256' in v:
        print('  manifest frozenInputs[%s]: %s %s'%(k,v.get('size'),v.get('sha256')[:16]))