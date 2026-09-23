import sys,io,os,json
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
base=r'D:\Newtest\DSH\ATE-Coding-Plat'
gc=os.path.join(base,'team','artifacts','acceptance-20260916-dali10','gate-check-t21')
orig=open(os.path.join(gc,'project_config.orig.json'),'rb').read()
J=json.loads(orig.decode('utf-8-sig'))
def absify(p):
    p=p.replace('/','\\')
    return p if os.path.isabs(p) else os.path.join(base,p).replace('/','\\')
print('keys in inputs:',list(J['inputs'].keys()))
print('vs_src_dir ->',os.path.join(gc,'baseline-source').replace('/','\\'))
J['inputs']['vs_src_dir']=os.path.join(gc,'baseline-source').replace('\\','/')
J['inputs']['relay_definitions']=os.path.join(gc,'baseline-source','StdAfx.h').replace('\\','/')
J['inputs']['channelmap']=os.path.join(gc,'baseline-source','Pin_Channel_define.h').replace('\\','/')
# make sure every relative input resolves from the repo root (config location)
for k,v in list(J['inputs'].items()):
    if isinstance(v,str) and not os.path.isabs(v.replace('/','\\')) and not v.startswith('D:'):
        J['inputs'][k]=absify(v).replace('\\','/')
for sec in ('intermediates','outputs'):
    if isinstance(J.get(sec),dict):
        for k,v in list(J[sec].items()):
            if isinstance(v,str) and not os.path.isabs(v.replace('/','\\')) and not v.startswith('D:'):
                J[sec][k]=absify(v).replace('\\','/')
ov=os.path.join(base,'team_t21_baseline_config.json')
open(ov,'w',encoding='utf-8').write(json.dumps(J,ensure_ascii=False,indent=2))
print('overlay config at repo root:',ov)