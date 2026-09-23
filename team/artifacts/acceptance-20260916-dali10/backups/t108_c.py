import sys,io,os,re,json
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
base=r'D:\Newtest\DSH\ATE-Coding-Plat'
p=os.path.join(base,'team','artifacts','acceptance-20260916-dali10','acceptance-report.json')
t=open(p,'rb').read().decode('utf-8-sig',errors='replace')
print('=== context of each 2d0984d9 (superseded) occurrence — is it LABELLED? ===')
for m in re.finditer(r'2d0984d992d5d8cb',t):
    s=max(0,m.start()-320); e=m.start()+220
    seg=t[s:e].replace('\n',' ')
    print('  @%d:'%m.start())
    print('   ...%s...'%seg[-440:])
    print()
print('=== and try to parse the JSON to see the structural FIELD names ===')
try:
    J=json.loads(t)
    def walk(o,path=''):
        if isinstance(o,dict):
            for k,v in o.items():
                if isinstance(v,str) and '2d0984d9' in v:
                    print('  field %s = %s'%(path+'/'+k, v[:80]))
                walk(v,path+'/'+str(k))
        elif isinstance(o,list):
            for i,v in enumerate(o): walk(v,path+'[%d]'%i)
    walk(J)
except Exception as ex: print('  (not parseable as JSON:',ex,')')