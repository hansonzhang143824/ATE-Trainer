import sys,io,os,json,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'implementation-manifest.json')
before=open(p,'rb').read()
M=json.loads(before.decode('utf-8-sig'))
changed=[]
def setk(path,val):
    cur=M
    for k in path[:-1]: cur=cur[k]
    old=cur.get(path[-1]) if isinstance(cur,dict) else None
    if old!=val:
        cur[path[-1]]=val; changed.append(('.'.join(map(str,path)),str(old)[:50],str(val)[:50]))

# ---- planGapsRecordedNotFixed: resolved in-plan by v21/t27, entries retained ----
g=M['planGapsRecordedNotFixed']
g['statusUpdate']=('RESOLVED IN-PLAN BY t27/v21. The freeze was lifted within the t27 scope and the three items are now written into test-plan.json '
 'itself, so the plan - not this manifest - is the authority for them. Verified against the live plan (v21): the ambiguous "floating channel last" '
 'wording has 0 occurrences and cleanup[0] / the high-current orderedStep 7 now name the MEASUREMENT channel (floating channel 0, the R-VIR pair) '
 'as released last; parameters.initializationRange is present for both high-current items (1 V + 10 uA, minimal compliant step, cited to '
 'units.md:3-5); and measurement.samples.evidence distinguishes the count 200 (method library, 10 us period) from the golden-specific (200, 5) pair. '
 'Every entry is RETAINED below as the record of what was reported and which evidence was used while the plan was frozen - nothing is deleted, per '
 'the run rule that traces are kept.')
disp={
 'PLAN-GAP-1':'resolved in-plan by t27/v21: the teardown wording is disambiguated in items[*].cleanup[0] and in the high-current orderedSteps step 7, naming the MEASUREMENT channel (floating channel 0, the R-VIR pair) as released last and the bootstrap source channel first. The implementation already did this; plan and payload now agree.',
 'PLAN-GAP-2':'resolved in-plan by t27/v21: parameters.initializationRange is now stated for both high-current items (1 V range with the 10 uA current range, the minimal compliant step), citing units.md:3-5, the unified off-range reuse and the 1 A point keeping the 2 A range. The plan gap this manifest recorded is closed.',
 'PLAN-GAP-3':'resolved in-plan by t27/v21: measurement.samples.evidence now states that count 200 appears in the method library at a 10 us period while the (200, 5) PAIR is golden-specific in this tree because every TM-level call uses (50, 5). Accuracy item; no code consequence.'}
for it in g.get('items',[]):
    if it.get('id') in disp: it['disposition']=disp[it['id']]
setk(['planGapsRecordedNotFixed'],g)
g2=M['planGapsRecordedNotFixed']
setk(['planGapsRecordedNotFixed','soloAuthorityNote'],('SUPERSEDED BY t27/v21. The earlier assertion that the plan could not be revised, and that the payload comments were '
 'therefore the sole authority, no longer holds: the freeze was lifted inside the t27 scope and the plan now records all three items. Plan text and '
 'implementation evidence are MUTUAL CORROBORATION. Nothing in this section is deleted.'))
setk(['planGapsRecordedNotFixed','retentionNote'],'All three entries and their evidence are retained verbatim as history, per the run rule that reported findings and their evidence are never removed.')

# ---- t28 gate/compile evidence references ----
M['gateAndGenerationEvidence']={
 'sourceTask':'t28',
 'artefacts':[
  {'path':'team/artifacts/acceptance-20260916-dali10/gate-logs-t28/t28-red-proof.json','size':5351,'sha256':'b97441a457119ca0'+''},
  {'path':'team/artifacts/acceptance-20260916-dali10/gate-logs-t28/t28-summary.md','size':12444,'sha256':'917fed02acca7d27'+''}],
 'generationReplayRequirement':('Reported by t28 and recorded here as THEIR finding, not as a verified conclusion by this author: the meta-generation '
  'baseline read was tampered such that a replay appeared IN SYNC. t28 provides a red proof - the same check run through a restored (correct) reader '
  'gives a different verdict than the tampered path.'),
 'redProof':{
  'beforeFix':{'script':'gate-logs-t28/backups/check_input_sync.py','scriptSha256':'d8722d9123827d55bc7af95b2fdf503f9689d5113ca7ace8fac618b75903d467',
    'exitCode':0,'verdict':'IN SYNC','log':'gate-logs-t28/redproof-before-fix.log','logSha256':'c0bfc972d34b44915165f7d893f19d8a6f9fe9c8ce641d8c20ed168d17327786'},
  'afterFix':{'script':'scripts/check_input_sync.py','scriptSha256':'e804c459b2d3088e72d455eb9e1b7893119cea47ad0a640735b6f5db42d784d1',
    'exitCode':1,'verdict':'OUT OF SYNC','log':'gate-logs-t28/redproof-after-fix.log','logSha256':'6a17726003afaa6e6470c20e7e94ea18477e96c6590d76ad906e1970c3aae7e2'},
  'redProofPassed':True,
  'authoritativeVerdict':'OUT OF SYNC (exit 1) is the TRUE state; the tampered-path IN SYNC (exit 0) was a false green.'},
 'status':'reported by t28; this manifest records the reference and both hashes, and does NOT assert gate success on the strength of it.'}

# ---- t33 / build report ----
M['buildReport']={'path':'team/artifacts/acceptance-20260916-dali10/build-report.json','status':'PENDING t33',
 'note':('t33 has not produced build-report.json yet (measured: the file does not exist in the run directory). This field is deliberately left as a '
  'placeholder rather than populated from older logs, so that no un-reviewed gate or compile output is presented as a verified result. When t33 lands, '
  'its path and hash are to be written here.')}

# ---- review status ----
M['reviewStatus']={
 't24':{'verdictRecorded':'ACCEPT','status':'PARTIALLY WITHDRAWN by the reviewing party',
   'reason':('The BST closure set (K109/K110) is NOT inside t24 coverage, so t24 ACCEPT must not be read as clearing it. The defect was raised '
    'separately and is the subject of t29. The manifest must therefore not imply that everything was fully passed.')},
 't29':{'status':'AWAITING rule-reviewer verdict','note':'t29 content is complete (payload + evidence + gates re-run on a sandbox copy with 0 new red); the independent four-point review has not yet been returned.'},
 'statement':'No claim of full review closure is made. t24 coverage is partial and t29 review is outstanding.'}
setk(['status'],('APPLIED (previous revision) + t29 PENDING LANDING. The tree holds the t23 revision of the TM600/TM601 region. The t29 repair '
 '(K109/K110 BST excitation path) is content-complete and independently reviewable but NOT yet written. Gate and compilation conclusions await t33; '
 'no verified gate or compile result is claimed here.'))
open(p,'wb').write((json.dumps(M,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
after=open(p,'rb').read()
print('manifest %d B -> %d B'%(len(before),len(after)))
print('sha256 %s'%hashlib.sha256(after).hexdigest())
print('changed keys:'); [print('  ',k) for k,_,_ in changed]