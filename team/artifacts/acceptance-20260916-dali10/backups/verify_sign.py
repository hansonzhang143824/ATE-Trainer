import sys,io,os,hashlib,re
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
src=os.path.join(d,'implementation-payload-TM600-TM601.cpp')
u=open(src,'rb').read().decode('utf-8-sig'); code=[l for l in u.split('\n') if not l.strip().startswith('//')]
print('=== contract-required relay state check (code) ===')
for tok in ['K92','K93','K141','K142','K90','K91','K82','K87','K88','K89']:
    n=sum(l.count(tok) for l in code); print('  %-6s in code: %d'%(tok,n))
print()
print('  SetOn relay set TM600:',re.search(r'cbite\.SetOn\((.*?)\);',u,re.S).group(1)[:120])
print('  SetOn relay set TM601:',re.findall(r'cbite\.SetOn\((.*?)\);',u,re.S)[1][:120])
print()
print('=== sign derivation comment present ===', 'signConventionFinding step3' in u, '| U11 noted:', 'U11' in u)
# sync the second (captain-named) file
dst=os.path.join(d,'implementation-payload-TM600-TM601.pulse2ms-variant.cpp')
raw=open(src,'rb').read(); open(dst,'wb').write(raw)
for p in (src,dst):
    r=open(p,'rb').read(); print('%-58s %6d B %s'%(os.path.basename(p),len(r),hashlib.sha256(r).hexdigest()))