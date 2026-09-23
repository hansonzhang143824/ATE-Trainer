import sys,io,os,hashlib,re
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'implementation-payload-TM600-TM601.cpp')
t=open(p,'rb').read().decode('utf-8-sig')
old='    delay_ms(2);                                             // settle per the golden'
new='    delay_ms(1);  // PULSE ARITHMETIC: settle 1 ms + acquisition 200 x 5 us = 1 ms => total 2 ms <= 2 ms HARD CAP (user ruling). Settle reduced from the golden 2 ms: INTENTIONAL DEVIATION, taken because the user states the cap as a HARD CAP bounding the whole 1 A force duration (thermal/stress limit) whereas the golden form is itself ~3 ms.'
n=t.count(old)
print('settle lines found:',n)
if n!=2: print('UNEXPECTED COUNT'); 
t=t.replace(old,new)
open(p,'wb').write(b'\xef\xbb\xbf'+(t.replace('\r\n','\n').replace('\n','\r\n')).encode('utf-8'))
raw=open(p,'rb').read(); u=raw.decode('utf-8-sig')
code=[l for l in u.split('\n') if not l.strip().startswith('//')]
print('payload',len(raw),'B BOM',raw[:3]==b'\xef\xbb\xbf','loneLF',raw.count(b'\n')-raw.count(b'\r\n'))
print('sha256',hashlib.sha256(raw).hexdigest())
print('code delay_ms(1)=%d delay_ms(2)=%d'%(sum(l.count('delay_ms(1)') for l in code),sum(l.count('delay_ms(2)') for l in code)))
print('PULSE ARITHMETIC in code comment:', 'PULSE ARITHMETIC' in u)
# the variant is now identical in intent -> delete it to avoid two contradictory copies
dst=os.path.join(d,'implementation-payload-TM600-TM601.pulse2ms-variant.cpp')
if os.path.exists(dst):
    v=open(dst,'rb').read().decode('utf-8-sig')
    print('variant still has delay_ms(1) settle:', 'settle shortened' in v, '| differs from payload now:', v.replace('settle shortened','')!=u)
# verify the measure sequence order in code
for i,l in enumerate(code):
    if 'MeasureVI(200' in l:
        print('  context:',[x.strip()[:58] for x in code[i-1:i+2]])