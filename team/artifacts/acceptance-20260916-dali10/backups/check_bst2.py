import sys,io,re,os,json,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
p=r'D:\PROJECT6-DALI\ForCodexDebug\source\StdAfx.h'
t=open(p,'rb').read().decode('utf-8-sig',errors='replace')
print('=== composite macros containing 131/132/134/135 (the ch1 set the ruling names) ===')
for i,l in enumerate(t.split('\n')):
    if re.search(r'#define\s+\w+\s+[\d,\s]*(13[1-5])',l) and l.strip().startswith('#define'):
        m=re.match(r'\s*#define\s+(\w+)\s+([\d,]+)',l)
        if m and any(x in m.group(2).split(',') for x in ('131','134','135')):
            print('   %-34s = %s'%(m.group(1),m.group(2)))
print()
print('=== is there any SIMPLE ch1 endpoint macro to BST or SW? (names containing BST/SW with FPVI1) ===')
for i,l in enumerate(t.split('\n')):
    if re.match(r'\s*#define\s+K_FPVI1',l): print('   ',l.strip()[:120])
print()
print('=== contract: does its alias table assign BST-SW to FPVIe1 CH1? ===')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
sc=json.loads(open(d+r'\setup-contract.json','rb').read().decode('utf-8-sig'))
v=sc['tmDeltas']['TM600']
print('  resourceBudget:',v.get('resourceBudget'))
print('  aliasesUsed:',v.get('aliasesUsed'))
ks=[k for k in v.keys() if 'alias' in k.lower() or 'route' in k.lower()]
print('  keys with alias/route:',ks)
at=sc.get('aliasResolution') or {}
s=json.dumps(at,ensure_ascii=False)
for tok in ('bst2sw','BST_SW','bst_sw'):
    i=s.find(tok)
    print('  %-8s found at %d -> %s'%(tok,i,s[max(0,i-160):i+200] if i>0 else '(absent)'))