import sys,io,os,json,re
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
J=json.loads(open(os.path.join(d,'test-plan.json'),'rb').read().decode('utf-8-sig'))
s=json.dumps(J,ensure_ascii=False)
print('revision:',str(J.get('revision'))[:400])
print()
print('=== did v21 close my three reported gaps? ===')
checks={
 'PLAN-GAP-1 teardown disambiguation':'float' in s and ('last' in s.lower()),
 'PLAN-GAP-2 initialization range (10UA)': '10UA' in s,
 'PLAN-GAP-2 minimal compliant wording': 'minimal compliant' in s.lower(),
 'PLAN-GAP-3 (200,5) golden-specific': '(200, 5)' in s or '200, 5' in s,
}
for k,v in checks.items(): print('  %-46s %s'%(k,v))
print()
for tok in ['10UA','FPVIe_10UA','minimal compliant','initialization range','golden-specific','(50, 5)','measured current path']:
    print('  %-24s %d'%(tok,s.count(tok)))
print()
print('=== the disambiguated teardown wording (live) ===')
for it in J['items'][:2]:
    c=it.get('cleanup') or []
    if c: print('  %s cleanup[0]: %s'%(it.get('tm'),str(c[0])[:260]))