import sys,io,os,json,hashlib,time
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
print('=== 1) verify THEIR evidence: t28-anchors.json mirrorSize claim ===')
for cand in ['t28-anchors.json','t28_anchors.json']:
    p=os.path.join(d,cand)
    if os.path.exists(p):
        r=open(p,'rb').read()
        print('  found %s: %d B / %s'%(cand,len(r),hashlib.sha256(r).hexdigest()[:24]))
        try:
            J=json.loads(r.decode('utf-8-sig'))
            def walk(o,path=''):
                if isinstance(o,dict):
                    for k,v in o.items():
                        if 'mirror' in k.lower() and isinstance(v,(int,str)):
                            print('    %s/%s = %s'%(path,k,v))
                        walk(v,path+'/'+str(k))
                elif isinstance(o,list):
                    for i,v in enumerate(o): walk(v,path+'[%d]'%i)
            walk(J)
        except Exception as e: print('    (not JSON:',e,')')
print()
print('=== 2) does MY manifest already cover the t42/t44 reader risk? ===')
mp=os.path.join(d,'implementation-manifest.json')
r=open(mp,'rb').read(); M=json.loads(r.decode('utf-8-sig'))
print('  manifest: %d B / %s'%(len(r),hashlib.sha256(r).hexdigest()[:24]))
h=M['handoffCitationRisk']
print('  handoffCitationRisk keys:',list(h.keys()))
s=json.dumps(h,ensure_ascii=False)
for pat in ['[48,61,76]','[48,60,61,76]','{48,60,61,76,83}','t42','t44','t43','old incomplete']:
    print('    mentions %-16s %d'%(pat,s.count(pat)))