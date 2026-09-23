import sys,io,os,json,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'implementation-manifest.draft.json')
J=json.loads(open(p,'rb').read().decode('utf-8-sig'))
ch=J['changes'][0]
ch['payloadSha256']='7399598332fac6c342ec44f2e0217e5f43cebc499e17974e4b8c431aded1885b'
ch['payloadSize']=32969
ch['repairNote']=('t21 rev3 (option B): TM601 closes only K57_CAP_BST_SW plus the terminal/cap-gate relays. K5_VBUS_Cap, '
 'K44_Cap_SW2_BST2 and K45_Cap_SW1_BST1 are deliberately NOT closed, each with a locator: VBUS is not a TM601 ATE '
 'stimulus (BD-08; the meta carries simulation-domain vbus 5.0) and arrives via K3, while SW1/SW2 are different nodes '
 'from SW. K126_V1P5_CAP retained. See t21-tm601-fr001-exception.md.')
J['newRedTriage']['relay-trace_TM601_caps']={
 'status':'NAMED EXCEPTION (option B) - K5/K44/K45 not closed; K57 closed',
 'evidence':('Root cause is the meta authority model, proved from the meta text itself: TM601_LS_RDSON hardwareInit carries '
   'vset vbat 3.5 / vset vbus 5.0 (the OVERVIEW/.sv layer) and capAuthority.powered_pins contains VBUS, while the frozen '
   'ATE stimulus is VBAT 4.2 / PMID 9 / VDRV 5 with VBUS simulation-only (BD-08 + test-plan v20). gen_testitems_meta.py:148-149 '
   'derives powered_pins from the OVERVIEW row. Wiring: CH0 Low -> SW needs K60,K61 (SCH-Connect-Map.txt:174); CH0 High -> PGND '
   'needs K154,K155 (:156); VBUS needs K3 (:213); SW1 needs K46 (:177); SW2 needs K46,K49 (:183). K44/K45 are flagged only by '
   'name-prefix family folding (verify_relay_trace.py:56-58 with cap_pin :100-115). K57 is closed because the exemption at '
   ':325-326 is keyed on mi_pins/ramp_pins and this item meta declares both EMPTY - though populating mi_pins under option (A) '
   'would exempt SW and remove the need for K57 as well.')}
J['limitations'].append('TM601_LS_RDSON does not close K5_VBUS_Cap / K44_Cap_SW2_BST2 / K45_Cap_SW1_BST1. K5: VBUS is not a TM601 ATE stimulus (BD-08) and is reached only via K3; the meta powered_pins VBUS entry derives from the simulation-domain OVERVIEW row. K44/K45: SW1 and SW2 are different nodes from SW (K46 / K46,K49) and are not in powered_pins. Recorded as a named exception with locators, not as a code gap. K57_CAP_BST_SW IS closed (SW is the measured-current node; the rule exemption is keyed on the empty mi_pins set).')
J['limitations'].append('The relay-trace gate reports 3 warnings on TM601_LS_RDSON (SW family folded by prefix twice, plus VBUS) and 2 pre-existing on TM643. These cannot be cleared by code without closing relays on rails the item does not use; the fix belongs in the meta authority inputs (run-scope override) or the harness family folding.')
open(p,'wb').write((json.dumps(J,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
r=open(p,'rb').read(); print('draft %d B / %s valid=%s'%(len(r),hashlib.sha256(r).hexdigest(),bool(json.loads(r.decode('utf-8')))))
a=os.path.join(d,'t21-tm601-fr001-exception.md'); ra=open(a,'rb').read()
print('exception doc %d B / %s'%(len(ra),hashlib.sha256(ra).hexdigest()))
pay=os.path.join(d,'implementation-payload-TM600-TM601.cpp'); rp=open(pay,'rb').read()
v=rp.decode('utf-8-sig'); code=[l for l in v.split('\n') if not l.strip().startswith('//')]
print('payload %d B / %s'%(len(rp),hashlib.sha256(rp).hexdigest()))
print('  K5/K44/K45 in code: %d | K57: %d | K126: %d'%(
 sum(l.count('K5_VBUS_Cap')+l.count('K44_Cap_SW2_BST2')+l.count('K45_Cap_SW1_BST1') for l in code),
 sum(l.count('K57_CAP_BST_SW') for l in code),sum(l.count('K126_V1P5_CAP') for l in code)))
print('  guards=%d delay_ms(1)=%d delay_ms(2)=%d'%(sum(l.count('i_meas[site] > 0.1') for l in code),
 sum(l.count('delay_ms(1)') for l in code),sum(l.count('delay_ms(2)') for l in code)))
s=open(r'D:\PROJECT6-DALI\ForCodexDebug\source\test.cpp','rb').read()
print('target unchanged:',hashlib.sha256(s).hexdigest()=='3dbceb496d79d7d08631713b98e46c0c2ba6163eaf5356a87dded677e35ba479')