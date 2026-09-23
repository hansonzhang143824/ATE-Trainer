import sys,io,os,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
p=r'D:\Newtest\DSH\ATE-Coding-Plat\knowledge\hardware\relays.md'
print('exists:',os.path.exists(p))
if os.path.exists(p):
    L=open(p,'rb').read().decode('utf-8-sig',errors='replace').split('\n')
    print('=== L1-34 (verify the G6K-2G-Y terminal assignment I cited) ===')
    for i in range(0,min(34,len(L))): print('%4d| %s'%(i+1,L[i].rstrip()[:130]))