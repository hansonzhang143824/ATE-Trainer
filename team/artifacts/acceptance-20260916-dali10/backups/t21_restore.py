import sys,io,os,json,hashlib,subprocess
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
base=r'D:\Newtest\DSH\ATE-Coding-Plat'
gc=os.path.join(base,'team','artifacts','acceptance-20260916-dali10','gate-check-t21')
# restore the authoritative config IMMEDIATELY
orig=open(os.path.join(gc,'project_config.orig.json'),'rb').read()
cp=os.path.join(base,'project_config.json')
cur=open(cp,'rb').read()
open(cp,'wb').write(orig)
print('project_config.json restored:',hashlib.sha256(open(cp,'rb').read()).hexdigest()==hashlib.sha256(orig).hexdigest())
print('  sha256',hashlib.sha256(open(cp,'rb').read()).hexdigest()[:16])
# now build a BASELINE sandbox (pre-change test.cpp from the verified backup) with its own config
bsbx=os.path.join(gc,'baseline-source'); os.makedirs(bsbx,exist_ok=True)
import shutil
for f in os.listdir(os.path.join(gc,'source')):
    s=os.path.join(gc,'source',f)
    if os.path.isfile(s): shutil.copy2(s,os.path.join(bsbx,f))
bak=os.path.join(base,'team','artifacts','acceptance-20260916-dali10','backups','test.cpp.before_TM600_TM601.bak')
shutil.copy2(bak,os.path.join(bsbx,'test.cpp'))
J=json.loads(orig.decode('utf-8-sig'))
J['inputs']['vs_src_dir']=bsbx.replace('\\','/')
J['inputs']['relay_definitions']=os.path.join(bsbx,'StdAfx.h').replace('\\','/')
J['inputs']['channelmap']=os.path.join(bsbx,'Pin_Channel_define.h').replace('\\','/')
ov=os.path.join(gc,'baseline-config.json')
open(ov,'w',encoding='utf-8').write(json.dumps(J,ensure_ascii=False,indent=2))
print('baseline overlay config written:',ov)
print('baseline sandbox test.cpp sha256:',hashlib.sha256(open(os.path.join(bsbx,'test.cpp'),'rb').read()).hexdigest())