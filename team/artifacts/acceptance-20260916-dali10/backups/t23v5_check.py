import sys,io,os,re
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
u=open(os.path.join(d,'implementation-payload-TM600-TM601.cpp'),'rb').read().decode('utf-8-sig')
L=u.split('\n'); code=[l for l in L if not l.strip().startswith('//')]
print('=== lines containing ": 0.0;" ===')
for i,l in enumerate(code):
    if ': 0.0;' in l: print('  ',l.strip()[:130])
print()
print('=== TM600 block: any mention of TM601 or "derived -1 A" (the misplaced comment)? ===')
s=u.find('DUT_API int TM600_HS_RDSON'); e=u.find('DUT_API int TM601_LS_RDSON')
blk=u[s:e]
for i,l in enumerate(blk.split('\n')):
    if 'TM601' in l or 'derived -1 A' in l or 'derived' in l.lower(): print('  TM600 line %d: %s'%(i+1,l.strip()[:140]))