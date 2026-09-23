import sys,io,os,json
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
base=r'D:\Newtest\DSH\ATE-Coding-Plat'
p=os.path.join(base,'team','artifacts','acceptance-20260916-dali10','acceptance-report.json')
J=json.loads(open(p,'rb').read().decode('utf-8-sig'))
print('=== does the report carry a CURRENT-CANONICAL pointer? ===')
for k,v in J.items():
    if 'canonical' in k.lower() or 'current' in k.lower():
        print('  %s = %s'%(k,json.dumps(v,ensure_ascii=False)[:300]))
print()
print('=== the coverage entries that name the payload: record index, status, hash ===')
for i,c in enumerate(J.get('coverage') or []):
    if isinstance(c,dict) and 'implementation-payload' in str(c.get('artifact','')):
        h=str(c.get('artifactSha256',''))[:24]
        tag='CURRENT' if h.startswith('66abc088') else 'SUPERSEDED'
        print('  coverage[%d] status=%-8s hash=%s  %s'%(i,c.get('status'),h,tag))
print()
print('=== is 2d0984d9 referenced by any superseded-marking field? ===')
s=json.dumps(J,ensure_ascii=False)
print('  "superseded" occurrences:',s.lower().count('superseded'))
print('  "currentCanonicalArtifact" present:', 'currentCanonicalArtifact' in s)
i=s.find('currentCanonicalArtifact')
if i>0: print('  ...%s...'%s[i-120:i+260])