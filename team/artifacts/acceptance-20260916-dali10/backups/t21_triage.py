import sys,io,os,re,glob,json,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
base=r'D:\Newtest\DSH\ATE-Coding-Plat'
# 1) does TM643 exist in the BASELINE (pre-change) test.cpp?
bak=os.path.join(base,'team','artifacts','acceptance-20260916-dali10','backups','test.cpp.before_TM600_TM601.bak')
b=open(bak,'rb').read().decode('utf-8-sig',errors='replace')
print('=== TM643 in BASELINE backup ===')
print('  TM643 occurrences:',b.count('TM643'))
i=b.find('TM643')
if i>0:
    j=b.find('DUT_API int',i)
    print('  function header:',b[max(0,i-200):i+80].split('\n')[-3:])
print()
# does baseline close K57/K5 inside TM643?
s=b.find('DUT_API int TM643_VBAT_LOOP_INDICTOR')
if s<0: print('  (exact DUT_API name not found; searching near TM643)')
if s>0:
    e=b.find('DUT_API int',s+10); blk=b[s:e if e>0 else len(b)]
    print('  TM643 SetOn:',[l.strip()[:110] for l in blk.split('\n') if 'SetOn(' in l])
print()
# 2) cbit baseline comparison file
p=os.path.join(base,'project','DALI','phase2_singlepoint_output.txt')
print('=== cbit baseline file ===')
print('  exists:',os.path.exists(p), os.path.getsize(p) if os.path.exists(p) else '')
if os.path.exists(p):
    c=open(p,'rb').read().decode('utf-8-sig',errors='replace')
    for k in ['K168','K169','K170','126','159','160','161']:
        print('  %-6s in baseline: %d'%(k,c.count(k)))
print()
# 3) locate SCH-Connect-Map
for pat in [os.path.join(base,'project','DALI','SCH-Connect-Map.txt'), os.path.join(base,'**','SCH-Connect-Map.txt')]:
    f=glob.glob(pat,recursive=True)
    if f: print('SCH-Connect-Map:',f[0]); break