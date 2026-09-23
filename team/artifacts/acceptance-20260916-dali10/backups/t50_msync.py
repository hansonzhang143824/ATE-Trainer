import sys,io,os,re,json,hashlib,time
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
base=r'D:\Newtest\DSH\ATE-Coding-Plat'
d=os.path.join(base,'team','artifacts','acceptance-20260916-dali10')
P=os.path.join(d,'implementation-payload-TM600-TM601.cpp')
r=open(P,'rb').read(); h=hashlib.sha256(r).hexdigest()
u=r.decode('utf-8-sig'); code=re.sub(r'//.*$','',u,flags=re.M)
C=json.loads(open(os.path.join(d,'setup-contract.json'),'rb').read().decode('utf-8-sig'))
cstat=open(os.path.join(d,'review','t43-t42-review-and-unknown-ruling.md'),'rb').read() if os.path.exists(os.path.join(d,'review','t43-t42-review-and-unknown-ruling.md')) else b''
mp=os.path.join(d,'implementation-manifest.json')
M=json.loads(open(mp,'rb').read().decode('utf-8-sig'))
lg=M['handoffCitationRisk']['landingGate']
lg['status']=('BLOCKED - bst-sw is RED on the current bytes. t39/t40/t42/t43/t44 are all complete and the captain has authorised a batch, '
 'but this payload does NOT pass the gate set, so it must NOT be treated as electrically correct or cleared to land.')
lg['gates']=['LANDING BLOCKED on bst-sw: the contract on disk (revision %s) still lists relay 110 for TM600 in '
 'aliasResolution[3].closedRelayNumbers, which is the criterion verify_bst_sw_sequence.py declares it uses, while the payload no longer '
 'closes K110 (the captain authorised its removal). relay-trace PASS exit 0; awg PASS exit 0; bst-sw FAIL exit 1.'%str(C.get('revision'))]
lg['gateHistoryNote']=('Gate history, retained: t39+t40 -> t40+t42 -> t43 -> CLOSED(batch) -> BLOCKED on bst-sw. That is five wordings during one '
 'run, which is why this field exists, why artefacts are cited by content key and role rather than by hash, and why the current state is stated '
 'as RED rather than closed.')
lg['contractRevisionSeen']='setup-contract.json revision %s; aliasResolution[3].closedRelayNumbers = [110, 61] with usedByTm including TM600'%str(C.get('revision'))
lg['whyT42Matters']=('SUPERSEDED by events, retained for history: t42 concluded ch5 (implying [48,76]); t43 then ruled ch5-vs-ch18 UNKNOWN(c) and '
 'prescribed the union; the captain then relied on production behaviour to authorise REMOVING K109/K110 outright. The ch5 reading is now the '
 'operative one, and the payload closes K48/K76 only.')
lg['tm600ExposureOpen']=('RESOLVED in the payload: TM600 now closes the ch5 leg (K48_ACM5_AMP_REF + K76_ACM_BST, 1 each) and no longer closes '
 'K109/K110 (0 each). The remaining exposure is NOT in the payload but in the CONTRACT: rev %s still demands 110, so bst-sw reds.'%str(C.get('revision')))
lg['verifiedCounts']={
 'payloadSha256':h,'payloadSize':len(r),
 'executableK48_ACM5_AMP_REF':code.count('K48_ACM5_AMP_REF'),
 'executableK76_ACM_BST':code.count('K76_ACM_BST'),
 'executableK109_BUSL1_PB0':code.count('K109_BUSL1_PB0'),
 'executableK110_ACM18_BST':code.count('K110_ACM18_BST'),
 'executableK46':code.count('K46'),
 'executableERROR_RES':code.count('ERROR_RES'),
 'executableDelayMs1':code.count('delay_ms(1)'),
 'executableDelayMs2':code.count('delay_ms(2)'),
 'executableSetClamp':code.count('SetClamp(50, 50)'),
 'executableMeasureVI':code.count('MeasureVI(200, 5, FPVIe_MV_X10)'),
 'verifiedAt':time.strftime('%Y-%m-%dT%H:%M:%S%z'),
 'note':('SUPERSEDED the previous value (which read 6034af71... with K109/K110 = 1 each, i.e. the union state). Current: ch5 leg closed, '
  'K109/K110 removed. A receipt quoting the union counts describes the 38,147/39,457/40,658/41,797 revisions, not this one.')}
open(mp,'wb').write((json.dumps(M,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
r2=open(mp,'rb').read()
print('manifest %d B / %s'%(len(r2),hashlib.sha256(r2).hexdigest()))
J=json.loads(r2.decode('utf-8'))
vc=J['handoffCitationRisk']['landingGate']['verifiedCounts']
print('  payloadSha256 now:',vc['payloadSha256'][:16],'| K48/K76/K109/K110/K46:',vc['executableK48_ACM5_AMP_REF'],vc['executableK76_ACM_BST'],vc['executableK109_BUSL1_PB0'],vc['executableK110_ACM18_BST'],vc['executableK46'])
print('  status starts BLOCKED:',J['handoffCitationRisk']['landingGate']['status'].startswith('BLOCKED'))
print('  contractRevisionSeen:',J['handoffCitationRisk']['landingGate']['contractRevisionSeen'])