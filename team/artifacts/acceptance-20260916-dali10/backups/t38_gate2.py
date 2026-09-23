import sys,io,os,json,hashlib,re
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'implementation-manifest.json')
M=json.loads(open(p,'rb').read().decode('utf-8-sig'))
u=open(os.path.join(d,'implementation-payload-TM600-TM601.cpp'),'rb').read().decode('utf-8-sig')
code=re.sub(r'//.*$','',u,flags=re.M).split('\n')
def n(k): return sum(l.count(k) for l in code)
blk=M['handoffCitationRisk']
blk['landingGate']={
 'status':'BLOCKED - the payload must NOT be treated as electrically correct or cleared to land.',
 'gates':['t40 (rule-reviewer, independent)','t42 (schematic-expert, ACM200 pin attribution)'],
 'completed':['t39 (contract owner) - COMPLETE; its conclusion was reached under the ch18 premise, which is exactly what t42 can overturn'],
 'whyT42Matters':('t42 decides which ACM200 pin drives SW12_U1REF_BST_ACM, which changes WHICH RELAYS ARE REQUIRED: '
   'the netlist gives S5_ACM200_FH5 -> K48 -> K76 -> BST_F (SCH-Connect-Map.txt:672-674, section 6 ACM200 column) '
   '=> pin 5 requires [48,76] and NOT K109/K110. Under that reading this payload closes the FPVIe-side leg while the '
   'ACM200-side leg is open, so TM600 may also be affected. TM601 is unaffected either way: it owns none of 48/76/109/110.'),
 'tm600ExposureOpen':('OPEN, not settled: neither K48 nor K76 is closed by this payload, while K109/K110 are. '
   'Separability is the captain\'s call, and the schematic-expert corrected the framing: closing K48 is a '
   'topology change ("rerouting ch5 from SW1 to BST"), not an additive superposition, so any conjunctive use of '
   'the instrument as an SW1/SW2 source must be assessed before splitting the work.'),
 'verifiedCounts':{'payloadSha256':hashlib.sha256(open(os.path.join(d,'implementation-payload-TM600-TM601.cpp'),'rb').read()).hexdigest(),
   'executableK109_BUSL1_PB0':n('K109_BUSL1_PB0'),'executableK110_ACM18_BST':n('K110_ACM18_BST'),
   'executableERROR_RES':n('ERROR_RES'),'executableK48':n('K48'),'executableK76':n('K76'),
   'note':'K48/K76 = 0 in executable code: this revision addresses the FPVIe-side route only.'},
 'noSelfApproval':'The author of this payload does not certify it; t40/t42 rulings and the captain\'s REPLACE are outstanding.'}
msgs=M.get('reviewStatus',{}).get('statement')
if msgs: M['reviewStatus']['landingGate']='BLOCKED pending t40 + t42 (t39 complete). See handoffCitationRisk.landingGate.'
open(p,'wb').write((json.dumps(M,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
r=open(p,'rb').read(); s=r.decode('utf-8')
print('manifest %d B / %s'%(len(r),hashlib.sha256(r).hexdigest()))
print('  states t40 + t42:', 't40 + t42' in s)
print('  landingGate keys:',list(json.loads(s)['handoffCitationRisk']['landingGate'].keys()))
print('  valid JSON:',bool(json.loads(s)))