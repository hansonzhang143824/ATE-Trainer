import sys,io,os,re,hashlib,time
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
u=open(os.path.join(d,'implementation-payload-TM600-TM601.cpp'),'rb').read().decode('utf-8-sig')
L=u.split('\n'); code=re.sub(r'//.*$','',u,flags=re.M); cl=code.split('\n')
t6=[i for i,l in enumerate(L) if l.startswith('DUT_API int TM600_HS_RDSON')][0]
t7=[i for i,l in enumerate(L) if l.startswith('DUT_API int TM601_LS_RDSON')][0]
e7=next((i for i in range(t7+1,len(L)) if L[i].startswith('DUT_API int')),len(L))
def acm(a,b): return sum(1 for x in cl[a:b] if 'SW12_U1REF_BST_ACM.Set' in x)
print('=== t50 acceptance measurements on the frozen canonical ===')
print('  content keys (executable): K109=%d K110=%d K48=%d K76=%d'%(
 sum(l.count('K109_BUSL1_PB0') for l in cl),sum(l.count('K110_ACM18_BST') for l in cl),
 sum(l.count('K48_ACM5_AMP_REF') for l in cl),sum(l.count('K76_ACM_BST') for l in cl)))
print('  ACM Sets: TM600=%d  TM601=%d'%(acm(t6,t7),acm(t7,e7)))
print('  invariants: d1=%d d2=%d clamp=%d meas=%d bare126=%d K126=%d ERR=%d K5+44+45=%d K57=%d'%(
 cl.count('delay_ms(1)'),cl.count('delay_ms(2)'),cl.count('SetClamp(50, 50)'),cl.count('MeasureVI(200, 5, FPVIe_MV_X10)'),
 len(re.findall(r'(?<![\dA-Za-z_])126(?![\dA-Za-z_])',code)),cl.count('K126_V1P5_CAP'),cl.count('ERROR_RES'),
 cl.count('K5_VBUS_Cap')+cl.count('K44_Cap_SW2_BST2')+cl.count('K45_Cap_SW1_BST1'),cl.count('K57_CAP_BST_SW')))
print('  PMID 10V step uses FXVIe_PLUS_20V:', 'FXVIe_PLUS_20V' in code and 'Set(FV, 10, FXVIe_PLUS_10V' not in code)
r=open(os.path.join(d,'implementation-payload-TM600-TM601.cpp'),'rb').read()
print('  BOM',r[:3]==b'\xef\xbb\xbf','| loneLF',r.count(b'\n')-r.count(b'\r\n'))
print('  "relays.md L31 口诀" referenced in payload:', '记忆口诀' in u or 'L31' in u)
print()
print('=== the TWO t50 items that would require a WRITE ===')
print('  (2b) coupling cost for retaining K109/K110 registered in the payload comment:',
      ('FPVIe1_FL_BUS_S1' in u) or ('FPVIe1_SL_BUS_S1' in u))
print('  (3)  operational-fact mechanism rewrite in the TM600 block (K48 NC->K49 SW1/SW2; K48 ON -> K76 -> BST):',
      ('NC' in u and 'SW1' in u and 'SW2' in u))
for i,l in enumerate(L[t6:t7]):
    if 'SW1' in l or 'SW2' in l or 'FPVIe1' in l: print('     TM600 L%d: %s'%(t6+i+1,l.strip()[:120]))