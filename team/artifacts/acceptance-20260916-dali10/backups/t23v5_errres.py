import sys,io,os,re,glob
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
src=r'D:\PROJECT6-DALI\ForCodexDebug\source'
t=open(os.path.join(src,'test.cpp'),'rb').read().decode('utf-8-sig')
print('=== test.cpp includes ===')
for i,l in enumerate(t.split('\n')[:40]):
    if l.strip().startswith('#include'): print('  %2d: %s'%(i+1,l.strip()))
print()
print('ERROR_RES in ForCodexDebug test.cpp:',t.count('ERROR_RES'))
print()
print('=== is Test_Method.h in the debug tree or its include path? ===')
for f in glob.glob(os.path.join(src,'*.h')):
    n=os.path.basename(f)
    if 'Method' in n: print('  found:',n)
h=os.path.join(src,'Test_Method.h')
print('  Test_Method.h in source/:',os.path.exists(h))
if os.path.exists(h):
    for i,l in enumerate(open(h,'rb').read().decode('utf-8-sig',errors='replace').split('\n')):
        if 'ERROR_RES' in l: print('    %4d: %s'%(i+1,l.strip()[:110]))
print()
print('=== StdAfx.h include chain mention of Test_Method ===')
sa=open(os.path.join(src,'StdAfx.h'),'rb').read().decode('utf-8-sig',errors='replace')
for i,l in enumerate(sa.split('\n')):
    if 'TestMethod' in l or 'Test_Method' in l: print('  StdAfx.h %4d: %s'%(i+1,l.strip()[:110]))
print()
print('=== other TMs that use ERROR_RES in target ===')
for i,l in enumerate(t.split('\n')):
    if 'ERROR_RES' in l: print('  test.cpp %4d: %s'%(i+1,l.strip()[:110]))