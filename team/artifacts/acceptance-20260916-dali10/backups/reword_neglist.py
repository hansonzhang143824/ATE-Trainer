import sys,io,os,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'implementation-payload-TM600-TM601.cpp')
u=open(p,'rb').read().decode('utf-8-sig')
old='//   * v5 NEGATIVE LIST honoured: relays 87, 88, 89, 90, 91 (local-sense cross-shorts, sense-float,'
i=u.find(old)
if i>0:
    j=u.find('\n',u.find('must NOT appear',i) if 'must NOT appear' in u[i:i+400] else i)
    print('current header line(s):'); print(u[i:i+300])
    u=u.replace(old,'//   * NEGATIVE LIST (verifiable form): relays 87, 88, 89, 90, 91 must NOT appear in the')
    print('header reworded')
raw=b'\xef\xbb\xbf'+u.replace('\r\n','\n').replace('\n','\r\n').encode('utf-8')
open(p,'wb').write(raw)
r=open(p,'rb').read(); v=r.decode('utf-8-sig'); code=[l for l in v.split('\n') if not l.strip().startswith('//')]
print()
print('payload %d B BOM=%s CRLF=%d loneLF=%d'%(len(r),r[:3]==b'\xef\xbb\xbf',r.count(b'\r\n'),r.count(b'\n')-r.count(b'\r\n')))
print('sha256',hashlib.sha256(r).hexdigest())
print('code delay_ms(1)=%d delay_ms(2)=%d'%(sum(l.count('delay_ms(1)') for l in code),sum(l.count('delay_ms(2)') for l in code)))
print('required-on wording present:','required-on (SetOn) set' in v)
print('not-a-conflict note present:','NOT A CONFLICT' in v)