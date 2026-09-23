import sys,io,os,re,hashlib,time
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
print('=== current values with mtimes (measured now) ===')
for n in ['implementation-payload-TM600-TM601.cpp','t40-tm601-bst-evidence.md','t29-k110-evidence.md','APPLY-TM600-TM601.md','implementation-manifest.json']:
    p=os.path.join(d,n); r=open(p,'rb').read()
    print('  %-40s %6d B / %s  @%s'%(n,len(r),hashlib.sha256(r).hexdigest(),time.strftime('%H:%M:%S',time.localtime(os.stat(p).st_mtime))))
print()
print('  my frozen value was: payload 39457 B / 2d0984d992d5d8cb11868660b29cf2c7786ff27367bd7b24b80df4ccf48997f9')
print()
u=open(os.path.join(d,'implementation-payload-TM600-TM601.cpp'),'rb').read().decode('utf-8-sig')
c=re.sub(r'//.*$','',u,flags=re.M)
print('=== content check on the LIVE payload ===')
print('  t29 PER-FUNCTION JUSTIFICATION (TM601 block):',u.count('PER-FUNCTION JUSTIFICATION'))
print('  t38 STATUS/section marker present in payload?:','t38 REMOVED the ACM excitation' in u)
print('  K109_BUSL1_PB0 total:',c.count('K109_BUSL1_PB0'),' K110_ACM18_BST total:',c.count('K110_ACM18_BST'))
s=u.find('DUT_API int TM601_LS_RDSON')
b=u[s:]
print('  TM601 ACM Sets:',sum(1 for l in b.split('\n') if 'SW12_U1REF_BST_ACM.Set' in l and not l.strip().startswith('//')))
print('  TM600 ACM Sets:',sum(1 for l in u[:s].split('\n') if 'SW12_U1REF_BST_ACM.Set' in l and not l.strip().startswith('//')))
print('  delays/clamp/meas: d1=%d d2=%d clamp=%d meas=%d'%(c.count('delay_ms(1)'),c.count('delay_ms(2)'),c.count('SetClamp(50, 50)'),c.count('MeasureVI(200, 5, FPVIe_MV_X10)')))