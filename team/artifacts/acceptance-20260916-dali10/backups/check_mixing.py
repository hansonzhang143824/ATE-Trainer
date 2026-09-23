import sys,io,hashlib,re
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
p=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10\implementation-payload-TM600-TM601.cpp'
t=open(p,'rb').read().decode('utf-8-sig')
code=[l for l in t.split('\n') if not l.strip().startswith('//')]
print('=== MY PAYLOAD: all .Set(FV, <value>... on rails (code only) ===')
for l in code:
    if re.search(r'(PMID_HG2_FXVI|VBAT_PD3_FXVI|V1P5_U34PS_FXVI|SW12_U1REF_BST_ACM)\.Set\(',l):
        print('   ',l.strip()[:110])
print()
print('=== forbidden mixing check (code only): 3.5 V or 5 V used as PMID excitation? ===')
for l in code:
    if 'PMID_HG2_FXVI.Set' in l: print('   PMID line:',l.strip()[:100])
print('   any "3.5" in code:',[l.strip()[:70] for l in code if '3.5' in l])
print('   any VBAT = 5 in code:',[l.strip()[:70] for l in code if 'VBAT_PD3_FXVI.Set(FV, 5' in l])