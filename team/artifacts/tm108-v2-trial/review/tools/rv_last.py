import os,re,hashlib
ROOT=r'D:\PROJECT6-DALI\ForCodexDebug'
SRC=os.path.join(ROOT,'source')
def rb(p): return open(p,'rb').read()
print('=== any definition of CBC_log:: members anywhere in the tree ===')
hit=0
for dp,dn,fn in os.walk(SRC):
    for f in fn:
        if not f.lower().endswith(('.cpp','.h','.hpp')): continue
        fp=os.path.join(dp,f)
        t=rb(fp).decode('utf-8-sig',errors='replace')
        for i,l in enumerate(t.split('\n')):
            if re.search(r'CBC_log\s*::', l):
                print('  %s:%d| %s' % (os.path.relpath(fp,ROOT), i+1, l.strip()[:140])); hit+=1
print('  total CBC_log:: occurrences (definitions or qualified uses): %d' % hit)
print()
print('=== worklist hashes (final, plaintext, python byte mode) ===')
files=[r'D:\PROJECT6-DALI\ForCodexDebug\source\test.cpp',
 r'D:\PROJECT6-DALI\ForCodexDebug\source\BoardCheck.h',
 r'D:\PROJECT6-DALI\ForCodexDebug\source\treg.h',
 r'D:\PROJECT6-DALI\ForCodexDebug\source\src\treg.h',
 r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\tm108-v2-trial\implementation\backup\tm108-v2-impl__test.cpp.before']
for p in files:
    b=rb(p); print('  %-70s %d %s' % (os.path.basename(p), len(b), hashlib.sha256(b).hexdigest()))
