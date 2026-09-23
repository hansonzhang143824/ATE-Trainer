import sys,io,os,json
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
base=r'D:\Newtest\DSH\ATE-Coding-Plat'
p=os.path.join(base,'project','DALI','meta','dali_tm_meta.json')
M=json.loads(open(p,'rb').read().decode('utf-8-sig'))
print('top-level type:',type(M).__name__, list(M)[:6] if isinstance(M,dict) else len(M))
# locate the two entries flexibly
found={}
def walk(o,path=''):
    if isinstance(o,dict):
        for k,v in o.items():
            if k in ('TM601_LS_RDSON','TM600_HS_RDSON'): found[k]=(path,v)
            walk(v,path+'/'+str(k))
    elif isinstance(o,list):
        for i,v in enumerate(o):
            if isinstance(v,dict) and v.get('name') in ('TM601_LS_RDSON','TM600_HS_RDSON'): found[v['name']]=(path+'[%d]'%i,v)
            walk(v,path+'[%d]'%i)
walk(M)
for k,(path,v) in found.items():
    print('===',k,'at',path)
    print(json.dumps(v,ensure_ascii=False,indent=1)[:1200])