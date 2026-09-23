import sys,io,os,json,hashlib,time
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
print('=== 1) verify MY manifest state (they claim 57,006 B / ac8c1f9f... @00:33:16) ===')
mp=os.path.join(d,'implementation-manifest.json')
r=open(mp,'rb').read(); h=hashlib.sha256(r).hexdigest()
print('  %d B / %s @%s'%(len(r),h,time.strftime('%H:%M:%S',time.localtime(os.stat(mp).st_mtime))))
print('  match their reading:', h=='ac8c1f9f5bc8655c4a80a8c27e3e482ec6a0b26f651b28e1516035a6dbbb1d9a')
J=json.loads(r.decode('utf-8-sig')); hh=J['handoffCitationRisk']
s=json.dumps(hh,ensure_ascii=False)
for pat in ['revisionBoundInventoryWarning','withdrawnFromAuthoritativeList','readerNoteOldRelaySetShorthand','2d0984d9']:
    print('    %-34s %d'%(pat,s.count(pat)))
print()
print('=== 2) verify THEIR mirrorSize correction: field value vs file size ===')
for cand in ['gate-logs-t28/t28-anchors.json','gate-logs-t28/setupArchitect-freeze-snapshots.json']:
    p=os.path.join(d,cand)
    if os.path.exists(p):
        b=open(p,'rb').read()
        print('  %-52s file = %d B'%(cand,len(b)))
        try:
            K=json.loads(b.decode('utf-8-sig'))
            found=[]
            def walk(o,path=''):
                if isinstance(o,dict):
                    for k,v in o.items():
                        if k=='mirrorSize': found.append((path+'/'+k,v))
                        walk(v,path+'/'+str(k))
                elif isinstance(o,list):
                    for i,v in enumerate(o): walk(v,path+'[%d]'%i)
            walk(K)
            print('      mirrorSize fields found:',found if found else 'NONE (they say 0 occurrences now)')
        except Exception as e: print('      parse:',e)
print()
print('  raw text search for the literal 97636 across gate-logs-t28:')
gl=os.path.join(d,'gate-logs-t28')
for f in sorted(os.listdir(gl)):
    p=os.path.join(gl,f)
    if os.path.isfile(p):
        t=open(p,'rb').read().decode('utf-8-sig',errors='replace')
        if '97636' in t: print('     %-52s contains 97636'%f)
        if 'mirrorSize' in t: print('     %-52s contains mirrorSize (%d x)'%(f,t.count('mirrorSize')))