import sys,io,os,hashlib,re
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'review','t43-t42-review-and-unknown-ruling.md')
print('exists:',os.path.exists(p))
if os.path.exists(p):
    r=open(p,'rb').read()
    print('  %d B / %s'%(len(r),hashlib.sha256(r).hexdigest()))
    t=r.decode('utf-8-sig')
    print('  captain says: 7,439 B / d4c3835437a41c9f1bee7b15c2d381da69c99ceacd0503f5f6dbb0f1023e90a7')
    print()
    print('=== the ruling (first 55 lines) ===')
    for i,l in enumerate(t.split('\n')[:55]): print('  %s'%l[:140])