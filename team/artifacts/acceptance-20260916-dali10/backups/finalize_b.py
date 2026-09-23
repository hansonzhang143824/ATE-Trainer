import sys,io,os,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'implementation-payload-TM600-TM601.cpp')
t=open(p,'rb').read().decode('utf-8-sig')
anchor='// ============================ FINAL USER RULING (binding) ============================'
add=('// CAPTAIN RULING (b) APPLIED - settle reduced to 1 ms.\n'
     '//   The user states the 1 A pulse limit as a HARD CAP on the whole force duration; the golden form\n'
     '//   (delay_us(2000) then MeasureVI) is itself ~3 ms, so the precedent form and the explicit cap\n'
     '//   conflict. Ruling: the explicit cap governs, precedent supplies structure only. Reduction is the\n'
     '//   safe direction (shorter stress); exceeding the cap is the dangerous one.\n'
     '//   Result: settle 1 ms + acquisition 200 x 5 us = 1 ms => total 2 ms <= 2 ms HARD CAP.\n'
     '//   This is an INTENTIONAL DEVIATION from the golden 2 ms settle and is annotated as such in code.\n'
     '//   Superseded artefact: implementation-payload-TM600-TM601.pulse2ms-variant.cpp (removed - the\n'
     '//   delivered payload now IS the pulse-compliant form, so a second copy would only risk divergence).\n')
if t.count(anchor)==1:
    t=t.replace(anchor, add+anchor)
    print('header note inserted')
open(p,'wb').write(b'\xef\xbb\xbf'+(t.replace('\r\n','\n').replace('\n','\r\n')).encode('utf-8'))
dst=os.path.join(d,'implementation-payload-TM600-TM601.pulse2ms-variant.cpp')
if os.path.exists(dst): os.remove(dst); print('removed redundant variant')
for n in ['implementation-payload-TM600-TM601.cpp','implementation-payload-TM600-TM601.pulse2ms-variant.cpp','backups/test.cpp.before_TM600_TM601.bak']:
    q=os.path.join(d,n)
    if os.path.exists(q):
        r=open(q,'rb').read(); print('  %-58s %6d B %s'%(n,len(r),hashlib.sha256(r).hexdigest()))
    else: print('  %-58s (removed)'%n)
u=open(p,'rb').read().decode('utf-8-sig'); code=[l for l in u.split('\n') if not l.strip().startswith('//')]
print()
print('code: delay_ms(1)=%d delay_ms(2)=%d SetClamp=%d MeasureVI(200,5,X10)=%d FPVIe_10UA=%d FPVIe_10A=%d'%(
 sum(l.count('delay_ms(1)') for l in code),sum(l.count('delay_ms(2)') for l in code),
 sum(l.count('SetClamp(50, 50)') for l in code),sum(l.count('MeasureVI(200, 5, FPVIe_MV_X10)') for l in code),
 sum(l.count('FPVIe_10UA') for l in code),sum(l.count('FPVIe_10A') for l in code)))