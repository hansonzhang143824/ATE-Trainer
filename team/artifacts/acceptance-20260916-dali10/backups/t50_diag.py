import sys,io,os,hashlib,json,re
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
sbx=os.path.join(d,'gate-check-t21','source','test.cpp')
t=open(sbx,'rb').read().decode('utf-8-sig')
seg=t[t.find('DUT_API int TM600_HS_RDSON'):t.find('DUT_API int TM601_LS_RDSON')]
print('=== which SetOn does the SANDBOX carry for TM600? ===')
for l in seg.split('\n'):
    if 'cbite.SetOn(' in l: print('  ',l.strip()[:175])
print('  K110 in TM600 segment:', 'K110_ACM18_BST' in seg, '| K48 in segment:', 'K48_ACM5_AMP_REF' in seg)
print()
print('=== the OTHER SetOn sites that mention K110 (why the segment test was misleading) ===')
for i,l in enumerate(t.split('\n')):
    if 'cbite.SetOn(' in l and ('K110' in l or 'K154' in l):
        print('  L%d: %s'%(i+1,l.strip()[:150]))
print()
print('=== rev 25 expectation for TM600 (from the gate message and the contract) ===')
J=json.loads(open(os.path.join(d,'setup-contract.json'),'rb').read().decode('utf-8-sig'))
print('  contract on disk revision:',J.get('revision'))
for i,e in enumerate(J.get('aliasResolution') or []):
    if e.get('alias')=='bst2sw':
        print('  aliasResolution[%d] closedRelayNumbers=%s usedByTm=%s'%(i,e['resolution'].get('closedRelayNumbers'),json.dumps(e.get('usedByTm'),ensure_ascii=False)))