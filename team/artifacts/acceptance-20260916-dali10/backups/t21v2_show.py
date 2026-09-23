import sys,io,os
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
u=open(os.path.join(d,'implementation-payload-TM600-TM601.cpp'),'rb').read().decode('utf-8-sig')
lines=u.split('\n')
for i,l in enumerate(lines):
    if 'v_meas[site]' in l or 'i_meas[site]' in l or 'rdson[site] =' in l:
        print('%4d |%s|'%(i+1,l.rstrip('\r')))