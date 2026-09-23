import sys,io,os,re,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'implementation-payload-TM600-TM601.cpp')
u=open(p,'rb').read().decode('utf-8-sig').replace('\r\n','\n')
old='    cbite.SetOn(K83_BUSH0_PMID, K60_BUSL0_VCP, K61_ACM8_SW, K13_VBAT_Cap, K85_CAP_PMID, K57_CAP_BST_SW, K126_V1P5_CAP, -1);'
new=('''    // t29 FIX - BST EXCITATION PATH (contract conformance, high severity).
    // The BST-SW rail is driven by the ground-referenced ACM200 SW12_U1REF_BST_ACM per ruling (ii).
    // K110_ACM18_BST is a DOUBLE-THROW relay and its name alone does NOT route the source to BST:
    //   S5_ACM200_FH18 -> K110(Relay-NC) -> PB0_F   (SCH-Connect-Map.txt:724)
    //   S5_ACM200_SH18 -> K110(Relay-NC) -> PB0_S   (:725)
    // i.e. un-actuated it steers the ACM18 source to the PB0 PWM pin. Only when K110 is closed does
    // the source continue to BST:
    //   ... K109(Relay-ON) -> K110(Relay-ON) -> BST_F   (:43)
    //   ... K109(Relay-ON) -> K110(Relay-NC) -> PB0_F   (:109)
    // while K109_BUSL1_PB0 selects the branch. Route requirement: CH0 Low -> BST needsClosed
    // K109,K110,... (:42; contract pinRouteTable BST/CH0 Low = [109,110,138,139,145,146]).
    // Without K110 the ACM source reaches PB0, not BST, so ruling (ii)'s "ground-referenced drive of
    // BST-SW" would not hold electrically. "The fixture may hard-wire it" is NOT an acceptable
    // omission: both the contract and the connect map require the closure.
    // Negative list: K109/K110 are NOT part of the forbidden 87/88/89/90/91 class, and the
    // unrealisable ch1 composite (K_FPVIH_TO_BST_B = 131,132,134,135) is NOT used here.
    cbite.SetOn(K83_BUSH0_PMID, K60_BUSL0_VCP, K61_ACM8_SW, K109_BUSL1_PB0, K110_ACM18_BST, K13_VBAT_Cap, K85_CAP_PMID, K57_CAP_BST_SW, K126_V1P5_CAP, -1);''')
n=u.count(old); print('TM600 SetOn matched:',n)
if n==1:
    u=u.replace(old,new)
    open(p,'wb').write(b'\xef\xbb\xbf'+u.replace('\n','\r\n').encode('utf-8'))
r=open(p,'rb').read(); v=r.decode('utf-8-sig'); c=re.sub(r'//.*$','',v,flags=re.M)
print('payload %d B / %s'%(len(r),hashlib.sha256(r).hexdigest()))
print()
print('=== invariant matrix (comments stripped) ===')
for k,exp in [('delay_ms(1)',6),('delay_ms(2)',0),('SetClamp(50, 50)',2),('MeasureVI(200, 5, FPVIe_MV_X10)',2),('K126_V1P5_CAP',2),('ERROR_RES',2),('K5_VBUS_Cap',0),('K44_Cap_SW2_BST2',0),('K45_Cap_SW1_BST1',0),('K57_CAP_BST_SW',2)]:
    got=c.count(k); print('  %-34s %d  expected %d  %s'%(k,got,exp,'OK' if got==exp else 'MISMATCH'))
print('  bare 126 tokens                   %d  expected 0'%len(re.findall(r'(?<![\dA-Za-z_])126(?![\dA-Za-z_])',c)))
print('  rampi_capv+rampv_capv             %d  expected 0'%(c.count('rampi_capv')+c.count('rampv_capv')))
print('  composite K_FPVIH_TO_BST_B used   %d  expected 0'%c.count('K_FPVIH_TO_BST_B'))
print('  K109 present                      %d, K110 present %d'%(c.count('K109_BUSL1_PB0'),c.count('K110_ACM18_BST')))
print('  BOM',r[:3]==b'\xef\xbb\xbf','| loneLF',r.count(b'\n')-r.count(b'\r\n'))