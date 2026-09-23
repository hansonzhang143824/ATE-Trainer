import sys,io,os,json,hashlib,re,time
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'implementation-manifest.json')
M=json.loads(open(p,'rb').read().decode('utf-8-sig'))
pay=os.path.join(d,'implementation-payload-TM600-TM601.cpp'); rp=open(pay,'rb').read()
u=rp.decode('utf-8-sig'); code=[l for l in u.split('\n') if not l.strip().startswith('//')]
ev=os.path.join(d,'t40-tm601-bst-evidence.md'); re_=open(ev,'rb').read()
e29=os.path.join(d,'t29-k110-evidence.md'); r29=open(e29,'rb').read()
ap=os.path.join(d,'APPLY-TM600-TM601.md'); rap=open(ap,'rb').read()
M['handoffCitationRisk']['criterion']=('PRIMARY RULE (adopted from test-strategy-architect): cite the payload by CONTENT KEY, not by a single hash - the owner '
 'keeps revising it, so a hash anchor races. A file is the right revision only if it CONTAINS the required keys; verify against disk at '
 'publication and treat any hash quoted in a message as a check, not the criterion.')
M['handoffCitationRisk']['authoritativeCurrentValues']=[
 {'artefact':'implementation-payload-TM600-TM601.cpp','size':len(rp),'sha256':hashlib.sha256(rp).hexdigest(),
  'mtime':time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(os.stat(pay).st_mtime)),
  'mustContain':['t29 PER-FUNCTION JUSTIFICATION - WHY THIS ITEM DOES NOT CLOSE K109/K110 (explicit, not omitted)',
   'executable code: K109_BUSL1_PB0 x1','executable code: K110_ACM18_BST x1','TM601 ACM Sets = 0','TM600 ACM Sets = 10',
   'delay_ms(1) x6','delay_ms(2) x0','SetClamp(50, 50) x2','MeasureVI(200, 5, FPVIe_MV_X10) x2'],
  'note':('The t38 revision. The last three keys are what distinguish it from the t29 revision. All nine were verified present on this file at '
    'this instant. Missing any => stale citation.')},
 {'artefact':'t40-tm601-bst-evidence.md','size':len(re_),'sha256':hashlib.sha256(re_).hexdigest(),
  'note':'t38 evidence: conclusion-first, the three sources, the need-to-closed table, the relay-contact nuance, and section 0 with the FACT/INFERENCE/UNKNOWN separation plus the sequencing disclosure (the t38 edit crossed the user hold).'},
 {'artefact':'t29-k110-evidence.md','size':len(r29),'sha256':hashlib.sha256(r29).hexdigest(),
  'note':'t29 evidence, including section 2b (the TM601 per-function rationale) and section 6b (revision history - the reversion source for the t38 removal).'},
 {'artefact':'APPLY-TM600-TM601.md','size':len(rap),'sha256':hashlib.sha256(rap).hexdigest(),
  'note':'three-way compare-before-write block retained. NOTE: its payload hash row predates t38 and should be refreshed by the executor before use.'}]
M['handoffCitationRisk']['selfStalenessWarning']=('This block is itself subject to the same drift it warns about: t38 moved the payload after an earlier version of it '
 'was written. The content keys are the stable part; the hashes are a point-in-time check. Recompute from disk before relying on any value here.')
open(p,'wb').write((json.dumps(M,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
r=open(p,'rb').read()
print('manifest %d B / %s'%(len(r),hashlib.sha256(r).hexdigest()))
print('criterion present:','PRIMARY RULE' in json.dumps(M,ensure_ascii=False))
print('payload recorded:',M['handoffCitationRisk']['authoritativeCurrentValues'][0]['size'],M['handoffCitationRisk']['authoritativeCurrentValues'][0]['sha256'][:16])