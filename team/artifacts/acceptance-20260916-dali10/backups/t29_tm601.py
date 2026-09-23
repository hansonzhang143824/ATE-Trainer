import sys,io,os,json,re
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
J=json.loads(open(os.path.join(d,'setup-contract.json'),'rb').read().decode('utf-8-sig'))
print('=== TM601: does it have a BST route / does it drive BST at all? ===')
t6=J['tmDeltas']['TM601']
prt=t6.get('pinRouteTable') or {}
print('  TM601 pinRouteTable node keys:',[k for k in prt][:20])
b=prt.get('BST')
print('  TM601 pinRouteTable[BST]:',json.dumps(b,ensure_ascii=False)[:500] if b else '(ABSENT)')
print()
print('=== TM601 relaySet ===', json.dumps(t6.get('relaySet'),ensure_ascii=False)[:400])
print()
print('=== TM601 supplyRail / stimuli (does it power BST?) ===')
for k in ('supplyRail','stimuli','ateStimulus','powerSequenceDelta'):
    v=t6.get(k)
    if v is not None: print('  %s: %s'%(k,json.dumps(v,ensure_ascii=False)[:400]))
print()
print('=== aliasResolution entries used by TM601 ===')
for i,e in enumerate(J.get('aliasResolution') or []):
    u=json.dumps(e.get('usedByTm'),ensure_ascii=False)
    if 'TM601' in u:
        print('  [%d] alias=%s usedByTm=%s'%(i,e.get('alias'),u[:120]))
        r=e.get('resolution') or {}
        print('       closedRelayNumbers=%s forceInstrument=%s'%(r.get('closedRelayNumbers'),str(r.get('forceInstrument'))[:90]))
print()
print('=== does the contract mention BST anywhere in TM601 context? ===')
s=json.dumps(t6,ensure_ascii=False)
print('  BST occurrences in tmDeltas.TM601:',s.count('BST'),'| bst2sw:',s.count('bst2sw'))