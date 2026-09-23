import sys,io,os,re
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
src=open(r'D:\PROJECT6-DALI\ForCodexDebug\source\test.cpp','rb').read().decode('utf-8-sig')
L=src.split('\n')
print('=== deployed tree: the FULL SetOn lines that close K48/K76 ===')
for i,l in enumerate(L):
    if 'cbite.SetOn(' in l and 'K48_ACM5_AMP_REF' in l:
        print('  L%d: %s'%(i+1,l.strip()[:200]))
print()
print('=== the comment that names the mechanism (deployed L6997 region) ===')
for i in range(6993,7002): print('  L%d| %s'%(i+1,L[i].rstrip()[:150]))
print()
print('=== StdAfx defines for these relays ===')
h=open(r'D:\PROJECT6-DALI\ForCodexDebug\source\StdAfx.h','rb').read().decode('utf-8-sig',errors='replace')
for m in re.finditer(r'#define\s+(K48_[A-Za-z0-9_]*|K76_[A-Za-z0-9_]*|K46_[A-Za-z0-9_]*)\s+(\d+)',h):
    print('  ',m.group(0))
print()
print('=== does the deployed TM600/TM601 region close K48/K76? (the t23+rdsons area) ===')
s=src.find('DUT_API int TM600_HS_RDSON'); e=src.find('DUT_API int',src.find('DUT_API int TM601_LS_RDSON')+10)
blk=src[s:e]
for r in ['K48','K76','K109','K110']:
    print('   %-5s in the RDSON region: %s'%(r, r in blk))