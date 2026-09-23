import sys,io,os,re
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
t=open(os.path.join(d,'t38-acm-pin5-exposure.md'),'rb').read().decode('utf-8-sig')
print('=== does t38-acm-pin5-exposure.md carry any stale "48/76 = 0" claim? ===')
for pat in [r'K48.{0,12}=\s*0', r'K76.{0,12}=\s*0', r'neither', r'closed by my payload', r'\b0\b.*48', r'48/76']:
    hits=[m.group(0)[:80] for m in re.finditer(pat,t)]
    print('  %-24s %d %s'%(pat,len(hits),hits[:3]))
print()
print('=== the lines that mention K48 in that doc (context check) ===')
for i,l in enumerate(t.split('\n')):
    if 'K48' in l and ('0' in l or 'closes' in l or 'absent' in l):
        print('  L%-4d %s'%(i+1,l.strip()[:140]))