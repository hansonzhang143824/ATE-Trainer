import sys,io,os,hashlib,time
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
print('=== authoritative current values (measured now) ===')
for n in ['implementation-payload-TM600-TM601.cpp','t29-k110-evidence.md','APPLY-TM600-TM601.md','implementation-manifest.json','test-plan.json']:
    p=os.path.join(d,n); r=open(p,'rb').read()
    print('  %-44s %7d B / %s'%(n,len(r),hashlib.sha256(r).hexdigest()))
print()
print('  t4 keeps citing: payload 36381 / 73b511b7... , evidence 10062 / 1069e025...')
print('  current payload contains section 2b content:','PER-FUNCTION JUSTIFICATION' in open(os.path.join(d,'implementation-payload-TM600-TM601.cpp'),'rb').read().decode('utf-8-sig'))
print('  current evidence contains section 2b:','PER-FUNCTION JUSTIFICATION' in open(os.path.join(d,'t29-k110-evidence.md'),'rb').read().decode('utf-8-sig'))