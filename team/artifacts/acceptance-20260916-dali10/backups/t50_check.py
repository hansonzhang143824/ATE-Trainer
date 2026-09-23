import sys,io,os,re,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'implementation-payload-TM600-TM601.cpp')
r=open(p,'rb').read(); u=r.decode('utf-8-sig'); code=re.sub(r'//.*$','',u,flags=re.M)
print('=== post-edit self-check on 72d7bc3a... ===')
print('  payload %d B / %s'%(len(r),hashlib.sha256(r).hexdigest()))
print()
print('  content keys (executable):')
for k,exp in [('K48_ACM5_AMP_REF',1),('K76_ACM_BST',1),('K109_BUSL1_PB0',0),('K110_ACM18_BST',0),('K46',0)]:
    g=code.count(k); print('    %-20s %d (expect %d) %s'%(k,g,exp,'OK' if g==exp else 'MISMATCH'))
print('  invariants:')
for k,exp in [('delay_ms(1)',6),('delay_ms(2)',0),('SetClamp(50, 50)',2),('MeasureVI(200, 5, FPVIe_MV_X10)',2),('K126_V1P5_CAP',2),('ERROR_RES',2),('K57_CAP_BST_SW',2)]:
    g=code.count(k); print('    %-32s %d (expect %d) %s'%(k,g,exp,'OK' if g==exp else 'MISMATCH'))
print('    bare 126 = %d (expect 0)'%len(re.findall(r'(?<![\dA-Za-z_])126(?![\dA-Za-z_])',code)))
L=u.split('\n')
t6=next(i for i,l in enumerate(L) if l.startswith('DUT_API int TM600_HS_RDSON'))
t7=next(i for i,l in enumerate(L) if l.startswith('DUT_API int TM601_LS_RDSON'))
e7=next((i for i in range(t7+1,len(L)) if L[i].startswith('DUT_API int')),len(L))
print('  TM600 SetOn calls: %d ; ACM Sets TM600=%d TM601=%d'%(
 sum(1 for l in L[t6:t7] if 'cbite.SetOn(' in l),
 sum(1 for l in L[t6:t7] if 'SW12_U1REF_BST_ACM.Set' in re.sub(r'//.*$','',l)),
 sum(1 for l in L[t7:e7] if 'SW12_U1REF_BST_ACM.Set' in re.sub(r'//.*$','',l))))
print('  --check-extra still mentioned:', '--check-extra' in u)
print('  TM601段 unchanged (K109/K110 in code):', sum(l.count('K109')+l.count('K110') for l in re.sub(r'//.*$','',u,flags=re.M).split('\n')[t7:e7]))
print('  BOM',r[:3]==b'\xef\xbb\xbf','| loneLF',r.count(b'\n')-r.count(b'\r\n'))
print()
print('  the final TM600 SetOn line:')
for l in L[t6:t7]:
    if 'cbite.SetOn(' in l: print('   ',l.strip()[:170])