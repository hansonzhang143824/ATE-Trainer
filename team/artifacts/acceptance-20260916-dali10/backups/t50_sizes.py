import sys,io,os,hashlib,time
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
for n in ['implementation-payload-TM600-TM601.cpp','t50-payload-k76-evidence.md']:
    p=os.path.join(d,n); r=open(p,'rb').read()
    print('  %-42s %6d B / %s @%s'%(n,len(r),hashlib.sha256(r).hexdigest(),time.strftime('%H:%M:%S',time.localtime(os.stat(p).st_mtime))))