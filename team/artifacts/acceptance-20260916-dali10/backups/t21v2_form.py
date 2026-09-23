import sys,io,os,re
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
p=r'D:\PROJECT6-DALI\ForCodexDebug\source\test.cpp'
t=open(p,'rb').read().decode('utf-8-sig')
print('=== SetTestResult call forms (arity, 2nd arg) ===')
forms={}
for m in re.finditer(r'SetTestResult\(([^;]*)\)',t):
    a=[x.strip() for x in m.group(1).split(',')]
    key=(len(a),(a[1][:30] if len(a)>1 else ''))
    forms[key]=forms.get(key,0)+1
for k,v in sorted(forms.items(),key=lambda x:-x[1])[:12]:
    print('  args=%d  second=%-32s x%d'%(k[0],k[1],v))