import sys,io,os,json,hashlib,time
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
mp=os.path.join(d,'implementation-manifest.json')
before=open(mp,'rb').read()
M=json.loads(before.decode('utf-8-sig'))
lg=M['handoffCitationRisk']['landingGate']

lg['status']=('GATES PASS (bst-sw GREEN on the frozen payload under contract rev 29) - NOT cleared to land: '
 'target tree not yet updated.')
lg['gates']=('relay-trace PASS exit 0 / bst-sw PASS exit 0 (missing=[]) / awg PASS exit 0 - all three run on a SANDBOX COPY '
 '(gate-check-t21/source/test.cpp, built by substituting this payload\'s TM600..TM601 region into the deployed tree), under '
 'setup-contract.json = 355,658 B / 4a45f7345be4e5862a145851943a31d540dc906613c5f8094cc375bb3be3e170 (revision 29). '
 'bst-sw expectation [48,60,61,76,83] with missing=[] for TM600 and [60,61,154,155] missing=[] for TM601.')
lg['contractRevisionSeen']=('setup-contract.json revision 29 = 355,658 B / 4a45f7345be4e5862a145851943a31d540dc906613c5f8094cc375bb3be3e170; '
 'aliasResolution[3].closedRelayNumbers = [48, 60, 61, 76] (ch5), relayChain corrected to the ch5 pair with the ch18 text preserved '
 'under relayChainSuperseded. The earlier [110, 61] value was the value at revisions 25-28 and is what reddened bst-sw there.')
lg['gateHistoryNote']=('Gate history, retained: t39+t40 -> t40+t42 -> t43 -> CLOSED(batch) -> BLOCKED on bst-sw (rev 25-28, always '
 'missing=[110]) -> GREEN after t53 corrected the DECISION field to ch5 (rev 29). Six wordings during one run. The lesson the field '
 'change confirms: the payload was never the obstacle to that gate; the contract\'s decision field was, which is why option (1) was '
 'taken over rolling the payload back.')
lg['whyT42Matters']=('SUPERSEDED by events, retained for history: t42 concluded ch5 (implying [48,76]); t43 then ruled ch5-vs-ch18 '
 'UNKNOWN(c) and prescribed the union; the captain relied on production behaviour to authorise REMOVING K109/K110; t53 then corrected '
 'the contract decision field to the ch5 set. The ch5 reading is now BOTH the operative reading and the contract\'s declared value.')
lg['tm600ExposureOpen']=('CLOSED. The payload closes the ch5 leg (K48_ACM5_AMP_REF + K76_ACM_BST, 1 each), closes no K109/K110 (0 each), '
 'and the contract now declares the same required-on set, so bst-sw passes. Not an electrical conclusion: the gate compares a '
 'required-on SET, it does not verify that the source reaches BST on hardware.')
lg['verifiedCounts']={
 'payloadSha256':'66abc088ae6bd5f9b9d7201673003fc0be2450fd6f1f222c6a4a902cbe4f0cc4','payloadSize':43806,
 'executableK48_ACM5_AMP_REF':1,'executableK76_ACM_BST':1,
 'executableK109_BUSL1_PB0':0,'executableK110_ACM18_BST':0,'executableK46':0,
 'executableERROR_RES':2,'executableDelayMs1':6,'executableDelayMs2':0,
 'executableSetClamp':2,'executableMeasureVI':2,
 'verifiedAt':time.strftime('%Y-%m-%dT%H:%M:%S%z'),
 'note':('FROZEN value (captain stop-writing order). K48/K76 = 1 each, K109/K110 = 0, K46 = 0: the ch5 single route. '
  'Any receipt quoting K109/K110 = 1 describes the union revisions (39,457 / 41,797 / 42,998 B), not this one.')}
lg['noSelfApproval']=('The author of this payload does not certify it; independent review of 66abc088... and the captain\'s REPLACE '
 'are outstanding. Gate PASS is not electrical sign-off.')
open(mp,'wb').write((json.dumps(M,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
after=open(mp,'rb').read()
print('manifest %d B -> %d B / %s'%(len(before),len(after),hashlib.sha256(after).hexdigest()))
J=json.loads(after.decode('utf-8'))
g=J['handoffCitationRisk']['landingGate']
print('  status:',g['status'])
print('  contractRevisionSeen starts:',g['contractRevisionSeen'][:60])
print('  payloadSha256:',g['verifiedCounts']['payloadSha256'][:16])
# confirm the payload was NOT touched by this edit
pi=os.path.join(d,'implementation-payload-TM600-TM601.cpp'); pr=open(pi,'rb').read()
print()
print('  payload after edit: %d B / %s'%(len(pr),hashlib.sha256(pr).hexdigest()))
print('  payload still frozen (66abc088):',hashlib.sha256(pr).hexdigest()=='66abc088ae6bd5f9b9d7201673003fc0be2450fd6f1f222c6a4a902cbe4f0cc4')