import sys,io,os,re
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
u=open(os.path.join(d,'implementation-payload-TM600-TM601.cpp'),'rb').read().decode('utf-8-sig')
code=[l for l in u.split('\n') if not l.strip().startswith('//')]
t600=[i for i,l in enumerate(code) if 'DUT_API int TM600_HS_RDSON' in l][0]
t601=[i for i,l in enumerate(code) if 'DUT_API int TM601_LS_RDSON' in l][0]
b600=code[t600:t601]; b601=code[t601:]
print('=== executable ACM Set counts per function ===')
print('  TM600 body SW12 ACM Sets:',sum(1 for l in b600 if 'SW12_U1REF_BST_ACM.Set' in l))
print('  TM601 body SW12 ACM Sets:',sum(1 for l in b601 if 'SW12_U1REF_BST_ACM.Set' in l),'(must be 0 after t38)')
print('  payload-wide (header mentions excluded from code):',sum(1 for l in code if 'SW12_U1REF_BST_ACM.Set' in l))
print()
print('=== TM600 body: any change? (list its ACM lines) ===')
for l in b600:
    if 'SW12_U1REF_BST_ACM' in l: print('   ',l.strip()[:110])
print()
print('=== TM601 teardown still coherent after removal (L486-L500 region) ===')
for i,l in enumerate(b601):
    if any(k in l for k in ('Step 5','RELAY_OFF','FPVI0.Set(FV, 0','PMID_HG2_FXVI.Set(FV, 0','V1P5_U34PS_FXVI.Set(FV, 0','VBAT_PD3_FXVI.Set(FV, 0')):
        print('   ',l.strip()[:110])