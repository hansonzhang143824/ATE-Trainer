import sys,io,os,json,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
src=os.path.join(d,'implementation-manifest.draft.json')
dst=os.path.join(d,'implementation-manifest.json')
J=json.loads(open(src,'rb').read().decode('utf-8-sig'))
# make the PENDING state explicit and machine-visible at the top level
J['status']='PENDING-WRITE — created by ate-implementer (content author) before the target-tree write; the only unavailable value is the post-write afterSha256'
J['writeStateNote']=('This manifest is complete and schema-valid EXCEPT for the post-write re-read hash. The target tree is NOT yet written '
 'by this delivery: D:/PROJECT6-DALI/ForCodexDebug/source/test.cpp is still at the t20 appended state '
 '(462848 B / 3dbceb496d79d7d08631713b98e46c0c2ba6163eaf5356a87dded677e35ba479), which carries an OLDER TM601 relay list '
 '(bare 126, no stabiliser caps). The executor must replace that region with this payload, then set changes[0].afterSha256 to the '
 'post-write re-read hash and set the gate/compile selfChecks exitCodes to the real observed values before this manifest is final.')
J['changes'][0]['afterSha256']='pending-write — must be replaced with the post-write re-read sha256'
J['changes'][0]['afterSha256IsPending']=True
J['authoredBy']['executor']=('pending-write — the write-capable party (Captain). The report must credit content author = ate-implementer '
 'and executor = the write-capable party; the content must not be attributed to the executor nor the execution to the author.')
open(dst,'wb').write((json.dumps(J,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
r=open(dst,'rb').read()
print('implementation-manifest.json %d B / %s'%(len(r),hashlib.sha256(r).hexdigest()))
print('valid JSON:',bool(json.loads(r.decode('utf-8'))))
print('status:',J['status'][:80])
print('changes[0].afterSha256:',J['changes'][0]['afterSha256'][:60])
print('payload:',J['changes'][0]['payloadSha256'][:16],J['changes'][0]['payloadSize'])
print('before :',J['changes'][0]['beforeSha256'][:16])
print('limitations:',len(J['limitations']),'| selfChecks exitCodes:',[sc['exitCode'] for sc in J['selfChecks']])