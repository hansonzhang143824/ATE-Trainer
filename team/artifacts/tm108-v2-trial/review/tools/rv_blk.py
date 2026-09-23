import os,re
SRC=r'D:\PROJECT6-DALI\ForCodexDebug\source'
def L(p):
    t=open(p,'rb').read().decode('utf-8-sig',errors='replace')
    x=t.split('\n'); return [y[:-1] if y.endswith('\r') else y for y in x]
tl=L(os.path.join(SRC,'test.cpp'))
print('=== test.cpp 790-905 : the DO_BoardCheck block ===')
for n in range(790,906):
    print('  %5d| %s' % (n, tl[n-1].rstrip()))
