import sys,io,os,json,hashlib,time
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
M=json.loads(open(os.path.join(d,'implementation-manifest.json'),'rb').read().decode('utf-8-sig'))
print('=== MANIFEST ENTRY vs DISK, one by one ===')
for e in M['handoffCitationRisk']['authoritativeCurrentValues']:
    a=e.get('artefact'); p=os.path.join(d,a)
    if not os.path.exists(p):
        print('  %-38s NOT FOUND on disk (manifest claims %d B)'%(a,e.get('size'))); continue
    r=open(p,'rb').read(); h=hashlib.sha256(r).hexdigest(); mt=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(os.stat(p).st_mtime))
    ok = (len(r)==e.get('size')) and (h==e.get('sha256'))
    print('  %-38s %s'%(a,'OK' if ok else '*** STALE ***'))
    if not ok:
        print('      manifest: %d B / %s'%(e.get('size'),str(e.get('sha256'))[:24]))
        print('      on disk : %d B / %s  @%s'%(len(r),h[:24],mt))
print()
print('=== also check the OTHER in-scope artefacts I name ===')
for a in ['t50-payload-k76-evidence.md','t38-acm-pin5-exposure.md','t40-tm601-bst-evidence.md']:
    p=os.path.join(d,a)
    if os.path.exists(p):
        r=open(p,'rb').read()
        print('  %-34s %7d B / %s @%s'%(a,len(r),hashlib.sha256(r).hexdigest()[:20],time.strftime('%H:%M:%S',time.localtime(os.stat(p).st_mtime))))