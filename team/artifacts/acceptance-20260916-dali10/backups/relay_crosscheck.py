import sys,io,os,re,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
# Cross-check: the _A macros and union relays used by the payload
src=r'D:\PROJECT6-DALI\ForCodexDebug\source\StdAfx.h'
h=open(src,'rb').read().decode('utf-8-sig',errors='replace')
want=['K_FPVIH_TO_PMID_A','K_FPVIL_TO_SW_A','K_FPVIH_TO_PGND_A','K_FPVIH_TO_BST_A']
print('=== macro definitions used by the payload (live StdAfx.h) ===')
for w in want:
    for l in h.split('\n'):
        m=re.match(r'\s*#define\s+'+w+r'\s+([\d,]+)',l)
        if m: print('  %-24s = %s'%(w,m.group(1)))
print()
print('=== forbidden numbers inside those macros? ===')
for w in want:
    for l in h.split('\n'):
        m=re.match(r'\s*#define\s+'+w+r'\s+([\d,]+)',l)
        if m:
            nums=m.group(1).split(',')
            bad=[n for n in nums if n in ('87','88','89','90','91','131','132','133','134','135')]
            print('  %-24s forbidden=%s'%(w,bad if bad else 'none'))
print()
print('=== what the payload SetOn lists actually close ===')
p=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10\implementation-payload-TM600-TM601.cpp'
t=open(p,'rb').read().decode('utf-8-sig')
for m in re.finditer(r'cbite\.SetOn\(([^)]*)\)',t):
    print('  ',m.group(1).strip())
print()
print('=== plan t4 relayUnion (current revision) ===')
import json
J=json.loads(open(r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10\test-plan.json','rb').read().decode('utf-8-sig'))
for it in J.get('items',[]):
    if it.get('tm') in ('TM600','TM601'):
        r=it.get('relayUnion') or {}
        print('  %s union=%s high=%s low=%s'%(it.get('tm'),r.get('union'),r.get('highTerminal'),r.get('lowTerminal')))