import sys,io,os,shutil,json,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
base=r'D:\Newtest\DSH\ATE-Coding-Plat'
sbx=os.path.join(base,'team','artifacts','acceptance-20260916-dali10','gate-check-t21','source')
os.makedirs(sbx,exist_ok=True)
real=r'D:\PROJECT6-DALI\ForCodexDebug\source'
n=0
for f in os.listdir(real):
    s=os.path.join(real,f)
    if os.path.isfile(s):
        shutil.copy2(s,os.path.join(sbx,f)); n+=1
print('copied %d files to sandbox'%n)
# patch the sandbox copy
p=os.path.join(sbx,'test.cpp'); cur=open(p,'rb').read().decode('utf-8-sig')
o601='    cbite.SetOn(K154_BUSH0_AMUX, K155_FOVI3_PGND, K60_BUSL0_VCP, K61_ACM8_SW, K13_VBAT_Cap, K85_CAP_PMID, 126, -1);'
n601='    cbite.SetOn(K154_BUSH0_AMUX, K155_FOVI3_PGND, K60_BUSL0_VCP, K61_ACM8_SW, K13_VBAT_Cap, K85_CAP_PMID, K57_CAP_BST_SW, K44_Cap_SW2_BST2, K45_Cap_SW1_BST1, K5_VBUS_Cap, K126_V1P5_CAP, -1);'
o600='    cbite.SetOn(K83_BUSH0_PMID, K60_BUSL0_VCP, K61_ACM8_SW, K13_VBAT_Cap, K85_CAP_PMID, K57_CAP_BST_SW, 126, -1);'
n600='    cbite.SetOn(K83_BUSH0_PMID, K60_BUSL0_VCP, K61_ACM8_SW, K13_VBAT_Cap, K85_CAP_PMID, K57_CAP_BST_SW, K126_V1P5_CAP, -1);'
print('patch targets found: TM601=%d TM600=%d'%(cur.count(o601),cur.count(o600)))
open(p,'w',encoding='utf-8',newline='').write(cur.replace(o601,n601).replace(o600,n600))
r=open(p,'rb').read(); print('sandbox test.cpp: %d B / %s'%(len(r),hashlib.sha256(r).hexdigest()))
# point config at the sandbox (restore later)
cp=os.path.join(base,'project_config.json')
orig=open(cp,'rb').read()
open(os.path.join(base,'team','artifacts','acceptance-20260916-dali10','gate-check-t21','project_config.orig.json'),'wb').write(orig)
J=json.loads(orig.decode('utf-8-sig'))
J['inputs']['vs_src_dir']=sbx.replace('\\','/')
J['inputs']['relay_definitions']=os.path.join(sbx,'StdAfx.h').replace('\\','/')
J['inputs']['channelmap']=os.path.join(sbx,'Pin_Channel_define.h').replace('\\','/')
open(cp,'w',encoding='utf-8').write(json.dumps(J,ensure_ascii=False,indent=2))
print('config temporarily repointed to sandbox (original saved)')