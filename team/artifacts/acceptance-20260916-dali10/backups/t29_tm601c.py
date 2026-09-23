import sys,io,os,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'implementation-payload-TM600-TM601.cpp')
u=open(p,'rb').read().decode('utf-8-sig').replace('\r\n','\n')
old='    cbite.SetOn(K154_BUSH0_AMUX, K155_FOVI3_PGND, K60_BUSL0_VCP, K61_ACM8_SW, K13_VBAT_Cap, K85_CAP_PMID, K57_CAP_BST_SW, K126_V1P5_CAP, -1);'
new=('''    // t29 PER-FUNCTION JUSTIFICATION - WHY THIS ITEM DOES NOT CLOSE K109/K110 (explicit, not omitted).
    // Contract authority, both checked in setup-contract.json (rev 24):
    //   * pinRouteTable: this item's table has nodes SW, PGND, PMID, VBUS, VBAT, VDRV, V1P5, AGND and NO "BST"
    //     node at all - so it declares no BST route and no BST needsClosed. Contrast TM600, whose table does
    //     carry /BST/... with needsClosed [109,110,...] (CH0 Low) and [109,110] (CH1 Low).
    //   * tmDeltas.TM601.relaySet does NOT contain 109 or 110 (it is [3,7,60,61,83,86,130,132,133,134,135,...]),
    //     whereas tmDeltas.TM600.relaySet contains both.
    //   * Stimulus: this item's ateStimulus is {vbat 4.2 V, pmid 9 V, vdrv 5 V} only; there is no bst2sw
    //     stimulus and bst2sw occurs 0 times in its whole delta. Its single textual "BST" is the register
    //     field D2A_BUBO_TM_LSON, not a powered rail.
    // Physical consequence (the reason the distinction is real and not pedantic): the ACM200 bootstrap source
    // is only steered to BST when K110 is closed - S5_ACM200_FH18 -> K110(Relay-NC) -> PB0_F
    // (SCH-Connect-Map.txt:724) and SH18 -> K110(NC) -> PB0_S (:725), while the BST path requires
    // K109(ON) -> K110(ON) -> BST_F (:43, and :268/:269 for CH1). This item never drives that rail, so
    // closing K109/K110 here would be an unmotivated relay actuation, not a fix.
    // Minimal-endpoint discipline: no relay outside this item's contract authority is closed, the negative-list
    // relays (87/88/89/131/132/133, Relay-NC default-conducting) are NOT actuated, and the composite macros
    // K_FPVIH_TO_BST_B / K_FPVIL_TO_SW_B are NOT used (ruling (ii) records that route as unrealisable).
    cbite.SetOn(K154_BUSH0_AMUX, K155_FOVI3_PGND, K60_BUSL0_VCP, K61_ACM8_SW, K13_VBAT_Cap, K85_CAP_PMID, K57_CAP_BST_SW, K126_V1P5_CAP, -1);''')
n=u.count(old); print('TM601 SetOn matched:',n)
if n==1:
    u=u.replace(old,new)
    open(p,'wb').write(b'\xef\xbb\xbf'+u.replace('\n','\r\n').encode('utf-8'))
r=open(p,'rb').read(); v=r.decode('utf-8-sig'); import re
c=re.sub(r'//.*$','',v,flags=re.M)
print('payload %d B / %s'%(len(r),hashlib.sha256(r).hexdigest()))
print('  invariants: delay_ms(1)=%d delay_ms(2)=%d clamp=%d MeasureVI=%d K126=%d ERROR_RES=%d K5/K44/K45=%d K57=%d K109=%d K110=%d'%(
 c.count('delay_ms(1)'),c.count('delay_ms(2)'),c.count('SetClamp(50, 50)'),c.count('MeasureVI(200, 5, FPVIe_MV_X10)'),
 c.count('K126_V1P5_CAP'),c.count('ERROR_RES'),
 c.count('K5_VBUS_Cap')+c.count('K44_Cap_SW2_BST2')+c.count('K45_Cap_SW1_BST1'),c.count('K57_CAP_BST_SW'),
 c.count('K109_BUSL1_PB0'),c.count('K110_ACM18_BST')))
print('  composite used:',c.count('K_FPVIH_TO_BST_B')+c.count('K_FPVIL_TO_SW_B'))
print('  BOM',r[:3]==b'\xef\xbb\xbf','loneLF',r.count(b'\n')-r.count(b'\r\n'))