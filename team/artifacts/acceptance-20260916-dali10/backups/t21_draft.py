import sys,io,os,json,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'implementation-manifest.draft.json')
J=json.loads(open(p,'rb').read().decode('utf-8-sig'))
ch=J['changes'][0]
print('before: payload',ch.get('payloadSha256')[:16],ch.get('payloadSize'))
ch['payloadSha256']='c8bf3b3e693673bb92c04fc7c34d8529a1c2a02c785fbaa507f2387956fcd86e'
ch['payloadSize']=28726
ch['afterSha256']='pending-write'
ch['repairNote']=('t21 repaired two relay-trace defects in this payload: (1) the bare relay token 126 was replaced by '
 'K126_V1P5_CAP (StdAfx.h:299) in both functions - the gate reported it as a fabricated name because it matches NAMED '
 'tokens against the defines table; (2) TM601_LS_RDSON now also closes K57_CAP_BST_SW, K44_Cap_SW2_BST2, '
 'K45_Cap_SW1_BST1 and K5_VBUS_Cap, the stabiliser caps required by FR-001 reverse for its statically powered SW and '
 'VBUS rails. Verified with the project gate in a workspace sandbox: RELAY TRACE PASSED with only the two TM643 '
 'warnings that are byte-identical in the pre-change baseline.')
J['newRedTriage']={
 'relay-trace':{'status':'FIXED IN PAYLOAD (not yet on disk)','evidence':'t21-new-red-analysis.md section 3: project gate run against a workspace sandbox copy prints RELAY TRACE PASSED with the four TM601 findings and both fabricated-name errors gone'},
 'TM643_VBAT_LOOP_INDICTOR':{'status':'PRE-EXISTING (out of scope)','evidence':'exists in backups/test.cpp.before_TM600_TM601.bak (3 occurrences) and its body is unchanged; the gate run against the pre-change baseline produces byte-identical warnings; its own SetOn closes neither K57_CAP_BST_SW nor K5_VBUS_Cap'},
 'cbit_K168_K169_K170':{'status':'PRE-EXISTING (set-unchanged KNOWN-RED)','evidence':'the affected file is source/StdAfx.h, which this change does not modify; the same gate on the patched header copy reproduces the identical three errors; the relays (168/169/170) are disjoint from every relay this change adds (<=155); cbit was already the single KNOWN-RED gate in this run baseline'}
}
J['blockingLimitation']=('Steps requiring the workspace to BE the target tree (scripts/run_gates.ps1 and the Release build) could not be '
 'performed from the authoring session: it is scoped to D:/Newtest/DSH/ATE-Coding-Plat and approval is disabled, so the target '
 'tree is not writable and a delegated subagent scope cannot be widened from inside. Consequently gate-logs-t21, the compile report '
 'and the final implementation-manifest.json (which needs the real afterSha256) must be produced by the write-capable executor.')
open(p,'wb').write((json.dumps(J,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
r=open(p,'rb').read()
print('after : draft %d B / %s'%(len(r),hashlib.sha256(r).hexdigest()))
print('valid JSON:',bool(json.loads(r.decode('utf-8'))))
a=os.path.join(d,'t21-new-red-analysis.md'); ra=open(a,'rb').read()
print('analysis %d B / %s'%(len(ra),hashlib.sha256(ra).hexdigest()))