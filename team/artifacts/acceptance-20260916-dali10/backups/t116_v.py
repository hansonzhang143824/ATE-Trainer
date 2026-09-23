import sys,io,os,json,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
base=r'D:\Newtest\DSH\ATE-Coding-Plat'
d=os.path.join(base,'team','artifacts','acceptance-20260916-dali10')
J=json.loads(open(os.path.join(d,'acceptance-report.json'),'rb').read().decode('utf-8-sig'))
cov=J['coverage']
print('=== 1) THEIR BOUNDARY RELEASE: is coverage[11] a directory (not a permission issue)? ===')
for i in (5,11):
    art=cov[i].get('artifact')
    p=os.path.join(base, str(art).replace('/',os.sep))
    print('  coverage[%d] artifact=%r'%(i,art))
    print('     exists=%s is_file=%s is_dir=%s'%(os.path.exists(p), os.path.isfile(p), os.path.isdir(p)))
    print('     artifactSha256=%r'%str(cov[i].get('artifactSha256'))[:70])
print('  => if [11] is a directory, my PermissionError was the consequence of hashing a directory, NOT a sandbox bound.')
print()
print('=== 2) FULL 12-ENTRY CLASSIFICATION (their 4 EQUAL / 6 DIFFERS(2 MARKED) / 2 N/A) ===')
eq=[];dif=[];na=[]
for i,c in enumerate(cov):
    art=str(c.get('artifact','')); h=str(c.get('artifactSha256',''))
    if not (len(h)==64 and all(ch in '0123456789abcdef' for ch in h)):
        na.append(i); continue
    p=os.path.join(base, art.replace('/',os.sep))
    if os.path.isfile(p):
        real=hashlib.sha256(open(p,'rb').read()).hexdigest()
        (eq if real==h else dif).append((i,os.path.basename(art),'MARKED' if 'artifactSha256IsHistorical' in c else ''))
    else:
        na.append(i)
print('  EQUAL   : %s'%[x[0] for x in eq])
print('  DIFFERS : %s'%[(x[0],x[1],x[2]) for x in dif])
print('  NOT APPL: %s'%na)
print()
print('  counts: EQUAL=%d DIFFERS=%d (marked=%d) N/A=%d'%(len(eq),len(dif),sum(1 for x in dif if x[2]=='MARKED'),len(na)))