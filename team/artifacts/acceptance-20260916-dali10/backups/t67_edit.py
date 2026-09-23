import sys,io,os,json,hashlib,time
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
mp=os.path.join(d,'implementation-manifest.json')
before=open(mp,'rb').read()
M=json.loads(before.decode('utf-8-sig'))
C=json.loads(open(os.path.join(d,'setup-contract.json'),'rb').read().decode('utf-8-sig'))
lg=M['handoffCitationRisk']['landingGate']
lg['gates']=('relay-trace PASS exit 0 / bst-sw PASS exit 0 (missing=[]) / awg PASS exit 0 - all three run on a SANDBOX COPY '
 '(gate-check-t21/source/test.cpp, built by substituting this payload\'s TM600..TM601 region into the deployed tree). '
 'Verified at contract revisions 29, 33, 37 and 39 - four independent runs - so the green is stable across the contract being '
 'rebuilt repeatedly, which is the condition that produced the earlier red. Cite the contract by the VALUE the gate consumes, '
 '(aliasResolution[3].closedRelayNumbers = [48, 60, 61, 76]), or by a revision RANGE (>= 29) - not by a revision number or a '
 'file size, both of which move every few minutes.')
lg['contractRevisionSeen']=('setup-contract.json revision %s at the latest re-run; aliasResolution[3].closedRelayNumbers = [48, 60, 61, 76] '
 '(ch5), with [110, 61] demoted into closedRelayNumbersSuperseded. That field is the gate criterion; the route enumerations and the '
 'relaySet pool are locators only. The earlier [110, 61] live value is what reddened bst-sw at revisions 25-28. NOTE: '
 'the contract has been rebuilt many times during this run, so the criterion to quote is the VALUE, not a revision number.'%str(C.get('revision')))
open(mp,'wb').write((json.dumps(M,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
after=open(mp,'rb').read()
print('manifest %d B -> %d B / %s'%(len(before),len(after),hashlib.sha256(after).hexdigest()))
J=json.loads(after.decode('utf-8'))
print('  gates mentions rev 39:', '39' in J['handoffCitationRisk']['landingGate']['gates'])
print('  gateHistoryNote unchanged:', J['handoffCitationRisk']['landingGate']['gateHistoryNote'][:60])
p=os.path.join(d,'implementation-payload-TM600-TM601.cpp'); pr=open(p,'rb').read()
print('  payload untouched:', hashlib.sha256(pr).hexdigest()=='66abc088ae6bd5f9b9d7201673003fc0be2450fd6f1f222c6a4a902cbe4f0cc4')
print('  published payload in criterion (revision-agnostic):', 'mustContain' in J['handoffCitationRisk'])