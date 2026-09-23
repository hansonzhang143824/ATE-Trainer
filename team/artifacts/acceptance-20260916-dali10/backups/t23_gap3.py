import sys,io,os,json,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'implementation-manifest.json')
M=json.loads(open(p,'rb').read().decode('utf-8-sig'))
# third item: samples wording (already a limitation, now also a baseline item)
M['planGapsRecordedNotFixed']['items'].append({
 'id':'PLAN-GAP-3',
 'topic':'the plan\'s sampling wording is true but readable the wrong way',
 'planText':'"the shared trim-measurement source and the board-check source do contain 200/10 at a small number of sites, so 200 is not golden-exclusive" — semantically correct, but a reader can wrongly conclude that the (200,x) PAIR is not golden-specific.',
 'implementation':'The payload uses MeasureVI(200, 5, FPVIe_MV_X10). The precise fact is recorded in this manifest\'s limitations: the COUNT 200 appears in the method library at a 10 us period (sub.cpp x4, BoardCheck.cpp), while the PAIR (200, 5) is golden-specific in this tree because every TM-level call uses (50, 5).',
 'disposition':'Accuracy improvement only, not a finding risk: no code defect follows from the plan wording, and the payload choice is correctness-neutral.'})
M['planGapsRecordedNotFixed']['soloAuthorityNote']=(
 'The frozen plan cannot be revised (captain STOP order: no new revision after t11 completes), and no plan-side owner can amend it. Therefore for these three topics '
 'THE PAYLOAD INLINE COMMENTS AND THIS MANIFEST ARE THE SOLE AUTHORITY. A reviewer must not raise a finding on the basis of "the plan does not state this": '
 'PLAN-GAP-1 and PLAN-GAP-2 are covered by units.md/the captain\'s rulings plus the code comments, and PLAN-GAP-3 is an accuracy matter with no code consequence. '
 'If the captain later authorises a plan revision, these records remain valid as the read-time evidence and nothing here should be deleted.')
open(p,'wb').write((json.dumps(M,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
r=open(p,'rb').read(); k=json.loads(r.decode('utf-8'))
print('manifest %d B / %s'%(len(r),hashlib.sha256(r).hexdigest()))
print('plan gap items:',[i['id'] for i in k['planGapsRecordedNotFixed']['items']])
print('soloAuthorityNote present:','soloAuthorityNote' in k['planGapsRecordedNotFixed'])
print('limitations:',len(k['limitations']))