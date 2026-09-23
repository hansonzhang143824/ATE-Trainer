import sys,io,os,re,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
base=r'D:\Newtest\DSH\ATE-Coding-Plat'
work=os.path.join(base,'team','artifacts','acceptance-20260916-dali10','gate-check-t21')
os.makedirs(work,exist_ok=True)
tgt=os.path.join(r'D:\PROJECT6-DALI\ForCodexDebug','source','test.cpp')
cur=open(tgt,'rb').read().decode('utf-8-sig')
pay=open(os.path.join(base,'team','artifacts','acceptance-20260916-dali10','implementation-payload-TM600-TM601.cpp'),'rb').read().decode('utf-8-sig')
s=pay.find('DUT_API int TM600_HS_RDSON'); e=pay.rfind('DUT_API int')
# payload body = from the first TM600 function to end; take everything from the TM600 header onward
body=pay[s:]
o1='    cbite.SetOn(K154_BUSH0_AMUX, K155_FOVI3_PGND, K60_BUSL0_VCP, K61_ACM8_SW, K13_VBAT_Cap, K85_CAP_PMID, K126_V1P5_CAP, -1);'
n1='    cbite.SetOn(K154_BUSH0_AMUX, K155_FOVI3_PGND, K60_BUSL0_VCP, K61_ACM8_SW, K13_VBAT_Cap, K85_CAP_PMID, K57_CAP_BST_SW, K44_Cap_SW2_BST2, K45_Cap_SW1_BST1, K5_VBUS_Cap, K126_V1P5_CAP, -1);'
o2='    cbite.SetOn(K83_BUSH0_PMID, K60_BUSL0_VCP, K61_ACM8_SW, K13_VBAT_Cap, K85_CAP_PMID, K57_CAP_BST_SW, 126, -1);'
n2='    cbite.SetOn(K83_BUSH0_PMID, K60_BUSL0_VCP, K61_ACM8_SW, K13_VBAT_Cap, K85_CAP_PMID, K57_CAP_BST_SW, K126_V1P5_CAP, -1);'
print('current TM601 line found:',cur.count(o1),'| TM600 line found:',cur.count(o2))
patched=cur.replace(o1,n1).replace(o2,n2)
pt=os.path.join(work,'test.cpp')
open(pt,'w',encoding='utf-8',newline='').write(patched)
print('patched copy written:',pt,len(patched.encode('utf-8')),'B')
print('  sha256',hashlib.sha256(open(pt,'rb').read()).hexdigest())