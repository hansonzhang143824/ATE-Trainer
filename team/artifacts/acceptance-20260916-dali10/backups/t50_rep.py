import sys,io,os,re,hashlib,time
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'implementation-payload-TM600-TM601.cpp')
r=open(p,'rb').read(); u=r.decode('utf-8-sig'); code=re.sub(r'//.*$','',u,flags=re.M)
print('=== (b) FINAL STATE, measured now ===')
print('  size   = %d B'%len(r))
print('  sha256 = %s'%hashlib.sha256(r).hexdigest())
print('  mtime  = %s'%time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(os.stat(p).st_mtime)))
print('  BOM=%s  CRLF=%d  loneLF=%d'%(r[:3]==b'\xef\xbb\xbf',r.count(b'\r\n'),r.count(b'\n')-r.count(b'\r\n')))
print()
print('  captain measured: 42,998 / c03632d9... @20:59:12  -> that is the SECOND-to-last write')
print('  reviewer measured: 42,440 / 72d7bc3a...            -> the LF-broken intermediate')
print()
print('=== 9-item TM600 SetOn (verbatim) ===')
L=u.split('\r\n')
t6=next(i for i,l in enumerate(L) if l.startswith('DUT_API int TM600_HS_RDSON'))
t7=next(i for i,l in enumerate(L) if l.startswith('DUT_API int TM601_LS_RDSON'))
for i in range(t6,t7):
    if 'cbite.SetOn(' in L[i]: print('  L%d: %s'%(i+1,L[i].strip()))
print()
print('=== content keys + invariants (executable) ===')
print('  K48=%d K76=%d K109=%d K110=%d K46=%d'%(code.count('K48_ACM5_AMP_REF'),code.count('K76_ACM_BST'),code.count('K109_BUSL1_PB0'),code.count('K110_ACM18_BST'),code.count('K46')))
print('  delay_ms(1)=%d delay_ms(2)=%d clamp=%d MeasureVI=%d K126=%d ERROR_RES=%d K57=%d bare126=%d K5+44+45=%d'%(
 code.count('delay_ms(1)'),code.count('delay_ms(2)'),code.count('SetClamp(50, 50)'),code.count('MeasureVI(200, 5, FPVIe_MV_X10)'),
 code.count('K126_V1P5_CAP'),code.count('ERROR_RES'),code.count('K57_CAP_BST_SW'),
 len(re.findall(r'(?<![\dA-Za-z_])126(?![\dA-Za-z_])',code)),code.count('K5_VBUS_Cap')+code.count('K44_Cap_SW2_BST2')+code.count('K45_Cap_SW1_BST1')))
print('  SetOn calls total: %d (TM600 1 / TM601 1)'%code.count('cbite.SetOn('))
print()
print('=== (③) the --check-extra mention: what does it SAY now? ===')
for i,l in enumerate(L):
    if '--check-extra' in l: print('  L%d: %s'%(i+1,l.strip()[:150]))
print()
print('=== the two-case operational fact present? ===')
for pat in ['UN-ENERGISED','K48 ENERGISED','SW1_F/SW1_S']:
    print('  %-16s %d'%(pat,u.count(pat)))