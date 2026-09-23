import sys,io,json
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
p=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10\test-plan.json'
d=json.loads(open(p,'rb').read().decode('utf-8-sig'))
print('revision:',d.get('revision'))
for it in d.get('items',[]):
    if it.get('tm') in ('TM600','TM601'):
        print('\n#### %s %s'%(it.get('tm'),it.get('symbol')))
        for prm in it.get('parameters',[]):
            print('   param %-16s = %s'%(prm.get('name'),str(prm.get('value'))[:110]))
        mp=it.get('measurement',{})
        print('   samples:',json.dumps(mp.get('samples'),ensure_ascii=False)[:200])
        dp=mp.get('decisionPoint',{})
        print('   DV-01 status:',dp.get('status'))
        sa=mp.get('activationSemantics',{})
        print('   activation steps:',json.dumps(sa.get('orderedSteps'),ensure_ascii=False)[:400])