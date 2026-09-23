import sys,io,os,re
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
p=r'D:\PROJECT6-DALI\ForCodexDebug\source\test.cpp'
t=open(p,'rb').read().decode('utf-8-sig')
lines=t.split('\n')
print('=== existing "if (" guards (first 12) ===')
n=0
for i,l in enumerate(lines):
    if 'if (' in l and not l.strip().startswith('//'):
        n+=1
        if n<=12: print('  %5d: %s'%(i+1,l.strip()[:120]))
print('  total:',n)
print()
print('=== any epsilon / near-zero comparison idiom? ===')
for i,l in enumerate(lines):
    if re.search(r'(1e-|<= *0\.|== *0\.0|< *0\.)',l) and not l.strip().startswith('//'):
        print('  %5d: %s'%(i+1,l.strip()[:120]))