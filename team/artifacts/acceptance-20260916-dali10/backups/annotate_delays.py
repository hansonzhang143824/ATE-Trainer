import sys,io,os,hashlib,re
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'implementation-payload-TM600-TM601.cpp')
u=open(p,'rb').read().decode('utf-8-sig')
# annotate the two Step-1 delays and the TM601 Step-3 delay as OUTSIDE the pulse window
old3='    delay_ms(3);'
new3=('    delay_ms(3);  // NOT in the pulse window: power-up relay settle after Step 1, before any force\n'
      '                  // is applied. The 2 ms HARD CAP is judged between force and de-assert only.')
n3=u.count(old3)
u=u.replace(old3,new3)
old5='    delay_ms(5);                             // DFT row context: 5 ms settle before the pulse'
new5=('    delay_ms(5);  // NOT in the pulse window: register/sequence interval BEFORE the force is\n'
      '                  // applied (DFT row context). The 2 ms HARD CAP is judged between the force\n'
      '                  // statement and the de-assert only (1 ms settle + 1 ms acquisition = 2 ms).')
n5=u.count(old5)
u=u.replace(old5,new5)
open(p,'wb').write(b'\xef\xbb\xbf'+u.replace('\r\n','\n').replace('\n','\r\n').encode('utf-8'))
r=open(p,'rb').read(); v=r.decode('utf-8-sig'); code=[l for l in v.split('\n') if not l.strip().startswith('//')]
print('annotated delay_ms(3) x%d and the TM600/TM601 Step-3 delay x%d'%(n3,n5))
print('payload %d B BOM=%s CRLF=%d loneLF=%d'%(len(r),r[:3]==b'\xef\xbb\xbf',r.count(b'\r\n'),r.count(b'\n')-r.count(b'\r\n')))
print('sha256',hashlib.sha256(r).hexdigest())
print('code delay_ms(1)=%d delay_ms(2)=%d delay_ms(3)=%d delay_ms(5)=%d'%(
 sum(l.count('delay_ms(1)') for l in code),sum(l.count('delay_ms(2)') for l in code),
 sum(l.count('delay_ms(3)') for l in code),sum(l.count('delay_ms(5)') for l in code)))
print('pulse-window note present:','NOT in the pulse window' in v)
print('clamp stricter-than-golden present:','STRICTER THAN THE GOLDEN' in v)