import sys,io,os,re
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
sub=os.path.join(d,'backups','superseded-scratch')
fs=sorted(os.listdir(sub))
print('moved: %d files'%len(fs))
print()
print('=== attribution probe: whose names do these carry? ===')
mine=[]; other=[]; unk=[]
for f in fs:
    if f=='README.md': continue
    lf=f.lower()
    if re.match(r'^t(29|36|38|50|5[0-9]|6[0-9])_',lf): mine.append(f)
    elif re.match(r'^t(42|43|44|46|48|52|53)-',lf) or 't48' in lf or 't42' in lf: other.append(f)
    else: unk.append(f)
print('  my t-numbered helpers: %d'%len(mine))
print('  possibly another member\'s: %d  %s'%(len(other),other[:12]))
print('  unnumbered / unclear: %d'%len(unk))
for f in unk[:15]: print('     ',f)
print()
print('=== CRITICAL: what must still be in backups/ ===')
b=os.path.join(d,'backups')
for k in ['test.cpp.before_TM600_TM601.bak','t53-20260916-211719','t55-target-20260916-213542']:
    p=os.path.join(b,k)
    print('  %-34s exists: %s'%(k,os.path.exists(p)))
bak=os.path.join(b,'test.cpp.before_TM600_TM601.bak')
if os.path.exists(bak):
    r=open(bak,'rb').read(); import hashlib
    print('  pre-change backup: %d B / %s'%(len(r),hashlib.sha256(r).hexdigest()[:24]))