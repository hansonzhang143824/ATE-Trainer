import sys,io,os,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
for n in ['implementation-payload-TM600-TM601.cpp','implementation-payload-TM600-TM601.pulse2ms-variant.cpp']:
    p=os.path.join(d,n)
    t=open(p,'rb').read().decode('utf-8-sig')
    t=t.replace('\r\n','\n').replace('\r','\n')      # normalise
    out=b'\xef\xbb\xbf'+t.replace('\n','\r\n').encode('utf-8')
    open(p,'wb').write(out)
    r=open(p,'rb').read()
    print('%-58s %6d B BOM=%s CRLF=%d loneLF=%d'%(n,len(r),r[:3]==b'\xef\xbb\xbf',r.count(b'\r\n'),r.count(b'\n')-r.count(b'\r\n')))
    print('    sha256',hashlib.sha256(r).hexdigest())