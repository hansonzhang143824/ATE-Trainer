import sys,io,os,glob,json
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
print('=== run-dir files containing "lateRulingsNotInIR" ===')
hits=0
for p in glob.glob(os.path.join(d,'**','*'),recursive=True):
    if not os.path.isfile(p): continue
    if os.path.getsize(p)>4_000_000: continue
    try: s=open(p,'rb').read().decode('utf-8-sig',errors='replace')
    except: continue
    if 'lateRulingsNotInIR' in s:
        print('  ',os.path.relpath(p,d)); hits+=1
print('  total',hits)
print()
print('=== dft-raw listing ===')
for p in sorted(glob.glob(os.path.join(d,'dft-raw','**','*'),recursive=True)):
    if os.path.isfile(p): print('  %-46s %8d B'%(os.path.relpath(p,d),os.path.getsize(p)))