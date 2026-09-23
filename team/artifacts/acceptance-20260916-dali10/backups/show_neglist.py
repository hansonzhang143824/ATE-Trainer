import sys,io,os,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'implementation-payload-TM600-TM601.cpp')
u=open(p,'rb').read().decode('utf-8-sig')
old='    // EXPLICIT NEGATIVE LIST (must never be actuated here): relays 87, 88, 89, 90, 91 - the\n'
i=u.find(old)
print('old comment found at',i)
print(u[i:i+420] if i>0 else '(not found)')