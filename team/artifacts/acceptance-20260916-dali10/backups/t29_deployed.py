import sys,io,os,re,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
tgt=r'D:\PROJECT6-DALI\ForCodexDebug\source\test.cpp'
r=open(tgt,'rb').read(); t=r.decode('utf-8-sig')
print('deployed test.cpp: %d B / %s'%(len(r),hashlib.sha256(r).hexdigest()))
print()
s=t.find('DUT_API int TM600_HS_RDSON'); e=t.find('DUT_API int TM601_LS_RDSON')
blk=t[s:e if e>s else s+3000]
print('=== deployed TM600 SetOn ===')
for l in blk.split('\n'):
    if 'cbite.SetOn(' in l: print('  ',l.strip()[:200])
print()
print('=== deployed presence checks ===')
for k in ['K109_BUSL1_PB0','K110_ACM18_BST','K126_V1P5_CAP',', 126,','K5_VBUS_Cap','K44_Cap_SW2_BST2','K45_Cap_SW1_BST1','ERROR_RES','i_meas[site] > 0.1']:
    print('  %-22s %d'%(k,t.count(k)))
print()
s2=t.find('DUT_API int TM601_LS_RDSON'); e2=t.find('\nDUT_API int',s2+10)
b2=t[s2:e2 if e2>0 else len(t)] if s2>0 else ''
print('=== deployed TM601 SetOn ===')
for l in b2.split('\n'):
    if 'cbite.SetOn(' in l: print('  ',l.strip()[:200])
print()
print('=== which of my revisions is this? compare against my payloads ===')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
pay=open(os.path.join(d,'implementation-payload-TM600-TM601.cpp'),'rb').read().decode('utf-8-sig')
body=pay[pay.find('DUT_API int TM600_HS_RDSON'):]
print('  my new payload body (with K109/K110) is byte-contained in deployed:', body.rstrip('\n') in t)
print('  deployed contains the K126 fix:', 'K126_V1P5_CAP' in t)
print('  deployed contains the ERROR_RES fail-closed guard:', 'ERROR_RES' in t)