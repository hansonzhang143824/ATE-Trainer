import sys,io,os,json,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
base=r'D:\Newtest\DSH\ATE-Coding-Plat'
cfg=json.load(open(os.path.join(base,'project_config.json'),'rb').read().decode('utf-8-sig'))
def find(o,path=''):
    if isinstance(o,dict):
        for k,v in o.items():
            if 'test' in k.lower() and isinstance(v,str) and v.endswith('.cpp'): print('  %s.%s = %s'%(path,k,v))
            find(v,path+'.'+k)
    elif isinstance(o,list):
        for i,v in enumerate(o): find(v,path+'[%d]'%i)
print('=== config paths mentioning test.cpp ==='); find(cfg)
print()
print('relay_definitions:',cfg.get('inputs',{}).get('relay_definitions'))
print('singlepoint_bench:',(cfg.get('intermediates') or {}).get('singlepoint_bench'))