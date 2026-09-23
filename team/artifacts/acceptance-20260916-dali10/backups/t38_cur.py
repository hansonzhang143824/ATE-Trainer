import sys,io,os,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
print('=== CURRENT values (measured now) ===')
for n in ['implementation-payload-TM600-TM601.cpp','t40-tm601-bst-evidence.md','t29-k110-evidence.md','APPLY-TM600-TM601.md','implementation-manifest.json']:
    p=os.path.join(d,n); r=open(p,'rb').read()
    print('  %-40s %6d B / %s'%(n,len(r),hashlib.sha256(r).hexdigest()))
print()
print('=== what changed in t38 (the payload t4 will hand the reviewer) ===')
u=open(os.path.join(d,'implementation-payload-TM600-TM601.cpp'),'rb').read().decode('utf-8-sig')
code=[l for l in u.split('\n') if not l.strip().startswith('//')]
t600=[i for i,l in enumerate(code) if 'DUT_API int TM600_HS_RDSON' in l][0]
t601=[i for i,l in enumerate(code) if 'DUT_API int TM601_LS_RDSON' in l][0]
print('  TM600 body: K109=%d K110=%d  (the t29 closure - COMPLETE)'%(
  sum(l.count("K109_BUSL1_PB0") for l in code[t600:t601]),sum(l.count("K110_ACM18_BST") for l in code[t600:t601])))
print('  TM601 body: K109=%d K110=%d  ACM Sets=%d  (t38 removed the dangling drive)'%(
  sum(l.count("K109_BUSL1_PB0") for l in code[t601:]),sum(l.count("K110_ACM18_BST") for l in code[t601:]),
  sum(1 for l in code[t601:] if 'SW12_U1REF_BST_ACM.Set' in l)))