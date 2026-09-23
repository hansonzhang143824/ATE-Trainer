import sys,io,os,json,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
J=json.loads(open(os.path.join(d,'test-plan.json'),'rb').read().decode('utf-8-sig'))
print('revision:',str(J.get('revision'))[:200])
print()
for it in J.get('items',[]):
    if it.get('tm') in ('TM600','TM601'):
        v={x.get('name'):x.get('value') for x in it.get('parameters',[])}
        m=it.get('measurement',{})
        print('%s: settle=%s samples=%s force=%s ramp=%s'%(it.get('tm'),v.get('settle'),v.get('measureSamples'),v.get('forceCurrent'),v.get('forceRamp')))
        print('   pulseCap=%s'%json.dumps(m.get('pulseCap'),ensure_ascii=False)[:150])
        # ordered steps mentioning ms
        for s in (m.get('activationSemantics') or {}).get('orderedSteps',[]):
            if 'ms' in str(s) or '2 ms' in str(s): print('   step: %s'%str(s)[:150])