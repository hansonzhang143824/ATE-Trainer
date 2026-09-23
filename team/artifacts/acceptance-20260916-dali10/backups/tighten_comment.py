import sys,io,os,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'implementation-payload-TM600-TM601.cpp')
u=open(p,'rb').read().decode('utf-8-sig')
print('=== current settle line (code) ===')
for i,l in enumerate(u.split('\n')):
    if l.strip().startswith('delay_ms(1);  // PULSE'): print('  %d: %s'%(i+1,l.strip()[:190]))
print()
print('delay_ms(2) present:',u.count('delay_ms(2)'))
old='    delay_ms(1);  // PULSE ARITHMETIC: settle 1 ms + acquisition 200 x 5 us = 1 ms => total 2 ms <= 2 ms HARD CAP (user ruling). Settle reduced from the golden 2 ms: INTENTIONAL DEVIATION, taken because the user states the cap as a HARD CAP bounding the whole 1 A force duration (thermal/stress limit) whereas the golden form is itself ~3 ms.'
new=('    delay_ms(1);  // 1 ms + 1 ms = 2 ms <= 2 ms HARD CAP (user ruling)\n'
     '                  // settlement 1 ms + acquisition 200 x 5 us = 1 ms => the WHOLE 1 A force duration\n'
     '                  // (settle + acquisition) is within the user-stated HARD CAP, whose purpose is to limit\n'
     '                  // DUT/relay thermal and stress. deliberate deviation: golden used delay_us(2000) and the\n'
     '                  // golden form is itself ~3 ms; an explicit hard cap governs over a precedent form.')
n=u.count(old)
print('exact-form comment present:',n==2)
if n==2:
    u=u.replace(old,new)
    open(p,'wb').write(b'\xef\xbb\xbf'+(u.replace('\r\n','\n').replace('\n','\r\n')).encode('utf-8'))
raw=open(p,'rb').read(); v=raw.decode('utf-8-sig'); code=[l for l in v.split('\n') if not l.strip().startswith('//')]
print()
print('payload %d B BOM=%s loneLF=%d'%(len(raw),raw[:3]==b'\xef\xbb\xbf',raw.count(b'\n')-raw.count(b'\r\n')))
print('sha256',hashlib.sha256(raw).hexdigest())
print('code checks: delay_ms(1)=%d delay_ms(2)=%d SetClamp=%d MeasureVI(200,5,X10)=%d FPVIe_10UA=%d FPVIe_10A=%d'%(
 sum(l.count('delay_ms(1)') for l in code),sum(l.count('delay_ms(2)') for l in code),
 sum(l.count('SetClamp(50, 50)') for l in code),sum(l.count('MeasureVI(200, 5, FPVIe_MV_X10)') for l in code),
 sum(l.count('FPVIe_10UA') for l in code),sum(l.count('FPVIe_10A') for l in code)))
print('HARD CAP wording present:','HARD CAP (user ruling)' in v)