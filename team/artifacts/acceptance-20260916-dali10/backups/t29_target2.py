import sys,io,os,re,hashlib,time
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
p=r'D:\PROJECT6-DALI\ForCodexDebug\source\test.cpp'
st=os.stat(p); r=open(p,'rb').read(); t=r.decode('utf-8-sig')
print('NOW: %d B / %s'%(len(r),hashlib.sha256(r).hexdigest()))
print('mtime %s'%time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(st.st_mtime)))
print()
L=t.split('\n')
print('=== symbol occurrence counts and line numbers ===')
for sym in ['DUT_API int TM600_HS_RDSON','DUT_API int TM601_LS_RDSON']:
    lines=[i+1 for i,l in enumerate(L) if sym in l]
    print('  %-32s total=%d lines=%s'%(sym.replace('DUT_API int ',''),t.count(sym),lines))
print()
print('=== SetOn lines and their line numbers ===')
for i,l in enumerate(L):
    if 'cbite.SetOn(' in l and ('K83_BUSH0_PMID' in l or 'K154_BUSH0_AMUX' in l):
        print('  L%d: %s'%(i+1,l.strip()[:190]))
print()
print('=== K109/K110 present? ===')
print('  K109_BUSL1_PB0:',t.count('K109_BUSL1_PB0'),' K110_ACM18_BST:',t.count('K110_ACM18_BST'))
print()
print('=== does the deployed file still match what I described as t23-deployed? ===')
print('  previous read (my t29 turn): 469714 B / 15c7d2b8d37b15648d552ad5dde14e57b5c0d520d05a41c8c41492a06236c01a')