import sys,io,os,re
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
base=r'D:\Newtest\DSH\ATE-Coding-Plat'
# 1) ERROR_RES in Test_Method.h
h=os.path.join(base,'debug','source','Test_Method.h')
if not os.path.exists(h): h=os.path.join(base,'source','Test_Method.h')
print('Test_Method.h path:',h,'exists:',os.path.exists(h))
if os.path.exists(h):
    for i,l in enumerate(open(h,'rb').read().decode('utf-8-sig',errors='replace').split('\n')):
        if 'ERROR_RES' in l: print('  %4d: %s'%(i+1,l.strip()[:120]))
# search wider
import glob
if not os.path.exists(h):
    for f in glob.glob(os.path.join(base,'**','Test_Method.h'),recursive=True):
        print('  found elsewhere:',f)
        for i,l in enumerate(open(f,'rb').read().decode('utf-8-sig',errors='replace').split('\n')):
            if 'ERROR_RES' in l: print('    %4d: %s'%(i+1,l.strip()[:120]))
print()
# 2) the precedent at test.cpp:8087-8090
p=os.path.join(r'D:\PROJECT6-DALI\ForCodexDebug','source','test.cpp')
t=open(p,'rb').read().decode('utf-8-sig',errors='replace').split('\n')
print('=== test.cpp 8080-8095 (precedent) ===')
for i in range(8079,8095):
    if i<len(t): print('%4d: %s'%(i+1,t[i].rstrip()[:135]))
print()
print('=== does the target use ERROR_RES anywhere? ===')
n=sum(1 for l in t if 'ERROR_RES' in l)
print('  ERROR_RES occurrences in test.cpp:',n)
for i,l in enumerate(t):
    if 'ERROR_RES' in l and i<8100: print('  %4d: %s'%(i+1,l.strip()[:120]))