import sys,io,json
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
p=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10\test-plan.json'
J=json.loads(open(p,'rb').read().decode('utf-8-sig'))
it=[x for x in J['items'] if x.get('tm')=='TM600'][0]
m=it.get('measurement',{})
print('=== TM600 measurement.gainFirstUse ==='); print(json.dumps(m.get('gainFirstUse'),ensure_ascii=False,indent=1)[:1200])
print('=== TM600 senseActivation ==='); print(json.dumps(m.get('activationSemantics',{}).get('senseActivation'),ensure_ascii=False,indent=1)[:900])
print('=== TM600 orderedSteps ===')
for s in m.get('activationSemantics',{}).get('orderedSteps',[]): print('   -',str(s)[:170])
# DV-01 activationSurface / fourInstrumentRejection
for b in (J.get('blockingDecisions') or []):
    if isinstance(b,dict) and b.get('id')=='DV-01':
        print('=== DV-01 keys:',list(b.keys()))
        print('activationSurface:',json.dumps(b.get('activationSurface'),ensure_ascii=False)[:600])