import sys,io,os,re,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'implementation-payload-TM600-TM601.cpp')
u=open(p,'rb').read().decode('utf-8-sig').replace('\r\n','\n')
before=u
# 1) remove the dangling ACM drives in the TM601 region only (unique 4-space-indented forms)
out=[]
s=u.find('DUT_API int TM601_LS_RDSON')
head,body=u[:s],u[s:]
removed=[]
def drop(line_frag,reason):
    global body
    lines=body.split('\n'); keep=[]
    for l in lines:
        if line_frag in l and not l.strip().startswith('//'):
            removed.append((line_frag.strip()[:70],reason)); continue
        keep.append(l)
    body='\n'.join(keep)
drop('SW12_U1REF_BST_ACM.Set(FV, 5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);','dangling TM601 ACM drive (no BST path, no contract requirement)')
drop('SW12_U1REF_BST_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);','TM601 ACM zero-return for the removed drive')
drop('SW12_U1REF_BST_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);','TM601 ACM RELAY_OFF for the removed drive')
u=head+body
# 2) correct the now-false comment claim and record the finding inline
old_c=('    // (SCH-Connect-Map.txt:724) and SH18 -> K110(NC) -> PB0_S (:725), while the BST path requires\n'
 '    // K109(ON) -> K110(ON) -> BST_F (:43, and :268/:269 for CH1). This item never drives that rail, so\n'
 '    // closing K109/K110 here would be an unmotivated relay actuation, not a fix.')
new_c=('    // (SCH-Connect-Map.txt:724) and SH18 -> K110(NC) -> PB0_S (:725), while the BST path requires\n'
 '    // K109(ON) -> K110(ON) -> BST_F (:43, and :268/:269 for CH1). t38 REMOVED the ACM excitation that\n'
 '    // used to be switched on in this function: it was a DANGLING drive - the source was commanded to 5 V\n'
 '    // but, with K110 un-actuated, it landed on PB0 and never reached BST. Removing it is the correct\n'
 '    // remedy rather than closing K109/K110, because this item has NO BST requirement in any source:\n'
 '    //   * DFT.csv - its row (L98) declares no bst2sw stimulus (the TM600 row declares none either);\n'
 '    //   * setup-contract - TM601.pinRouteTable has NO BST node, TM601.relaySet contains neither 109 nor 110,\n'
 '    //     and aliasResolution[3] (bst2sw) lists usedByTm = TM600 and TM1205 only;\n'
 '    //   * netlist (SCH-Connect-Map.txt) - the only paths to BST need K109(ON)+K110(ON) (:42/:43), which no\n'
 '    //     authority assigns to this item.\n'
 '    // Closing K109/K110 here would therefore be an unmotivated relay actuation on a rail the item does not use.\n'
 '    // SW side is complete as required: CH0 Low -> SW needsClosed K60,K61 (:174) and both are closed, and the\n'
 '    // SW stabiliser K57_CAP_BST_SW (Cap_SW_BST_S1, :904) remains closed.')
n=u.count(old_c); print('TM601 comment block matched:',n)
if n==1: u=u.replace(old_c,new_c)
open(p,'wb').write(b'\xef\xbb\xbf'+u.replace('\n','\r\n').encode('utf-8'))
r=open(p,'rb').read(); v=r.decode('utf-8-sig'); c=re.sub(r'//.*$','',v,flags=re.M)
print('removed lines:')
for f,why in removed: print('   -',f,'|',why)
print()
print('payload %d B -> %d B / %s'%(len(before.encode('utf-8')),len(r),hashlib.sha256(r).hexdigest()))
print("TM601 SW12 ACM Sets remaining:",len(re.findall(r'SW12_U1REF_BST_ACM\.Set', v[v.find('DUT_API int TM601_LS_RDSON'):])))
print("TM600 SW12 ACM Sets (must be unchanged 13):",len(re.findall(r'SW12_U1REF_BST_ACM\.Set', v[:v.find('DUT_API int TM601_LS_RDSON')])))
print()
print('=== invariants (comments stripped) ===')
for k,exp in [('delay_ms(1)',6),('delay_ms(2)',0),('SetClamp(50, 50)',2),('MeasureVI(200, 5, FPVIe_MV_X10)',2),('K126_V1P5_CAP',2),('ERROR_RES',2),('K57_CAP_BST_SW',2),('K5_VBUS_Cap',0),('K44_Cap_SW2_BST2',0),('K45_Cap_SW1_BST1',0),('K109_BUSL1_PB0',1),('K110_ACM18_BST',1)]:
    g=c.count(k); print('  %-32s %d  expect %d  %s'%(k,g,exp,'OK' if g==exp else 'MISMATCH'))
print('  bare 126:',len(re.findall(r'(?<![\dA-Za-z_])126(?![\dA-Za-z_])',c)),'| ramp family:',c.count('rampi_capv')+c.count('rampv_capv'),'| composite:',c.count('K_FPVIH_TO_BST_B')+c.count('K_FPVIL_TO_SW_B'))
print('  BOM',r[:3]==b'\xef\xbb\xbf','| loneLF',r.count(b'\n')-r.count(b'\r\n'))