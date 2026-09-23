import sys,io,os,hashlib,time
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'gate-logs-t28','setupArchitect-freeze-snapshots.json')
r=open(p,'rb').read(); h=hashlib.sha256(r).hexdigest()
print('=== the live ledger mirror, measured NOW ===')
print('  %d B / %s @%s'%(len(r),h,time.strftime('%H:%M:%S',time.localtime(os.stat(p).st_mtime))))
print('  they just cited 231,250 B / 6da19904... @02:17:40')
print('  match:', len(r)==231250)
print()
print('  the full reading sequence tonight:')
for v,who in [(159366,'schematic-expert (earlier)'),(196874,'schematic-expert'),(200758,'me'),(210620,'them'),(214271,'me'),(231250,'them'),(len(r),'ME, NOW')]:
    print('    %8d  <- %s'%(v,who))
print()
print('=== and my three artefacts, unchanged ===')
for f in ['implementation-payload-TM600-TM601.cpp','implementation-manifest.json','APPLY-TM600-TM601.md']:
    q=os.path.join(d,f); rr=open(q,'rb').read()
    print('  %-40s %7d B / %s'%(f,len(rr),hashlib.sha256(rr).hexdigest()[:16]))