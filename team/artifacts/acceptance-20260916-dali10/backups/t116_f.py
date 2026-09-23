import sys,io,os,json
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
J=json.loads(open(os.path.join(d,'implementation-manifest.json'),'rb').read().decode('utf-8-sig'))
h=J['handoffCitationRisk']
print('=== MY OWN PAYLOAD ENTRY: what qualifiers sit beside the value? ===')
for e in h['authoritativeCurrentValues']:
    if e['artefact'].startswith('implementation-payload'):
        for k,v in e.items():
            print('  %-30s %s'%(k,str(v)[:150]))
print()
print('=== the payload identity block (in landingGate.gates) — does it carry an instant? ===')
print('  ',h['landingGate']['gates'][-260:])
print()
print('=== and how my manifest cites OTHER members (L1 or L2?) ===')
w=h.get('withdrawnFromAuthoritativeList')
print('  withdrawnFromAuthoritativeList:',json.dumps(w,ensure_ascii=False)[:330])