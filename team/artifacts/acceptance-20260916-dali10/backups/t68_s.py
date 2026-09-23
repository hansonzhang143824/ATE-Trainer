import sys,io,os,re
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
t=open(os.path.join(d,'review-handoff-note-plan-side.md'),'rb').read().decode('utf-8-sig')
print('=== the [48,61,76] mentions in their note, in context ===')
for i,l in enumerate(t.split('\n')):
    if '[48,61,76]' in l or '[48, 61, 76]' in l:
        print('  L%-5d %s'%(i+1,l.strip()[:170]))
print()
print('=== and the correct ch5 closure set, from the contract + netlist ===')
import json
C=json.loads(open(os.path.join(d,'setup-contract.json'),'rb').read().decode('utf-8-sig'))
for e in C.get('aliasResolution') or []:
    if e.get('alias') in ('bst2sw','pmid2sw'):
        print('  %-8s closedRelayNumbers = %s'%(e['alias'],e['resolution'].get('closedRelayNumbers')))
n=open(os.path.join(d,'setup-contract.json'),'rb').read().decode('utf-8-sig')
m=re.search(r'"expectedUnion"\s*:\s*\[([^\]]*)\]',n)
print('  _t30ExpectationNote.expectedUnion =',m.group(1) if m else 'not found')
sch=open(r'D:\Newtest\DSH\ATE-Coding-Plat\project\DALI\SCH-Connect-Map.txt','rb').read().decode('utf-8-sig',errors='replace').split('\n')
print()
print('  netlist ch5 route:')
for i in (672,673,774,775,777,778):
    if i<len(sch) and ('FH5' in sch[i] or 'K48,K76' in sch[i] or 'SW1' in sch[i] or 'SW2' in sch[i]):
        print('    L%d| %s'%(i+1,sch[i].strip()[:120]))