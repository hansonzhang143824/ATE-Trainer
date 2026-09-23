import sys,io,os,json
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
base=r'D:\Newtest\DSH\ATE-Coding-Plat'
p=os.path.join(base,'team','artifacts','acceptance-20260916-dali10','acceptance-report.json')
J=json.loads(open(p,'rb').read().decode('utf-8-sig'))
cov=J.get('coverage') or []
print('=== THEIR CLAIM: the marker is on 2 of 12 coverage entries, exactly the superseded ones ===')
print('  total coverage entries: %d'%len(cov))
marked=[]
for i,c in enumerate(cov):
    if 'artifactSha256IsHistorical' in c:
        marked.append(i)
        print('  coverage[%d]: artifactSha256=%s  marker=%s'%(i,str(c.get('artifactSha256'))[:20],
              str(c.get('artifactSha256IsHistorical'))[:60]))
print('  entries carrying the marker: %s  (they say 2)'%marked)
print()
print('=== and does every entry with the marker ALSO lack a current hash? ===')
for i in marked:
    c=cov[i]
    print('  coverage[%d] currentCanonicalArtifact = %s'%(i,str((c.get('currentCanonicalArtifact') or {}).get('sha256'))[:24]))
print()
print('=== are there entries with a superseded-looking hash but NO marker? (the real risk test) ===')
import re
cur='66abc088ae6bd5f9b9d7201673003fc0be2450fd6f1f222c6a4a902cbe4f0cc4'
for i,c in enumerate(cov):
    h=c.get('artifactSha256')
    if h and h!=cur and 'artifactSha256IsHistorical' not in c:
        print('  coverage[%d] has non-current hash %s and NO marker  <== would be a real finding'%(i,str(h)[:20]))
print('  (none printed above means: every non-current hash is marked)')