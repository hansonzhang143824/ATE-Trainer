import sys,io,os,re,hashlib,glob
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
base=r'D:\Newtest\DSH\ATE-Coding-Plat'
work=os.path.join(base,'team','artifacts','acceptance-20260916-dali10','gate-check-t21')
tgt=os.path.join(r'D:\PROJECT6-DALI\ForCodexDebug','source','test.cpp')
cur=open(tgt,'rb').read().decode('utf-8-sig')
# exact-set variant: TM601 line with the four caps added, 126 kept as the named form matching the payload
var601='    cbite.SetOn(K154_BUSH0_AMUX, K155_FOVI3_PGND, K60_BUSL0_VCP, K61_ACM8_SW, K13_VBAT_Cap, K85_CAP_PMID, K57_CAP_BST_SW, K44_Cap_SW2_BST2, K45_Cap_SW1_BST1, K5_VBUS_Cap, 126, -1);'
var600='    cbite.SetOn(K83_BUSH0_PMID, K60_BUSL0_VCP, K61_ACM8_SW, K13_VBAT_Cap, K85_CAP_PMID, K57_CAP_BST_SW, K126_V1P5_CAP, -1);'
o601='    cbite.SetOn(K154_BUSH0_AMUX, K155_FOVI3_PGND, K60_BUSL0_VCP, K61_ACM8_SW, K13_VBAT_Cap, K85_CAP_PMID, 126, -1);'
o600='    cbite.SetOn(K83_BUSH0_PMID, K60_BUSL0_VCP, K61_ACM8_SW, K13_VBAT_Cap, K85_CAP_PMID, K57_CAP_BST_SW, 126, -1);'
print('exact target lines found: TM601=%d TM600=%d'%(cur.count(o601),cur.count(o600)))
patched=cur.replace(o601,var601).replace(o600,var600)
pt=os.path.join(work,'test.cpp')
open(pt,'w',encoding='utf-8',newline='').write(patched)
r=open(pt,'rb').read()
print('patched copy: %d B / %s'%(len(r),hashlib.sha256(r).hexdigest()))
print()
print('=== run the real relay-trace gate on the patched copy ===')