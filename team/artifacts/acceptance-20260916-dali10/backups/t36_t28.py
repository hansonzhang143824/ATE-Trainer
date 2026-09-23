import sys,io,os,json,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
g=os.path.join(d,'gate-logs-t28')
print('=== gate-logs-t28 contents ===')
for f in sorted(os.listdir(g)):
    p=os.path.join(g,f)
    if os.path.isfile(p):
        r=open(p,'rb').read(); print('  %-28s %7d B %s'%(f,len(r),hashlib.sha256(r).hexdigest()[:16]))
print()
p=os.path.join(g,'t28-red-proof.json')
if os.path.exists(p):
    J=json.loads(open(p,'rb').read().decode('utf-8-sig'))
    print('=== t28-red-proof.json (keys + shape) ===')
    def show(o,pre='',depth=0):
        if depth>2: return
        if isinstance(o,dict):
            for k,v in list(o.items())[:14]:
                if isinstance(v,(dict,list)): print('  %s%s: <%s>'%(pre,k,type(v).__name__)); show(v,pre+'  ',depth+1)
                else: print('  %s%s = %s'%(pre,k,str(v)[:110]))
        elif isinstance(o,list):
            for i,v in enumerate(o[:6]): show(v,pre+'[%d]'%i+' ',depth+1)
    show(J)