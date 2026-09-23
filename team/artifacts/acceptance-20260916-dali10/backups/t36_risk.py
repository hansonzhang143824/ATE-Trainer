import sys,io,os,json,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'implementation-manifest.json')
M=json.loads(open(p,'rb').read().decode('utf-8-sig'))
M['handoffCitationRisk']={
 'issue':('Superseded payload/evidence hashes are still circulating in teammate handoffs. Recorded here so that a reviewer opening '
   'the payload by hash is not misled, and so the correct values are stated in the artefact-of-record.'),
 'authoritativeCurrentValues':[
  {'artefact':'implementation-payload-TM600-TM601.cpp','size':38147,
   'sha256':'272667f3f79393b6b1365237c7ac01bed7a527d2984d53d1d5ae6804515057c0',
   'note':'the t29 final revision: adds K109/K110 AND the captain-mandated TM601 per-function justification plus the mechanism/locator comment (+1766 B over the earlier 36381 B build). Contains "PER-FUNCTION JUSTIFICATION".'},
  {'artefact':'t29-k110-evidence.md','size':13978,
   'sha256':'b8e400ca14f37ff9c355c692e0c52562ae4efef96fc6296532dc40588f1d948e',
   'note':'carries section 2b (per-function justification + the three minimal-endpoint proofs), section 6b (revision history) and section 8 (deployed-tree state), plus the locator-substitution note.'},
  {'artefact':'APPLY-TM600-TM601.md','size':7110,
   'sha256':'429ad881d67d3feb6886ca5006dbf663cf025a91025545d988f8cdc446f6dfa1'}],
 'supersededValuesSeenInHandoffs':[
  {'value':'implementation-payload-TM600-TM601.cpp = 36381 B / 73b511b775beda61cc91ea41fdc5358e53579fb4e32cc553bf47792667fea19e',
   'status':'SUPERSEDED by the t29 addendum revision','risk':('A reviewer handed this hash opens a payload WITHOUT the per-function justification and could conclude the mandated item was never produced — a false finding traceable only to the citation.'),
   'disposition':'Corrected with test-strategy-architect; still appears in their notes as of the latest exchange, and they report alignment, so the discrepancy is recorded here rather than re-litigated.'},
  {'value':'t29-k110-evidence.md = 10062 B / 1069e025 (and a later citation 1069e025…)','status':'SUPERSEDED','disposition':'same as above'}],
 'instructionToReviewer':('Verify the deliverable against the values in authoritativeCurrentValues, not against any hash quoted in a message. '
   'If a quoted hash is not one of these, treat the message as stale for that field and recompute from disk.')}
open(p,'wb').write((json.dumps(M,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
r=open(p,'rb').read()
print('manifest %d B / %s'%(len(r),hashlib.sha256(r).hexdigest()))
print('valid JSON:',bool(json.loads(r.decode('utf-8'))))