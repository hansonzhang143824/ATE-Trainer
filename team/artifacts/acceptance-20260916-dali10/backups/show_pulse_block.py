import sys,io,os,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'implementation-payload-TM600-TM601.cpp')
u=open(p,'rb').read().decode('utf-8-sig')
lines=u.split('\n')
# show the header pulse block to patch precisely
for i,l in enumerate(lines):
    if 'Pulse width arithmetic' in l or 'delay_ms(2) settle' in l or 'MeasureVI(200, 5) acquisition' in l or 'effective 1 A pulse' in l:
        print('%4d: %s'%(i+1,l.rstrip()[:150]))