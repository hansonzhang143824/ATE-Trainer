import sys,io,os,re,json,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
h=open(r'D:\PROJECT6-DALI\ForCodexDebug\source\StdAfx.h','rb').read().decode('utf-8-sig',errors='replace')
print('=== StdAfx.h defines for 109 / 110 ===')
for i,l in enumerate(h.split('\n')):
    if re.search(r'#define\s+\w*(109|110)\b',l) or re.search(r'#define\s+\w+\s+(109|110)\s*$',l):
        print('  %4d| %s'%(i+1,l.strip()[:130]))
print()
print('=== usage of K109/K110 in existing target test.cpp (precedent) ===')
t=open(r'D:\PROJECT6-DALI\ForCodexDebug\source\test.cpp','rb').read().decode('utf-8-sig')
for i,l in enumerate(t.split('\n')):
    if 'K109' in l or 'K110' in l: print('  %4d| %s'%(i+1,l.strip()[:130]))
print()
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
J=json.loads(open(os.path.join(d,'setup-contract.json'),'rb').read().decode('utf-8-sig'))
print("=== aliasResolution[3] (the [110,61] entry) ===")
print(json.dumps(J['aliasResolution'][3],ensure_ascii=False)[:900])