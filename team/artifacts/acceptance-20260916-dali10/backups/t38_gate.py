import sys,io,os,json,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
M=json.loads(open(os.path.join(d,'implementation-manifest.json'),'rb').read().decode('utf-8-sig'))
s=json.dumps(M,ensure_ascii=False)
print('=== does the MANIFEST state the current gate? ===')
for tok in ['t40 + t42','t40+t42','t39','t42','countingMethod','handoffCitationRisk']:
    print('  %-20s occurrences: %d'%(tok,s.count(tok)))
blk=M.get('handoffCitationRisk',{})
print()
print('  handoffCitationRisk keys:',list(blk.keys()))
print('  does it mention any gate/task?:',any('t4' in str(v) for v in blk.values()))
print()
print('=== does the FROZEN evidence doc state it? (read-only; captain re-froze it) ===')
t=open(os.path.join(d,'t40-tm601-bst-evidence.md'),'rb').read().decode('utf-8-sig')
print('  "t40 + t42":',t.count('t40 + t42'))
print('  "pending t39+t40":',t.count('pending t39+t40'))
print('  "t40 and t42":',t.count('t40 and t42'))