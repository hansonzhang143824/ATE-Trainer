import sys,io,os,re,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'implementation-payload-TM600-TM601.cpp')
u=open(p,'rb').read().decode('utf-8-sig')
edits=0
def rep(old,new,label,expect=1):
    global u,edits
    n=u.count(old)
    print('  %-58s found=%d %s'%(label,n,'OK' if n==expect else 'SKIP'))
    if n==expect: u=u.replace(old,new); edits+=1

# F4: PMID 15 V -> 30 V range (16.5 V over-ranges the 10 V range)
rep('PMID_HG2_FXVI.Set(FV, 15, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);',
    'PMID_HG2_FXVI.Set(FV, 15, FXVIe_PLUS_30V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);', 'PMID 15 V -> 30 V (was OVER-RANGE)')
# F4: PMID 9 V -> 20 V range (10 V fails the >=2x rule)
rep('PMID_HG2_FXVI.Set(FV, 9, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);',
    'PMID_HG2_FXVI.Set(FV, 9, FXVIe_PLUS_20V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);', 'PMID 9 V -> 20 V (>=2x rule)')
# F4: ACM divider 10 V -> 20 V step
rep('SW12_U1REF_BST_ACM.Set(FV, 10, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);',
    'SW12_U1REF_BST_ACM.Set(FV, 10, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);', 'ACM 10 V -> 20 V')
open(p,'wb').write(b'\xef\xbb\xbf'+u.replace('\r\n','\n').replace('\n','\r\n').encode('utf-8'))
r=open(p,'rb').read(); v=r.decode('utf-8-sig'); code=[l for l in v.split('\n') if not l.strip().startswith('//')]
print()
print('applied %d edits; payload %d B / %s'%(edits,len(r),hashlib.sha256(r).hexdigest()))
print('remaining FXVIe 10V at non-zero values:')
for l in code:
    if 'FXVIe_PLUS_10V' in l and re.search(r'Set\(FV, (?!0,)',l): print('   ',l.strip()[:110])
print('remaining ACM 10V at non-zero values:')
for l in code:
    if 'ACM200_10V' in l and re.search(r'Set\(FV, (?!0,)',l): print('   ',l.strip()[:110])