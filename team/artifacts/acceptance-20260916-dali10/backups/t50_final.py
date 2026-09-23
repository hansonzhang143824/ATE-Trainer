import sys,io,os,re,hashlib,time
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'implementation-payload-TM600-TM601.cpp')
r=open(p,'rb').read(); u=r.decode('utf-8-sig')
code=re.sub(r'//.*$','',u,flags=re.M)
print('=== DEFINITIVE (whole-file, proper strip) ===')
print('  payload %d B / %s @%s'%(len(r),hashlib.sha256(r).hexdigest(),time.strftime('%H:%M:%S',time.localtime(os.stat(p).st_mtime))))
for k,exp in [('delay_ms(1)',6),('delay_ms(2)',0),('SetClamp(50, 50)',2),('MeasureVI(200, 5, FPVIe_MV_X10)',2),
              ('K126_V1P5_CAP',2),('ERROR_RES',2),('K57_CAP_BST_SW',2),('K109_BUSL1_PB0',1),('K110_ACM18_BST',1),
              ('K48_ACM5_AMP_REF',1),('K76_ACM_BST',1),('K46',0)]:
    g=code.count(k); print('  %-34s %d (expect %d) %s'%(k,g,exp,'OK' if g==exp else 'MISMATCH'))
print('  bare 126: %d (expect 0)'%len(re.findall(r'(?<![\dA-Za-z_])126(?![\dA-Za-z_])',code)))
print('  K5+K44+K45: %d (expect 0)'%(code.count('K5_VBUS_Cap')+code.count('K44_Cap_SW2_BST2')+code.count('K45_Cap_SW1_BST1')))
L=u.split('\n')
t6=next(i for i,l in enumerate(L) if l.startswith('DUT_API int TM600_HS_RDSON'))
t7=next(i for i,l in enumerate(L) if l.startswith('DUT_API int TM601_LS_RDSON'))
e7=next((i for i in range(t7+1,len(L)) if L[i].startswith('DUT_API int')),len(L))
print('  ACM Sets: TM600=%d  TM601=%d'%(sum(1 for l in L[t6:t7] if 'SW12_U1REF_BST_ACM.Set' in re.sub(r'//.*$','',l)),
                                          sum(1 for l in L[t7:e7] if 'SW12_U1REF_BST_ACM.Set' in re.sub(r'//.*$','',l))))
print('  PMID 10V step = FXVIe_PLUS_20V:', ('FXVIe_PLUS_20V' in code) and ('Set(FV, 10, FXVIe_PLUS_10V' not in code))
print('  BOM',r[:3]==b'\xef\xbb\xbf','| loneLF',r.count(b'\n')-r.count(b'\r\n'))
print('  SetOn calls in TM600 body: %d'%sum(1 for l in L[t6:t7] if 'cbite.SetOn(' in l))