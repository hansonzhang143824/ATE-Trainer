import sys,io,os,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'implementation-payload-TM600-TM601.cpp')
raw=open(p,'rb').read(); u=raw.decode('utf-8-sig')
code=[l for l in u.split('\n') if not l.strip().startswith('//')]
print('=== artifact integrity ===')
print('bytes',len(raw),'BOM',raw[:3]==b'\xef\xbb\xbf','CRLF',raw.count(b'\r\n'),'loneLF',raw.count(b'\n')-raw.count(b'\r\n'))
print('sha256',hashlib.sha256(raw).hexdigest())
print()
print('=== code-level compliance (ruling b + range fix) ===')
print('delay_ms(1)=%d  delay_ms(2)=%d'%(sum(l.count('delay_ms(1)') for l in code),sum(l.count('delay_ms(2)') for l in code)))
print('SetClamp(50,50)=%d  MeasureVI(200,5,X10)=%d'%(sum(l.count('SetClamp(50, 50)') for l in code),sum(l.count('MeasureVI(200, 5, FPVIe_MV_X10)') for l in code)))
print('FPVIe_10UA=%d  FPVIe_10A=%d  rampfamily=%d'%(sum(l.count('FPVIe_10UA') for l in code),sum(l.count('FPVIe_10A') for l in code),sum(l.count('rampi_capv')+l.count('rampv_capv') for l in code)))
print('functions:',u.count('DUT_API int TM600_HS_RDSON'),u.count('DUT_API int TM601_LS_RDSON'))
print('HARD CAP wording in header:','= 2 ms <= 2 ms HARD CAP  OK' in u)
print('dangling fragment removed:', 'golden form, and the difference is disclosed' not in u)
print()
print('=== settle sequence order (code) ===')
for i,l in enumerate(code):
    if 'MeasureVI(200' in l: print('   ', [x.strip()[:52] for x in code[i-1:i+2]])