import sys,io,os,json,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
live=json.loads(open(os.path.join(d,'test-plan.json'),'rb').read().decode('utf-8-sig'))
old =json.loads(open(os.path.join(d,'test-plan.v20.json'),'rb').read().decode('utf-8-sig'))
print('=== structural diff: live v20 (fabdd24f) vs archived v20 (1925250d) ===')
def keys(o,pre=''):
    out={}
    if isinstance(o,dict):
        for k,v in o.items(): out.update(keys(v,pre+'/'+str(k)))
    elif isinstance(o,list):
        for i,v in enumerate(o): out.update(keys(v,pre+'[%d]'%i))
    else: out[pre]=o
    return out
a,b=keys(live),keys(old)
onlyA=[k for k in a if k not in b]; onlyB=[k for k in b if k not in a]
diff=[k for k in a if k in b and a[k]!=b[k]]
print('  keys only in live :',len(onlyA)); [print('     +',k) for k in onlyA[:12]]
print('  keys only in old  :',len(onlyB)); [print('     -',k) for k in onlyB[:12]]
print('  changed values    :',len(diff))
for k in diff[:25]:
    print('     ~ %s'%k)
    print('        live:',str(a[k])[:110])
    print('        old :',str(b[k])[:110])
print()
print('=== inputArtifacts comparison (the known drift source) ===')
la=live.get('inputArtifacts'); oa=old.get('inputArtifacts')
import json as J
print('  live inputArtifacts:',J.dumps(la,ensure_ascii=False)[:300] if la else '(absent)')
print('  old  inputArtifacts:',J.dumps(oa,ensure_ascii=False)[:300] if oa else '(absent)')