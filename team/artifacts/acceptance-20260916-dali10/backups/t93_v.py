import sys,io,os,json,re,hashlib,time
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
mp=os.path.join(d,'implementation-manifest.json')
M=json.loads(open(mp,'rb').read().decode('utf-8-sig'))
h=M['handoffCitationRisk']
print('=== FULL authoritativeCurrentValues (what the reviewer is told to trust) ===')
for e in h['authoritativeCurrentValues']:
    print('  artefact :',e.get('artefact'))
    print('  size     :',e.get('size'))
    print('  sha256   :',e.get('sha256'))
    print('  mtime    :',e.get('mtime'))
    print('  mustContain:'); 
    for m in e.get('mustContain',[]): print('      -',m)
print()
print('=== ACTUAL current payload ===')
p=os.path.join(d,'implementation-payload-TM600-TM601.cpp')
raw=open(p,'rb').read(); u=raw.decode('utf-8-sig'); L=u.split('\r\n')
code=re.sub(r'//.*$','',u,flags=re.M)
print('  %d B / %s @%s'%(len(raw),hashlib.sha256(raw).hexdigest(),time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(os.stat(p).st_mtime))))
print()
print('=== recompute the mustContain quantities on CURRENT bytes ===')
t6=next(i for i,l in enumerate(L) if l.startswith('DUT_API int TM600_HS_RDSON'))
t7=next(i for i,l in enumerate(L) if l.startswith('DUT_API int TM601_LS_RDSON'))
print('  TM600 body: L%d..L%d'%(t6+1,t7))
def cnt(s): return code.count(s)
for k in ['K48_ACM5_AMP_REF','K76_ACM_BST','K109_BUSL1_PB0','K110_ACM18_BST','K46','ERROR_RES','K126_V1P5_CAP','K57_CAP_BST_SW']:
    print('    executable %-20s = %d'%(k,cnt(k)))
print('    SetOn calls = %d'%code.count('cbite.SetOn('))
print('    bare 126 (token) = %d'%len(re.findall(r'(?<![A-Za-z0-9_])126(?![A-Za-z0-9_])',code)))
print('    delay_ms(1) = %d | delay_ms(2) = %d'%(code.count('delay_ms(1)'),code.count('delay_ms(2)')))