import sys,io,os,json
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
base=r'D:\Newtest\DSH\ATE-Coding-Plat'
p=os.path.join(base,'team','artifacts','acceptance-20260916-dali10','acceptance-report.json')
J=json.loads(open(p,'rb').read().decode('utf-8-sig'))
print('=== THEIR DEPTH-BASED CLAIM: currentCanonicalArtifact sits INSIDE coverage[2] and coverage[9] ===')
for i in (2,9):
    c=J['coverage'][i]
    print('  coverage[%d] keys: %s'%(i,list(c.keys())))
    cca=c.get('currentCanonicalArtifact')
    if cca:
        print('     currentCanonicalArtifact = %s'%json.dumps(cca,ensure_ascii=False)[:200])
    print('     artifactSha256 = %s'%str(c.get('artifactSha256'))[:24])
print()
print('=== SO: my earlier "residual" was ALSO shape-based. Was it wrong? ===')
print('  my claim was: marking lives in prose, not beside the field -> a field-only reader gets an unmarked old hash')
for i in (2,9):
    c=J['coverage'][i]
    print('  coverage[%d]: field-level sibling present? %s  -> a reader of coverage[%d] DOES get the canonical'
          %(i, 'currentCanonicalArtifact' in c, i))
print()
print('=== and WHY my window missed it: distance between the field and the name ===')
import re
t=open(p,'rb').read().decode('utf-8-sig',errors='replace')
for m in re.finditer(r'implementation-payload-TM600-TM601\.cpp',t):
    seg=t[m.start():m.start()+1200]
    j=seg.find('currentCanonicalArtifact')
    if j>=0:
        print('  name@%d -> currentCanonicalArtifact at +%d chars (my window was +/-400)'%(m.start(),j))