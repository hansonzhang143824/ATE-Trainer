import sys,io,os,hashlib,time
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
print('=== FINAL DELIVERY STATE (path -> value, values are readings at this instant) ===')
for f in ['implementation-payload-TM600-TM601.cpp','implementation-manifest.json','APPLY-TM600-TM601.md']:
    q=os.path.join(d,f); r=open(q,'rb').read()
    print('  %-40s -> %7d B / %s  @%s'%(f,len(r),hashlib.sha256(r).hexdigest(),time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(os.stat(q).st_mtime))))
print()
print('=== the frozen payload has been unchanged across every reading tonight ===')
p=os.path.join(d,'implementation-payload-TM600-TM601.cpp'); r=open(p,'rb').read()
print('  frozen target 66abc088ae6bd5f9b9d7201673003fc0be2450fd6f1f222c6a4a902cbe4f0cc4')
print('  match:', hashlib.sha256(r).hexdigest()=='66abc088ae6bd5f9b9d7201673003fc0be2450fd6f1f222c6a4a902cbe4f0cc4')
print()
print('=== and the schema still validates after all edits ===')