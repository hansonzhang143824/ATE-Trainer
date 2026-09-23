import sys,io,os,json,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
J=json.loads(open(os.path.join(d,'setup-contract.json'),'rb').read().decode('utf-8-sig'))
s=json.dumps(J,ensure_ascii=False)
i=s.find('signConvention')
print('=== signConvention block ===')
print(s[max(0,i-100):i+2600].replace('\\n',' ')[:2700])