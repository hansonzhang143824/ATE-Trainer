import sys,io,os
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
u=open(os.path.join(d,'implementation-payload-TM600-TM601.cpp'),'rb').read().decode('utf-8-sig')
for i,l in enumerate(u.split('\n')):
    if 'delay_ms(2)' in l:
        print('line %d: %s'%(i+1,l.strip()[:170]))
        print('  is comment:',l.strip().startswith('//'))
code=[l for l in u.split('\n') if not l.strip().startswith('//')]
print()
print('delay_ms(2) in EXECUTABLE code:',sum(l.count('delay_ms(2)') for l in code))