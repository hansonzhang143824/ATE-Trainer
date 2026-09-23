import sys,io,os,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
src=os.path.join(d,'implementation-payload-TM600-TM601.cpp')
dst=os.path.join(d,'implementation-payload-TM600-TM601.pulse2ms-variant.cpp')
raw=open(src,'rb').read()
open(dst,'wb').write(raw)
print('created the name the captain references:',os.path.basename(dst))
for p in (src,dst):
    r=open(p,'rb').read()
    print('  %-58s %6d B %s'%(os.path.basename(p),len(r),hashlib.sha256(r).hexdigest()))
print('byte-identical:',open(src,'rb').read()==open(dst,'rb').read())
u=open(dst,'rb').read().decode('utf-8-sig'); code=[l for l in u.split('\n') if not l.strip().startswith('//')]
print()
print('content check on the captain-designated file:')
print('  delay_ms(1) in code:',sum(l.count('delay_ms(1)') for l in code),'| delay_ms(2) in code:',sum(l.count('delay_ms(2)') for l in code))
print('  arithmetic comment:','1 ms + 1 ms = 2 ms <= 2 ms HARD CAP' in u)
print('  deviation labelled:','deliberate deviation' in u.lower())
print('  one-byte write probe (per your request):')
probe=r'D:\PROJECT6-DALI\ForCodexDebug\source\__t13_probe.tmp'
try:
    open(probe,'wb').write(b'x'); print('    WRITE OK'); os.remove(probe); print('    cleaned up')
except Exception as e: print('    DENIED ->',type(e).__name__,e)