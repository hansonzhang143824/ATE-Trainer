import sys,io,os,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'implementation-payload-TM600-TM601.cpp')
u=open(p,'rb').read().decode('utf-8-sig')
old=('//     delay_ms(2) settle                      = 2.000 ms\n'
     '//     MeasureVI(200, 5) acquisition           = 200 x 5 us = 1.000 ms   (MEAS_NORMAL\n'
     '//                                               completes inside the call, so it adds time)\n'
     '//     -> effective 1 A pulse                  ~ 3 ms\n')
new=('//     AS DELIVERED (captain ruling (b)): settle delay_ms(1) = 1.000 ms\n'
     '//     MeasureVI(200, 5) acquisition           = 200 x 5 us = 1.000 ms   (MEAS_NORMAL\n'
     '//                                               completes inside the call, so it adds time)\n'
     '//     -> effective 1 A pulse                  = 2 ms <= 2 ms HARD CAP  OK\n'
     '//     (superseded reading: with the golden 2 ms settle the same arithmetic gave ~3 ms.)\n')
n=u.count(old)
print('block found:',n==1)
if n==1:
    u=u.replace(old,new)
    open(p,'wb').write(b'\xef\xbb\xbf'+(u.replace('\r\n','\n').replace('\n','\r\n')).encode('utf-8'))
raw=open(p,'rb').read(); v=raw.decode('utf-8-sig')
code=[l for l in v.split('\n') if not l.strip().startswith('//')]
print('payload %d B loneLF=%d'%(len(raw),raw.count(b'\n')-raw.count(b'\r\n')))
print('sha256',hashlib.sha256(raw).hexdigest())
print('code: delay_ms(1)=%d delay_ms(2)=%d SetClamp=%d MeasureVI(200,5,X10)=%d FPVIe_10UA=%d FPVIe_10A=%d rampfamily=%d'%(
 sum(l.count('delay_ms(1)') for l in code),sum(l.count('delay_ms(2)') for l in code),
 sum(l.count('SetClamp(50, 50)') for l in code),sum(l.count('MeasureVI(200, 5, FPVIe_MV_X10)') for l in code),
 sum(l.count('FPVIe_10UA') for l in code),sum(l.count('FPVIe_10A') for l in code),
 sum(l.count('rampi_capv')+l.count('rampv_capv') for l in code)))
print('header now says 2 ms OK:','= 2 ms <= 2 ms HARD CAP  OK' in v)