import os,re
SRC=r'D:\PROJECT6-DALI\ForCodexDebug\source'
def L(p):
    t=open(p,'rb').read().decode('utf-8-sig',errors='replace')
    x=t.split('\n'); return [y[:-1] if y.endswith('\r') else y for y in x]
bc=L(os.path.join(SRC,'BoardCheck.cpp'))
print('=== CBC_log::log / test_log definitions in BoardCheck.cpp ===')
for i,l in enumerate(bc):
    if re.search(r'CBC_log::(log|test_log)\s*\(', l):
        print('--- BoardCheck.cpp:%d ---' % (i+1))
        for n in range(i+1, min(len(bc)+1, i+42)):
            print('  %5d| %s' % (n, bc[n-1].rstrip()))
        print('')
print('=== does BoardCheck.* write to the station datalog? (SetTestResult/msLogData/SetTestNumber) ===')
bch=L(os.path.join(SRC,'BoardCheck.h'))
for nm,ls in (('BoardCheck.cpp',bc),('BoardCheck.h',bch)):
    for k in ('SetTestResult','msLogData','SetTestNumber','GetMeasResult'):
        n=len(re.findall(r'\b'+k+r'\b','\n'.join(ls)))
        if n: print('  %-16s %-16s %d' % (nm,k,n))
print()
print('=== what "datalog" means inside BoardCheck.cpp (first 14 hits) ===')
c=0
for i,l in enumerate(bc):
    if re.search(r'(?i)datalog', l):
        print('  %5d| %s' % (i+1, l.strip()[:150])); c+=1
        if c>=14: break
print()
print('=== run_diags definition ===')
dg=L(os.path.join(SRC,'diags.cpp'))
for i,l in enumerate(dg):
    if re.search(r'run_diags', l):
        print('  %5d| %s' % (i+1, l.strip()[:160]))
print()
print('=== diags.cpp 70-100 (the BoardCheck bc; context) ===')
for n in range(70,101):
    print('  %5d| %s' % (n, dg[n-1].rstrip()))
