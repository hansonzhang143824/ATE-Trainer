import sys,io,os,hashlib,time,json
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
for n in ['test-plan.json','test-plan.v1.json','setup-contract.json','test-plan-tm600-tm601-measurement-excerpt.md','schematic-ir-sensing.json','dft-ir.json']:
    p=os.path.join(d,n)
    if not os.path.exists(p): print('%-52s ABSENT'%n); continue
    raw=open(p,'rb').read()
    print('%-46s %7d B %s  mtime=%s'%(n,len(raw),hashlib.sha256(raw).hexdigest()[:24],time.strftime('%H:%M:%S',time.localtime(os.path.getmtime(p)))))
p=os.path.join(d,'test-plan.json')
J=json.loads(open(p,'rb').read().decode('utf-8-sig'))
print()
print('test-plan revision string:',str(J.get('revision'))[:120])
print()
print("captain claims: test-plan v2 = 113773 B / 7f1bdf97...a86463 ; setup-contract = 229695 B / ab07d6f9...")
# re-verify the two TM items' key values in the current file
for it in J.get('items',[]):
    if it.get('tm') in ('TM600','TM601'):
        v={x.get('name'):x.get('value') for x in it.get('parameters',[])}
        print('  %s ramp=%s settle=%s samples=%s force=%s'%(it.get('tm'),v.get('forceRamp'),v.get('settle'),v.get('measureSamples'),v.get('forceCurrent')))