import sys,io,os,re
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
base=r'D:\Newtest\DSH\ATE-Coding-Plat'
sd=os.path.join(base,'scripts')
print('=== 1) THE PREDICATE DIFFERENCE: my broad scan vs their narrow one ===')
broad=[]; narrow=[]
for f in sorted(os.listdir(sd)):
    if not f.endswith('.py'): continue
    t=open(os.path.join(sd,f),encoding='utf-8-sig',errors='replace').read().split('\n')
    for i,l in enumerate(t):
        if re.search(r'\)\s*-\s*',l) and re.search(r'len\(|count\(|sum\(',l):
            broad.append((f,i+1,l.strip()[:110]))
        if re.search(r'len\([^)]*\)\s*-\s*len\([^)]*\)',l) or re.search(r'count\([^)]*\)\s*-[^=]*count\(',l):
            narrow.append((f,i+1,l.strip()[:110]))
print('  BROAD predicate (len/count/sum present AND a subtraction): %d lines'%len(broad))
for f,ln,l in broad: print('     %-30s L%-4d %s'%(f,ln,l))
print()
print('  NARROW predicate (len(x) - len(y) or count - count): %d lines'%len(narrow))
for f,ln,l in narrow: print('     %-30s L%-4d %s'%(f,ln,l))
print()
print('  => their claim (2 narrow) reproduces; my "6" used the broader predicate.')
print()
print('=== 2) THE THREE GATES: any subtraction at all? ===')
for g in ['verify_relay_trace.py','verify_bst_sw_sequence.py','verify_awg_params.py']:
    p=os.path.join(sd,g)
    t=open(p,encoding='utf-8-sig',errors='replace').read().split('\n')
    hits=[(i+1,l.strip()) for i,l in enumerate(t) if re.search(r'\)\s*-\s*',l) and re.search(r'len\(|count\(|sum\(',l)]
    print('  %-30s candidate lines: %d'%(g,len(hits)))
    for ln,l in hits: print('     L%-4d %s'%(ln,l[:105]))