import sys,io,json
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
p=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10\test-plan.json'
d=json.loads(open(p,'rb').read().decode('utf-8-sig'))
print('=== plan-level limitations ==='); print(json.dumps(d.get('limitations'),ensure_ascii=False,indent=1)[:2200])
for it in d.get('items',[]):
    if it.get('tm') in ('TM600','TM601'):
        print('\n=== %s exceptionalRequirements ==='%it.get('tm'))
        for r in it.get('exceptionalRequirements',[]): print('   -',str(r)[:190])