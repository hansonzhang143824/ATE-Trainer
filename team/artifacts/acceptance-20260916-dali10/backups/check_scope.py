import sys,io,os,hashlib,re
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
u=open(os.path.join(d,'implementation-payload-TM600-TM601.cpp'),'rb').read().decode('utf-8-sig')
code=[l for l in u.split('\n') if not l.strip().startswith('//')]
print('=== does my payload reference anything outside TM600/TM601 scope? (relevant to t18) ===')
for tm in ('TM102','TM103','TM108','TM109','TM000','TM001','TM135','TM1205','TM601','TM600'):
    print('  %-8s %d'%(tm,u.count(tm)))
print()
print('  ATE stimulus values in code:',sorted(set(re.findall(r'Set\(FV, (4\.2|15|9|5|3\.5)',u))))
print('  any 3.5 V in code:', '3.5' in ' '.join(code))
print('  U11 referenced:', u.count('U11'))
print()
print('payload',os.path.getsize(os.path.join(d,'implementation-payload-TM600-TM601.cpp')),'B',hashlib.sha256(open(os.path.join(d,'implementation-payload-TM600-TM601.cpp'),'rb').read()).hexdigest())
s=open(r'D:\PROJECT6-DALI\ForCodexDebug\source\test.cpp','rb').read()
print('target still baseline:',hashlib.sha256(s).hexdigest()=='5c9cb3f9339f6db373afcff7504ef6b34924a4ca3042b5926cb612c819ac3317')