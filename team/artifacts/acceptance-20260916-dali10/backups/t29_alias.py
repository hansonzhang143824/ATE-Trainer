import sys,io,os,json
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
J=json.loads(open(os.path.join(d,'setup-contract.json'),'rb').read().decode('utf-8-sig'))
e=J['aliasResolution'][3]
print('=== bst2sw resolution (full) ===')
print(json.dumps(e.get('resolution'),ensure_ascii=False,indent=1)[:1500])
print()
print('=== does bst2sw mention 109 anywhere? ===', '109' in json.dumps(e))
print()
print('=== TM600 pinRouteTable BST block (full) ===')
print(json.dumps(J['tmDeltas']['TM600']['pinRouteTable'].get('BST'),ensure_ascii=False,indent=1)[:1200])
print()
print('=== resourceBudget for TM600 (which channel drives BST) ===')
rb=J['tmDeltas']['TM600'].get('resourceBudget')
print(json.dumps(rb,ensure_ascii=False)[:600] if rb else '(absent)')
s=json.dumps(J['tmDeltas']['TM600'],ensure_ascii=False)
i=s.find('bst2sw')
print()
print('=== bst2sw mentions inside tmDeltas.TM600 ===')
import re
for m in re.finditer(r'bst2sw',s):
    print('  ...',s[max(0,m.start()-160):m.start()+260].replace('\\n',' ')[:420])
    break