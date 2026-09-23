import sys,io,os,json,re,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
u=open(os.path.join(d,'implementation-payload-TM600-TM601.cpp'),'rb').read().decode('utf-8-sig')
print('=== negative-list wording in the payload ===')
for i,l in enumerate(u.split('\n')):
    if 'NEGATIVE LIST' in l or 'never be actuated' in l or 'must NOT appear' in l:
        print('  %4d| %s'%(i+1,l.strip()[:120]))
print()
print('=== teardown order evidence in payload (code) ===')
code=[l for l in u.split('\n') if not l.strip().startswith('//')]
seq=[]
for l in code:
    if 'RELAY_OFF' in l: seq.append(l.split('.Set')[0].strip())
print('  RELAY_OFF order across file:',seq)
print()
print("=== does the plan mention 10UA / minimal compliant (t4's gap claim)? ===")
P=json.loads(open(os.path.join(d,'test-plan.json'),'rb').read().decode('utf-8-sig'))
s=json.dumps(P,ensure_ascii=False)
for k in ['10UA','minimal compliant','FPVIe_10UA','zero-init','initialization range']:
    print('  %-22s %d occurrence(s)'%(k,s.count(k)))
print()
print('payload:',len(open(os.path.join(d,'implementation-payload-TM600-TM601.cpp'),'rb').read()),'B')