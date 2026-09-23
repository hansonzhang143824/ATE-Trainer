import sys,io,os,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'implementation-payload-TM600-TM601.cpp')
u=open(p,'rb').read().decode('utf-8-sig').replace('\r\n','\n')
start=u.find('    // FR-001 REVERSE - CLOSURES ARE LIMITED')
end=u.find('cbite.SetOn(K154_BUSH0_AMUX',start)
end=u.find('\n',end)
print('replacing comment+setOn region of',end-start,'chars')
new=('''    // FR-001 REVERSE - CLOSURES LIMITED TO THE RAIL THIS FUNCTION ACTUALLY POWERS.
    // This item powers SW (low side) and PGND (high side), both on FPVIe0 CH0:
    //   CH0 Low  -> SW   [Kelvin] needsClosed: K60,K61   (SCH-Connect-Map.txt:174)
    //   CH0 High -> PGND [Kelvin] needsClosed: K154,K155 (SCH-Connect-Map.txt:156)
    // K57 IS closed on purpose: K57_CAP_BST_SW (:220) sits on SW via Cap_SW_BST_S1 220nF
    //   ("SW 稳压 needsClosed: K57", :904), and SW is the node the 1 A measurement current
    //   actually traverses (the force returns through the low terminal), so FR-001's reverse
    //   requirement is supported by the wiring here.
    // K5_VBUS_Cap IS NOT CLOSED - the earlier rationale was wrong and is withdrawn. This function
    //   does not power VBUS: the low-side group reaches SW through K60,K61 and VCP through K60,
    //   whereas VBUS is reached only via CH0 Low -> VBUS needsClosed: K3 (:213) or the CH1 route
    //   K138,K139,K145,K146,K3 (:421). The VBUS token is present in this item's meta powered_pins,
    //   but meta presence is not proof that THIS function drives the rail, and no K3 closure exists
    //   here. Closing K5 would switch in a 4.7uF branch on the vendor's VBUS bulk cap for a rail
    //   that is not energised on the tester side - (V-B) an exception, not a silencer.
    // K44_Cap_SW2_BST2 (:205) and K45_Cap_SW1_BST1 (:206) ARE NOT CLOSED - SW1 and SW2 are
    //   DIFFERENT NODES from SW: SW1 needs K46 (:177), SW2 needs K46+K49 (:183), and this function
    //   routes to neither. They are flagged only because the gate folds the family by PREFIX
    //   (cap_pin("K45_Cap_SW1_BST1") -> SW1_BST1, then fam_intersect matches the powered pin "SW"
    //   because "SW1_BST1".startswith("SW")) - a name-prefix collision across distinct rails.
    //   Closing K44/K45 would energise rails this item does not use.
    // SETTLING IS NOT ANALYSED, and this is NOT an assertion of inertness: K57 is a pin-to-cap
    //   branch (220nF) that changes the RC settling of the very rail being measured. With F6 giving
    //   ZERO on-paper margin inside the 2 ms force window, the effect on settling is a BRING-UP
    //   VERIFICATION ITEM (with U11), to be measured on hardware - not argued away here.
    cbite.SetOn(K154_BUSH0_AMUX, K155_FOVI3_PGND, K60_BUSL0_VCP, K61_ACM8_SW, K13_VBAT_Cap, K85_CAP_PMID, K57_CAP_BST_SW, K126_V1P5_CAP, -1);''')
u=u[:start]+new+u[end:]
open(p,'wb').write(b'\xef\xbb\xbf'+u.replace('\n','\r\n').encode('utf-8'))
r=open(p,'rb').read(); v=r.decode('utf-8-sig'); code=[l for l in v.split('\n') if not l.strip().startswith('//')]
print('payload %d B / %s'%(len(r),hashlib.sha256(r).hexdigest()))
for l in code:
    if 'SetOn(' in l: print('  ',l.strip()[:170])
print('K5/K44/K45 in code:',sum(l.count('K5_VBUS_Cap')+l.count('K44_Cap_SW2_BST2')+l.count('K45_Cap_SW1_BST1') for l in code))
print('inert claim gone:', 'inert for the measurement' not in v, '| settling caveat present:','SETTLING IS NOT ANALYSED' in v)