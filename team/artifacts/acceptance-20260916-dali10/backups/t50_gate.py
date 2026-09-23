import sys,io,os,json,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'implementation-manifest.json')
M=json.loads(open(p,'rb').read().decode('utf-8-sig'))
lg=M['handoffCitationRisk']['landingGate']
lg['status']=('GATE CLOSED - t39/t40/t42/t43/t44 all complete; landing is now governed by the batch t49 + t50 + t51 and their '
 'independent review; the payload must still NOT be treated as electrically correct or cleared to land.')
lg['gates']=['CLOSED - batch t49 (contract rev 25, additive-only), t50 (payload intersection fix), t51 (plan v22, additive-only)']
lg['completed']=['t39 (contract owner)','t40 (rule-reviewer, final 37430005...)','t42 (schematic-expert, PASS)','t44 (supplement)',
 't43 (rule-reviewer independent review + ruling: review/t43-t42-review-and-unknown-ruling.md = 7,439 B / d4c3835437a41c9f1bee7b15c2d381da69c99ceacd0503f5f6dbb0f1023e90a7 - ruled ch5-vs-ch18 UNKNOWN(c) and prescribed the union fix)']
lg['gateHistoryNote']=('Gate history, retained: t39+t40 -> t40+t42 -> t43 -> CLOSED. That is four wordings during one run, which is why '
 'this field exists and why the artefacts are cited by content key and role rather than by hash.')
lg['t43RulingApplied']=('The payload implements the t43 §4 minimal safe fix: the UNION of the ch5 BST branch (K48_ACM5_AMP_REF + K76_ACM_BST) '
 'and the contract-literal branch (K109/K110/K61), in ONE SetOn call. The ruling records that neither branch alone is safe - omitting '
 'K48/K76 leaves BST unreachable if ch5 is right, and deleting K110 breaks the chain if ch18 is right - and that the union is safe under '
 'both because both branches arrive on the same BST net. Side effect registered: --check-extra MUST NOT be enabled for this revision, '
 'since the union deliberately over-closes; that limitation is annotated in the payload comment as t43 requires.')
lg['tm600ExposureOpen']=('CLOSED by t43 as far as it can be documentarily: ch5-vs-ch18 is now formally UNKNOWN(c) rather than an open defect '
 'attribution, and the union fix removes the dependence on which reading is correct. Whether TM600 must be ch5-driven remains for the '
 'contract owner or bench evidence - it is no longer a blocking defect in this payload.')
lg['noSelfApproval']='The author of this payload does not certify it; independent review of 6034af71... and the captain\'s REPLACE are outstanding.'
vw=lg['verifiedCounts']
u=open(os.path.join(d,'implementation-payload-TM600-TM601.cpp'),'rb').read().decode('utf-8-sig')
import re as _re
code=_re.sub(r'//.*$','',u,flags=_re.M)
vw.update({'payloadSha256':hashlib.sha256(open(os.path.join(d,'implementation-payload-TM600-TM601.cpp'),'rb').read()).hexdigest(),
 'payloadSize':os.path.getsize(os.path.join(d,'implementation-payload-TM600-TM601.cpp')),
 'executableK48':code.count('K48_ACM5_AMP_REF'),'executableK76':code.count('K76_ACM_BST'),'executableK46':code.count('K46'),
 'note':'K48/K76 = 1 each and K46 = 0: this revision implements the t43 union fix inside a single SetOn call.'})
open(p,'wb').write((json.dumps(M,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
r=open(p,'rb').read(); J=json.loads(r.decode('utf-8'))
print('manifest %d B / %s'%(len(r),hashlib.sha256(r).hexdigest()))
print('  landingGate.status:',J['handoffCitationRisk']['landingGate']['status'][:80])
print('  GATE CLOSED present:', 'GATE CLOSED' in r.decode('utf-8'))