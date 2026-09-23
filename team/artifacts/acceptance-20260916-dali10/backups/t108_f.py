import sys,io,os,json,re
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
base=r'D:\Newtest\DSH\ATE-Coding-Plat'
p=os.path.join(base,'team','artifacts','acceptance-20260916-dali10','acceptance-report.json')
J=json.loads(open(p,'rb').read().decode('utf-8-sig'))
print('=== ALL coverage entries naming the payload, with their hash and status ===')
for i,c in enumerate(J.get('coverage') or []):
    if isinstance(c,dict) and 'implementation-payload' in str(c.get('artifact','')):
        h=str(c.get('artifactSha256',''))[:20]
        print('  coverage[%d] status=%-8s hash=%s'%(i,c.get('status'),h))
print()
print('=== the marking field for the superseded hash ===')
s=json.dumps(J,ensure_ascii=False)
for key in ['artifactSha256Note','sha256Note','revisionNote','supersededNote']:
    i=s.find('"'+key+'"')
    if i>0:
        print('  %s -> ...%s...'%(key,s[i:i+230]))
print()
print('=== and the currentCanonicalArtifact block, in full ===')
i=s.find('"currentCanonicalArtifact"')
print('  ',s[i:i+300])