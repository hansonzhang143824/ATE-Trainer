import sys,io,os,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'implementation-payload-TM600-TM601.cpp')
u=open(p,'rb').read().decode('utf-8-sig').replace('\r\n','\n')
old=('''    // FR-001 reverse (a powered rail requires its stabiliser cap closed). Names verified against
    // the StdAfx.h single-point defines: K44_Cap_SW2_BST2 (:205), K45_Cap_SW1_BST1 (:206),
    // K57_CAP_BST_SW (:220), K5_VBUS_Cap (:161) for the VBUS rail reachable via K154_BUSH0_AMUX.
    // These closures are stabiliser/protection only and inert for the measurement, which returns
    // through SW and PGND.
    cbite.SetOn(K154_BUSH0_AMUX, K155_FOVI3_PGND, K60_BUSL0_VCP, K61_ACM8_SW, K13_VBAT_Cap, K85_CAP_PMID, K57_CAP_BST_SW, K44_Cap_SW2_BST2, K45_Cap_SW1_BST1, K5_VBUS_Cap, K126_V1P5_CAP, -1);''')
new=('''    // FR-001 REVERSE - CLOSURES ARE LIMITED TO WHAT THE WIRING EVIDENCE SUPPORTS.
    // This function powers SW (low side) and PGND (high side). Both are routed on FPVIe0 CH0:
    //   CH0 Low  -> SW   [Kelvin] needsClosed: K60,K61   (SCH-Connect-Map.txt:174)
    //   CH0 High -> PGND [Kelvin] needsClosed: K154,K155 (SCH-Connect-Map.txt:156)
    // The ONLY stabiliser cap on a node this function actually reaches is therefore
    //   K57_CAP_BST_SW (:220) on SW  -- Cap_SW_BST_S1 220nF, "SW 稳压 needsClosed: K57" (:904)
    //   K5_VBUS_Cap  (:161) on VBUS  -- Cap2_VBUS_S1 4.7uF, "VBUS 稳压 needsClosed: K5" (:915)
    // K5 IS closed below: VBUS is a declared powered pin for this item (meta capAuthority
    // powered_pins contains VBUS) and this function does expose the VBUS rail through its own
    // channel - ACM200 channel S5_5 reaches SW via K61 (:771) and VBUS is one relay away through
    // the same low-side group (CH0 Low -> VBUS needsClosed: K3, :213). Closing it is therefore
    // rule-supported and is NOT a name-based guess.
    // DELIBERATE OMISSIONS, recorded as a NAMED EXCEPTION rather than assumed away:
    //   K45_Cap_SW1_BST1 (:206, "SW1 稳压 needsClosed: K45", :905) and
    //   K44_Cap_SW2_BST2 (:205, "SW2 稳压 needsClosed: K44", :906) sit on SW1 and SW2, which are
    //   DIFFERENT NODES from SW - SW1 needs K46 (:177), SW2 needs K46+K49 (:183) - and this
    //   function doesn't route to either. They are only flagged because the gate folds the SW
    //   family by PREFIX (cap_pin -> SW1_BST1/SW2_BST2, fam_intersect matches powered pin 'SW'
    //   since 'SW1_BST1'.startswith('SW')), i.e. a name-prefix collision across distinct rails.
    //   Closing them would energise rails this item does not use, so they are NOT closed here.
    // SETTLING IS NOT ANALYSED: K57 and K5 are pin-to-cap branches (220nF / 4.7uF), not merely
    //   "protection". Their effect on the rail RC settling inside the 2 ms force window has NOT
    //   been analysed and, given F6 leaves zero on-paper margin, that is a BRING-UP VERIFICATION
    //   ITEM alongside U11 - not an assertion of inertness.
    cbite.SetOn(K154_BUSH0_AMUX, K155_FOVI3_PGND, K60_BUSL0_VCP, K61_ACM8_SW, K13_VBAT_Cap, K85_CAP_PMID, K57_CAP_BST_SW, K5_VBUS_Cap, K126_V1P5_CAP, -1);''')
n=u.count(old)
print('TM601 block found:',n)
if n==1:
    u=u.replace(old,new)
    open(p,'wb').write(b'\xef\xbb\xbf'+u.replace('\n','\r\n').encode('utf-8'))
r=open(p,'rb').read(); v=r.decode('utf-8-sig'); code=[l for l in v.split('\n') if not l.strip().startswith('//')]
print('payload %d B / %s'%(len(r),hashlib.sha256(r).hexdigest()))
print('TM601 SetOn now:'); 
for l in code:
    if 'SetOn(' in l: print('  ',l.strip()[:175])
print("'inert for the measurement' removed:", 'inert for the measurement' not in v)
print("K44/K45 in code:",sum(l.count('K44_Cap_SW2_BST2')+l.count('K45_Cap_SW1_BST1') for l in code))
print("K57 closed:",sum(l.count('K57_CAP_BST_SW') for l in code),"| K5 closed:",sum(l.count('K5_VBUS_Cap') for l in code))
print('BOM',r[:3]==b'\xef\xbb\xbf','| loneLF',r.count(b'\n')-r.count(b'\r\n'))