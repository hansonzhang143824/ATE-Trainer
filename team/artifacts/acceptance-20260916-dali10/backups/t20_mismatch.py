import sys,io,os,json,hashlib,time
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
frozen={
 'setup-contract.json':'295d483a6d689e04d86744a7cfe55cb7936dd9b6ecb87ab5cc66b611b57b3d5c',
 'test-plan.json':'1925250df53f8b52126fdda9efa84ae84fe2bc8e529867e0965fc0ffe9a08016',
 'test-plan-tm600-tm601-measurement-excerpt.md':'9554d4d6f4fe878d05ba65fe5a79628192445f46ff74793e22d146f0e9ef89c8',
 'implementation-payload-TM600-TM601.cpp':'7902f5d91b0c07545b20ccc3103ca0f9bf76d5cb23dc44be6b5efd32312a9122',
 'backups/test.cpp.before_TM600_TM601.bak':'5c9cb3f9339f6db373afcff7504ef6b34924a4ca3042b5926cb612c819ac3317',
}
print('=== mismatch review: frozen value vs live (python plaintext, one pass) ===')
ok=True
for n,fz in frozen.items():
    p=os.path.join(d,n.replace('/',os.sep))
    if not os.path.exists(p): print('  %-52s MISSING'%n); ok=False; continue
    r=open(p,'rb').read(); h=hashlib.sha256(r).hexdigest()
    m = (h==fz)
    ok &= m
    print('  %-52s %8d B  %s  %s'%(n,len(r),h[:16],'MATCH' if m else 'MISMATCH'))
    if not m: print('      frozen %s'%fz)
print()
print('ALL MATCH:',ok)
print()
s=open(r'D:\PROJECT6-DALI\ForCodexDebug\source\test.cpp','rb').read()
print('target test.cpp:',len(s),'B',hashlib.sha256(s).hexdigest())
print('baseline intact:',hashlib.sha256(s).hexdigest()=='5c9cb3f9339f6db373afcff7504ef6b34924a4ca3042b5926cb612c819ac3317')