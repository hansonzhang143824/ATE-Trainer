import os, difflib, json
BASE = r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\tm108-v2-trial'
def load(p):
    b=open(p,'rb').read(); t=b.decode('utf-8-sig'); r=t.split('\n')
    L=[x[:-1] if x.endswith('\r') else x for x in r]
    if L and L[-1]=='': L=L[:-1]
    return L
A=load(os.path.join(BASE,'review','copy','test.cpp'))
B=load(os.path.join(BASE,'implementation','backup','tm108-v2-impl__test.cpp.before'))
for n in (0,1,2,3,5,10):
    d=list(difflib.unified_diff(B,A,lineterm='',n=n))
    hunks=[x for x in d if x.startswith('@@')]
    print('unified_diff n=%d -> hunks=%d' % (n,len(hunks)))
    if n==3:
        for h in hunks: print('   ',h)
print()
print('minimal changed before-range and after-range:')
sm=difflib.SequenceMatcher(None,B,A,autojunk=False)
ops=[o for o in sm.get_opcodes() if o[0]!='equal']
print('  before changed lines: %d..%d' % (min(o[1] for o in ops)+1, max(o[2] for o in ops)))
print('  after  changed lines: %d..%d' % (min(o[3] for o in ops)+1, max(o[4] for o in ops)))
