import sys,io,os,json,hashlib,re
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
base=r'D:\Newtest\DSH\ATE-Coding-Plat'
d=os.path.join(base,'team','artifacts','acceptance-20260916-dali10')
J=json.loads(open(os.path.join(d,'acceptance-report.json'),'rb').read().decode('utf-8-sig'))
cov=J['coverage']
print('=== MY FALSE ALARM, corrected: those hashes belong to OTHER artefacts ===')
for i,c in enumerate(cov):
    art=str(c.get('artifact',''))
    base_name=os.path.basename(art) if art else '(none)'
    h=str(c.get('artifactSha256',''))[:24]
    if art and os.path.exists(art):
        real=hashlib.sha256(open(art,'rb').read()).hexdigest()[:24]
        state='CURRENT' if h==real else 'STALE'
    elif art and os.path.exists(os.path.join(base,art.replace('/','\\'))):
        real=hashlib.sha256(open(os.path.join(base,art.replace('/','\\')),'rb').read()).hexdigest()[:24]
        state='CURRENT' if h==real else 'STALE'
    else:
        state='(artifact not resolvable here)'
    print('  coverage[%-2d] %-44s hash=%s  %s'%(i,base_name[:44],h,state))