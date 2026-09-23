import sys,io,os,json,re
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
base=r'D:\Newtest\DSH\ATE-Coding-Plat'
J=json.loads(open(os.path.join(base,'team','artifacts','acceptance-20260916-dali10','setup-contract.json'),'rb').read().decode('utf-8-sig'))
d=os.path.join(base,'team','artifacts','acceptance-20260916-dali10')
u=open(os.path.join(d,'implementation-payload-TM600-TM601.cpp'),'rb').read().decode('utf-8-sig')
code=[l for l in u.split('\n') if not l.strip().startswith('//')]
src=open(r'D:\PROJECT6-DALI\ForCodexDebug\source\test.cpp','rb').read().decode('utf-8-sig')
t600=[l for l in code if 'cbite.SetOn(' in l]
print('=== (1) what the payload ACTUALLY closes, both items ===')
for l in t600: print('   ',l.strip()[:170])
print()
def tok(n): return True
print('=== (2) exposure matrix: relay required by which route vs closed in payload ===')
c=' '.join(t600)
for r,nm in [(48,'K48'),(76,'K76'),(46,'K46'),(61,'K61'),(109,'K109'),(110,'K110')]:
    print('   %-6s closed in payload: %s'%(nm, nm in c))
print()
print('=== (3) relaySet membership (contract authority per item) ===')
for tm in ('TM600','TM601'):
    rs=J['tmDeltas'][tm].get('relaySet') or []
    print('   %s: 48=%s 76=%s 46=%s 109=%s 110=%s'%(tm,48 in rs,76 in rs,46 in rs,109 in rs,110 in rs))
print()
print('=== (4) where 48/76 appear in the DEPLOYED tree (context) ===')
for m in list(re.finditer(r'\bK(?:48|76)[A-Za-z0-9_]*',src))[:12]:
    ln=src[:m.start()].count('\n')+1
    line=src.split('\n')[ln-1].strip()
    print('   L%-6d %s'%(ln,line[:110]))