import sys,io,json,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
p=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10\test-plan.json'
raw=open(p,'rb').read()
d=json.loads(raw.decode('utf-8-sig'))
print('test-plan revision:',d.get('revision'))
for it in d.get('items',[]):
    if it.get('tm') in ('TM600','TM601'):
        v={x.get('name'):x.get('value') for x in it.get('parameters',[])}
        mp=it.get('measurement',{})
        print('\n%s: forceLoop=%s'%(it.get('tm'),v.get('forceLoop')))
        print('  forceCurrent=%s ramp=%s settle=%s samples=%s'%(v.get('forceCurrent'),v.get('forceRamp'),v.get('settle'),v.get('measureSamples')))
        print('  clamp=%s'%str(v.get('clamp'))[:80])
        print('  samples=',json.dumps(mp.get('samples'),ensure_ascii=False)[:120])