import sys,io,os,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'implementation-payload-TM600-TM601.cpp')
raw=open(p,'rb').read()
if raw[:3]!=b'\xef\xbb\xbf':
    open(p,'wb').write(b'\xef\xbb\xbf'+raw); print('BOM restored')
raw=open(p,'rb').read()
t=raw.decode('utf-8-sig')
if raw.count(b'\n')-raw.count(b'\r\n')!=0:
    open(p,'wb').write(b'\xef\xbb\xbf'+t.replace('\r\n','\n').replace('\n','\r\n').encode('utf-8')); print('line endings normalised')
raw=open(p,'rb').read()
u=raw.decode('utf-8-sig'); code=[l for l in u.split('\n') if not l.strip().startswith('//')]
print('FINAL payload: %d B  BOM=%s  CRLF=%d  loneLF=%d'%(len(raw),raw[:3]==b'\xef\xbb\xbf',raw.count(b'\r\n'),raw.count(b'\n')-raw.count(b'\r\n')))
print('FINAL sha256:',hashlib.sha256(raw).hexdigest())
print('code: delay_ms(1)=%d delay_ms(2)=%d | FPVIe_10UA=%d FPVIe_10A=%d | SetClamp=%d | MeasureVI=%d | ramp=%d'%(
 sum(l.count('delay_ms(1)') for l in code),sum(l.count('delay_ms(2)') for l in code),
 sum(l.count('FPVIe_10UA') for l in code),sum(l.count('FPVIe_10A') for l in code),
 sum(l.count('SetClamp(50, 50)') for l in code),sum(l.count('MeasureVI(200, 5, FPVIe_MV_X10)') for l in code),
 sum(l.count('rampi_capv')+l.count('rampv_capv') for l in code)))
# target untouched
s=open(r'D:\PROJECT6-DALI\ForCodexDebug\source\test.cpp','rb').read()
print()
print('target test.cpp:',len(s),'B',hashlib.sha256(s).hexdigest())
print('baseline intact:',hashlib.sha256(s).hexdigest()=='5c9cb3f9339f6db373afcff7504ef6b34924a4ca3042b5926cb612c819ac3317')