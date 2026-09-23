import sys,io,os,json
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
p=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10\dft-raw\dft-ir-hashes.json'
s=open(p,'rb').read().decode('utf-8-sig')
print('top-level keys:',list(json.loads(s).keys()))
for tok in ['lateRulingsNotInIR','BD-05','provisional','SetClamp','U9']:
    print('  %-20s %s'%(tok, tok in s))
import re
i=s.find('BD-05')
print()
print('BD-05 context:',s[max(0,i-200):i+420].replace('\n',' ')[:620] if i>0 else '(absent)')