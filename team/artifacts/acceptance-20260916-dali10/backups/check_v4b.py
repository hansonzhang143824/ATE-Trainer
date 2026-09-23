import sys,io,os,json,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
for n in ('test-plan.v4.json','test-plan.json'):
    p=os.path.join(d,n); r=open(p,'rb').read(); J=json.loads(r.decode('utf-8-sig'))
    it=[x for x in J['items'] if x.get('tm')=='TM600'][0]
    m=it.get('measurement',{})
    pc=m.get('pulseCap') or {}
    print('%-22s %8d B rev=%s'%(n,len(r),str(J.get('revision'))[:40]))
    print('    pulseCap value:',pc.get('value'),pc.get('unit'),'| present:',bool(pc))
    print('    boundaryStatement matches user wording:', '须上机验证' in str(J.get('boundaryStatement')) or 'bench-signoff' in str(J.get('boundaryStatement')))
    print('    limitations count:',len(J.get('limitations') or []))
    print('    U10 present:','U10' in json.dumps(J))
    print('    revisionHistory:','revisionHistory' in J)
    print('    clampReissueStricterThanGolden param:',[x.get('name') for x in it.get('parameters',[]) if 'Stricter' in str(x.get('name'))])