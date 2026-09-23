import sys,io,os,json,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'implementation-manifest.json')
M=json.loads(open(p,'rb').read().decode('utf-8-sig'))
M['resolvedSinceEscalation']=[
 {'topic':'BST-SW resource arbitration (plan text vs ruling (ii))',
  'escalatedAs':'I reported a decision-level conflict: the live plan then stated the ch1 (floating channel 1) baseline as DECIDED, which contradicted the captain\'s ruling (ii) and the plan\'s own negative-list logic.',
  'nowResolved':'RESOLVED IN THE PLAN. The live test-plan.json revision v20 (the captain\'s t17 closure) now reads: "Resource arbitration — DECIDED (ruling (ii), captain; supersedes the earlier floating-channel-1 baseline): the bootstrap-to-switched rail is driven by the GROUND-REFERENCED ACM200 pair SW12_U1REF_BST_ACM (closed set [110,61] = K110_ACM18_BST / K61_ACM8_SW), and the floating-channel-1 route is recorded as INTENDED BUT CURRENTLY UNREALISABLE", with the same evidence I gave (no minimal ch1 endpoint macro; only composite K_FPVIH_TO_BST_B = 131,132,134,135; those relays are ch1 sense-float/local-sense/PC-route, the class the negative list forbids actuating; StdAfx.h:303-309).',
  'payloadConsequence':'NONE — the payload already implemented ruling (ii) and did not change. Verified live: the BST rail is driven by SW12_U1REF_BST_ACM, FPVI1 appears only in the teardown RELAY_OFF, and K131/K132/K134/K135 appear nowhere in executable code.',
  'evidenceAtReferenceTime':'test-plan.json 166099 B / 1925250df53f8b52126fdda9efa84ae84fe2bc8e529867e0965fc0ffe9a08016, revision "v20 (t17 closure - BST-SW ruling (ii) + idempotent generatedAt)". I verified the quoted passage myself rather than relying on the relay.'}]
open(p,'wb').write((json.dumps(M,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
r=open(p,'rb').read()
print('manifest %d B / %s'%(len(r),hashlib.sha256(r).hexdigest()))
print('resolvedSinceEscalation present:','resolvedSinceEscalation' in json.loads(r.decode('utf-8')))