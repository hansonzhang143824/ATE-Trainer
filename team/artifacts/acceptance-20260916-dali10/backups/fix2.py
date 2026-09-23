import sys,io,os,hashlib,re
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
for n in ['implementation-payload-TM600-TM601.cpp','implementation-payload-TM600-TM601.pulse2ms-variant.cpp']:
    p=os.path.join(d,n)
    t=open(p,'rb').read().decode('utf-8-sig')
    t=t.replace('\r\n','\n').replace('\r','\n')
    open(p,'wb').write(b'\xef\xbb\xbf'+t.replace('\n','\r\n').encode('utf-8'))
    r=open(p,'rb').read(); u=r.decode('utf-8-sig')
    code=[l for l in u.split('\n') if not l.strip().startswith('//')]
    print('%-58s %6d B BOM=%s CRLF=%d loneLF=%d'%(n,len(r),r[:3]==b'\xef\xbb\xbf',r.count(b'\r\n'),r.count(b'\n')-r.count(b'\r\n')))
    print('    sha256',hashlib.sha256(r).hexdigest())
    print('    code FPVIe_10UA=%d FPVIe_10A=%d SetClamp=%d delay_ms(2)=%d delay_ms(1)=%d MeasureVI(200,5,X10)=%d'%(
        sum(l.count('FPVIe_10UA') for l in code),sum(l.count('FPVIe_10A') for l in code),
        sum(l.count('SetClamp(50, 50)') for l in code),sum(l.count('delay_ms(2)') for l in code),
        sum(l.count('delay_ms(1)') for l in code),sum(l.count('MeasureVI(200, 5, FPVIe_MV_X10)') for l in code)))