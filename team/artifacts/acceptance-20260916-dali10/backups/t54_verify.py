import sys,io,os,re,hashlib,time
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'implementation-payload-TM600-TM601.cpp')
r=open(p,'rb').read(); u=r.decode('utf-8-sig'); code=re.sub(r'//.*$','',u,flags=re.M)
print('=== VERIFY THE CAPTAIN\'S ASSERTIONS ===')
print('  size/sha  : %d B / %s'%(len(r),hashlib.sha256(r).hexdigest()))
print('  expected  : 43806 B / 66abc088ae6bd5f9b9d7201673003fc0be2450fd6f1f222c6a4a902cbe4f0cc4')
print('  mtime     : %s (captain says 21:09:24)'%time.strftime('%H:%M:%S',time.localtime(os.stat(p).st_mtime)))
print('  BOM=%s CRLF=%d loneLF=%d (captain: BOM yes, CRLF 566, loneLF 0)'%(r[:3]==b'\xef\xbb\xbf',r.count(b'\r\n'),r.count(b'\n')-r.count(b'\r\n')))
print()
print('  all-text K109/K110 (captain says 3 each):  K109=%d  K110=%d'%(u.count('K109_BUSL1_PB0'),u.count('K110_ACM18_BST')))
print('  executable K109/K110 (must be 0 each)   :  K109=%d  K110=%d'%(code.count('K109_BUSL1_PB0'),code.count('K110_ACM18_BST')))
print('  executable K48/K76/K46 = %d / %d / %d'%(code.count('K48_ACM5_AMP_REF'),code.count('K76_ACM_BST'),code.count('K46')))
print('  SetOn calls total = %d'%code.count('cbite.SetOn('))
L=u.split('\r\n')
t6=next(i for i,l in enumerate(L) if l.startswith('DUT_API int TM600_HS_RDSON'))
t7=next(i for i,l in enumerate(L) if l.startswith('DUT_API int TM601_LS_RDSON'))
for i in range(t6,len(L)):
    if 'cbite.SetOn(' in L[i]:
        owner='TM600' if i<t7 else 'TM601'
        print('  SetOn %s at L%d: %s'%(owner,i+1,L[i].strip()[:120]))
print('  SUPERSEDED markers: %d (captain says 2)'%u.count('[SUPERSEDED BY t50'))
print()
print('  where K109/K110 still appear (should be comments only):')
for i,l in enumerate(L):
    if ('K109_BUSL1_PB0' in l or 'K110_ACM18_BST' in l):
        print('    L%-4d [%s] %s'%(i+1,'COMMENT' if l.strip().startswith('//') else '*** CODE ***',l.strip()[:105]))