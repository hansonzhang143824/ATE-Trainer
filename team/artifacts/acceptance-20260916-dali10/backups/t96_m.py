import sys,io,os,json,hashlib,time
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'gate-logs-t28','setupArchitect-freeze-snapshots.json')
r=open(p,'rb').read(); u=r.decode('utf-8-sig')
print('=== the file that actually contains 97636 ===')
print('  file: setupArchitect-freeze-snapshots.json = %d B @%s'%(len(r),time.strftime('%H:%M:%S',time.localtime(os.stat(p).st_mtime))))
print('  (they reported 196,874 B; earlier 159,366 B)')
print()
print('=== every 97636 occurrence, in context ===')
L=u.split('\n')
for i,l in enumerate(L):
    if '97636' in l:
        print('  L%-5d %s'%(i+1,l.strip()[:190]))
print()
print('=== and the mirrorSize keys in this file, with their values ===')
try:
    K=json.loads(u)
    def walk(o,path=''):
        if isinstance(o,dict):
            for k,v in o.items():
                if 'mirror' in k.lower(): print('  %s/%s = %s'%(path,k,str(v)[:90]))
                walk(v,path+'/'+str(k))
        elif isinstance(o,list):
            for i,v in enumerate(o): walk(v,path+'[%d]'%i)
    walk(K)
except Exception as e: print('  (parse:',e,')')