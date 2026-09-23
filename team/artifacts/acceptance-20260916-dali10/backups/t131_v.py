import sys,io,re
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
KW={'return','yield','raise','else','in','not','and','or','lambda','assert','del','pass','elif','while','if'}
def v1(s):
    return len(re.findall(r'(?<=[\w\)\]])\s*-(?!>)',s))
def v3(s):
    # v3 = identifier-shaped-or-closing left operand + keyword guard + arrow guard
    hits=0
    for m in re.finditer(r'(?<=[\w\)\]])\s*-(?!>)',s):
        seg=s[:m.start()].rstrip()
        w=re.search(r'[A-Za-z_]\w*$',seg)
        if w and w.group(0) in KW: continue
        hits+=1
    return hits
cases=[('len(a) - len(b)',1),('x-y',1),('(a)-b',1),('arr[i]-b',1),('errors) -> None',0),
       ('f(-a)',0),('a*-b',0),('-x',0),('return -x',0),('a - -b',1),('x = a - -1',1)]
print('=== THEIR v1 vs v3 against the 11-case witness set ===')
o1=o3=0
for s,want in cases:
    a,b=v1(s),v3(s)
    ok1='OK' if a==want else 'FAIL'; ok3='OK' if b==want else 'FAIL'
    if a==want:o1+=1
    if b==want:o3+=1
    print('  %-18r want=%d v1=%d %-4s v3=%d %-4s'%(s,want,a,ok1,b,ok3))
print()
print('  v1: %d/%d   v3: %d/%d'%(o1,len(cases),o3,len(cases)))