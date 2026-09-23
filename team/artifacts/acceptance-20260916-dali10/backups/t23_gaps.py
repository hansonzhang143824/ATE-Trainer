import sys,io,os,json,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'implementation-manifest.json')
M=json.loads(open(p,'rb').read().decode('utf-8-sig'))
M['planGapsRecordedNotFixed']={
 'purpose':('Two items where the FROZEN test plan is silent or ambiguous. They are recorded here so a downstream reviewer can see '
   'the evidence and disposition instead of raising them as implementation findings. The plan has NOT been edited: the captain froze it, '
   'and t17-completed-plus-a-new-revision would count as incomplete. Both claims below were independently reproduced by the author.'),
 'items':[
  {'id':'PLAN-GAP-1','topic':'teardown release order is ambiguous with two floating channels',
   'planText':"cleanup[0] '…unified RELAY_OFF, rails bled to AGND, then the floating instrument released last' and orderedSteps step 7 '…floating channel last' — with FPVIe0 and FPVIe1 both in play it is not stated WHICH is 'the floating channel'.",
   'implementation':'TM600 order VBAT, V1P5, PMID, SW12, FPVI1, FPVI0 — the BST-SW loop channel (FPVI1) releases first and the MEASUREMENT channel (FPVI0) releases last. TM601 order VBAT, V1P5, PMID, SW12, FPVI0 — FPVI0 last.',
   'assessment':'The strict reading of "floating instrument released last" applied to the measurement channel. Independently reproduced from the payload code by extracting every RELAY_OFF statement in file order.',
   'disposition':'Implementation already conforms; recorded as a plan wording ambiguity so it is not raised as a finding.'},
  {'id':'PLAN-GAP-2','topic':'plan specifies no initialization range for the zero-value power-on state',
   'planText':'The frozen plan contains NO initialization-range statement: searches for "10UA", "FPVIe_10UA", "minimal compliant" and "initialization range" return 0 occurrences. The golden precedent that does exist uses FPVIe_2A at the same step.',
   'implementation':'Both 0 V / 0 A power-on inits use FPVIe_1V / FPVIe_10UA.',
   'basis':('units.md:3-5 requires range >= 2x the set value and the nearest-to-2x SMALLEST step; a 0 V/0 A initialization has no 2x requirement, so the minimal compliant step applies. '
     'FPVIe_10UA is also the unified off-range current side that R-POFF-06 prescribes. The 1 A force point keeps FPVIe_2A, so reusing 2 A for a zero initialization would repeat a different error. '
     'Recorded in the payload as an inline comment and ruled acceptable by the captain.'),
   'disposition':'Author-chosen, documented and defensible; the gap is on the plan side. Recorded so it is not raised as an unsupported deviation.'}]
}
open(p,'wb').write((json.dumps(M,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
r=open(p,'rb').read()
print('manifest %d B / %s'%(len(r),hashlib.sha256(r).hexdigest()))
print('planGapsRecordedNotFixed present:','planGapsRecordedNotFixed' in M,'| items:',len(M['planGapsRecordedNotFixed']['items']))