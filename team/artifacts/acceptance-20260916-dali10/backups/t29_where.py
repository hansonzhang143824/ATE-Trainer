import sys,io,os,re
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
p=r'D:\PROJECT6-DALI\ForCodexDebug\source\test.cpp'
L=open(p,'rb').read().decode('utf-8-sig').split('\n')
for sym in ['TM600_HS_RDSON','TM601_LS_RDSON','K126_V1P5_CAP']:
    print('=== %s ==='%sym)
    for i,l in enumerate(L):
        if sym in l: print('  L%-6d %s'%(i+1,l.strip()[:120]))
    print()