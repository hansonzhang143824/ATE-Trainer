import sys,io,json
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
p=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10\test-plan.json'
J=json.loads(open(p,'rb').read().decode('utf-8-sig'))
print('=== globalRulesApplied ==='); print(json.dumps(J.get('globalRulesApplied'),ensure_ascii=False,indent=1)[:3500])