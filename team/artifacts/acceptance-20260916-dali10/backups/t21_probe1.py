import sys,io,os,re,hashlib,glob
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
tgt=r'D:\PROJECT6-DALI\ForCodexDebug\source\test.cpp'
r=open(tgt,'rb').read(); t=r.decode('utf-8-sig')
print('target test.cpp: %d B / %s'%(len(r),hashlib.sha256(r).hexdigest()))
print('expected after t20 write: 462848 B / 3dbceb496d79d7d08631713b98e46c0c2ba6163eaf5356a87dded677e35ba479')
print()
print('=== 126 occurrences in target ===')
for i,l in enumerate(t.split('\n')):
    if re.search(r'\b126\b',l): print('  %5d: %s'%(i+1,l.strip()[:120]))
print()
print('=== is there a #define for 126 anywhere in the tree? ===')
for f in glob.glob(r'D:\PROJECT6-DALI\ForCodexDebug\source\*.h'):
    h=open(f,'rb').read().decode('utf-8-sig',errors='replace')
    for i,l in enumerate(h.split('\n')):
        if re.search(r'#define\s+\S*126\b',l) or re.search(r'#define\s+\S+\s+126\b',l):
            print('  %s:%d %s'%(os.path.basename(f),i+1,l.strip()))
print()
print('=== my payload SetOn lines ===')
p=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10\implementation-payload-TM600-TM601.cpp'
u=open(p,'rb').read().decode('utf-8-sig')
for l in u.split('\n'):
    if 'cbite.SetOn(' in l: print('  ',l.strip()[:130])
print()
print('=== K44/K45/K57/K5 usage in target for TM601 ===')
start=t.find('DUT_API int TM601_LS_RDSON'); end=t.find('DUT_API int',start+10)
blk=t[start:end if end>0 else len(t)]
for k in ['K44','K45','K57','K5_','K13','K85','K126','126']:
    print('  TM601 block mentions %-6s %d'%(k,blk.count(k)))