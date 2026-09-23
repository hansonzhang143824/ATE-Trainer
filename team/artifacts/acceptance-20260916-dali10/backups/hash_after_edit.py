import sys,io,hashlib,os
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
for n in ['implementation-payload-TM600-TM601.cpp','implementation-payload-TM600-TM601.pulse2ms-variant.cpp']:
    p=os.path.join(d,n); raw=open(p,'rb').read()
    print('%-58s %6d B %s'%(n,len(raw),hashlib.sha256(raw).hexdigest()))
t=open(os.path.join(d,'implementation-payload-TM600-TM601.cpp'),'rb').read().decode('utf-8-sig')
print('clamp-trigger semantics present:','CLAMP-TRIGGER SEMANTICS' in t)
print('alternative-not-adopted present:','ALTERNATIVE NOT ADOPTED' in t)
print('sample provenance present:','MEASUREMENT-SAMPLE PROVENANCE' in t)