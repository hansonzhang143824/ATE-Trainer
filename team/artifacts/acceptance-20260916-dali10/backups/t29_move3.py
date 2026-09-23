import sys,io,os,json,hashlib,time
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'test-plan.json'); st=os.stat(p); r=open(p,'rb').read()
live=json.loads(r.decode('utf-8-sig'))
print('live test-plan.json: %d B / %s'%(len(r),hashlib.sha256(r).hexdigest()))
print('mtime %s'%time.strftime('%H:%M:%S',time.localtime(st.st_mtime)))
print('revision:',str(live.get('revision'))[:120])
prev=json.loads(open(os.path.join(d,'test-plan.v20.json'),'rb').read().decode('utf-8-sig'))
print('archived v20 (1925250d):',len(open(os.path.join(d,'test-plan.v20.json'),'rb').read()),'B')
def flat(o,pre=''):
    out={}
    if isinstance(o,dict):
        for k,v in o.items(): out.update(flat(v,pre+'/'+str(k)))
    elif isinstance(o,list):
        for i,v in enumerate(o): out.update(flat(v,pre+'[%d]'%i))
    else: out[pre]=o
    return out
a,b=flat(live),flat(prev)
onlyA=[k for k in a if k not in b]; onlyB=[k for k in b if k not in a]
diff=[k for k in a if k in b and a[k]!=b[k]]
print()
print('=== diff live vs archived v20 ===')
print('  keys only in live:',len(onlyA))
for k in onlyA[:10]: print('     +',k,'=',str(a[k])[:90])
print('  keys only in old :',len(onlyB))
for k in onlyB[:10]: print('     -',k,'=',str(b[k])[:90])
print('  changed values   :',len(diff))
for k in diff[:12]: print('     ~',k,'| live:',str(a[k])[:70],'| old:',str(b[k])[:70])
print()
print('revisionHistory entries:',len(live.get('revisionHistory') or []))