import sys,io,os,re,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'implementation-payload-TM600-TM601.cpp')
r=open(p,'rb').read(); u=r.decode('utf-8-sig'); code=re.sub(r'//.*$','',u,flags=re.M)
L=u.split('\n')
print('=== POST-CHANGE SELF-CHECK on the final bytes ===')
print('  payload %d B / %s'%(len(r),hashlib.sha256(r).hexdigest()))
print('  BOM:',r[:3]==b'\xef\xbb\xbf',' CRLF:',r.count(b'\r\n'),' loneLF:',r.count(b'\n')-r.count(b'\r\n'))
print()
print('  content keys (proper strip):')
for k,exp in [('K48_ACM5_AMP_REF',1),('K76_ACM_BST',1),('K109_BUSL1_PB0',0),('K110_ACM18_BST',0),('K46',0)]:
    g=code.count(k); print('    %-20s %d (expect %d) %s'%(k,g,exp,'OK' if g==exp else 'MISMATCH'))
print('  invariants:')
for k,exp in [('delay_ms(1)',6),('delay_ms(2)',0),('SetClamp(50, 50)',2),('MeasureVI(200, 5, FPVIe_MV_X10)',2),('K126_V1P5_CAP',2),('ERROR_RES',2),('K57_CAP_BST_SW',2)]:
    g=code.count(k); print('    %-32s %d (expect %d) %s'%(k,g,exp,'OK' if g==exp else 'MISMATCH'))
print('    bare126 %d (expect 0) | K5+K44+K45 %d (expect 0)'%(len(re.findall(r'(?<![\dA-Za-z_])126(?![\dA-Za-z_])',code)),code.count('K5_VBUS_Cap')+code.count('K44_Cap_SW2_BST2')+code.count('K45_Cap_SW1_BST1')))
print('    PMID 10V step FXVIe_PLUS_20V:', ('FXVIe_PLUS_20V' in code) and ('Set(FV, 10, FXVIe_PLUS_10V' not in code))
t6=next(i for i,l in enumerate(L) if l.startswith('DUT_API int TM600_HS_RDSON'))
t7=next(i for i,l in enumerate(L) if l.startswith('DUT_API int TM601_LS_RDSON'))
print('  TM600 SetOn calls: %d | ACM Sets TM600=%d TM601=%d'%(
 sum(1 for i in range(t6,t7) if 'cbite.SetOn(' in L[i]),
 sum(1 for i in range(t6,t7) if 'SW12_U1REF_BST_ACM.Set' in re.sub(r'//.*$','',L[i])),
 sum(1 for i in range(t7,len(L)) if 'SW12_U1REF_BST_ACM.Set' in re.sub(r'//.*$','',L[i]))))
print('  "--check-extra" disable statement withdrawn:', 'is withdrawn' in u or 'DISABLE is needed any more' in u)
print()
e=os.path.join(d,'t50-payload-k76-evidence.md'); re_=open(e,'rb').read()
print('  evidence %d B / %s'%(len(re_),hashlib.sha256(re_).hexdigest()))