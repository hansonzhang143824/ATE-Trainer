import sys,io,os,re
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
u=open(os.path.join(d,'implementation-payload-TM600-TM601.cpp'),'rb').read().decode('utf-8-sig')
code=[l for l in u.split('\n') if not l.strip().startswith('//')]
print('=== early-return / skip-cleanup enumeration (executable code) ===')
print('  return statements:',[l.strip()[:80] for l in code if re.search(r'\breturn\b',l)])
print('  goto/break/continue/throw:',[l.strip()[:70] for l in code if re.search(r'\b(goto|break|continue|throw)\b',l)])
print('  "return" total:',sum(1 for l in code if re.search(r'\breturn\b',l)))
print()
print('=== the two measurement blocks (executable) ===')
for i,l in enumerate(code):
    if 'GetMeasResult(site, M' in l or 'rdson[site] =' in l or 'SetTestResult' in l:
        print('  ',l.strip()[:120])
print()
print('=== MVRET/MIRET counts ===',sum(l.count('MVRET') for l in code),sum(l.count('MIRET') for l in code))