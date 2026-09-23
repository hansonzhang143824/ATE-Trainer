import sys,io,os,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'implementation-payload-TM600-TM601.cpp')
raw=open(p,'rb').read()
print('before: bytes',len(raw),'BOM',raw[:3]==b'\xef\xbb\xbf','starts',raw[:12])
if raw[:3]!=b'\xef\xbb\xbf':
    open(p,'wb').write(b'\xef\xbb\xbf'+raw)
raw2=open(p,'rb').read()
print('after : bytes',len(raw2),'BOM',raw2[:3]==b'\xef\xbb\xbf','sha256',hashlib.sha256(raw2).hexdigest())
# verify CRLF integrity and code-level compliance once more
t=raw2.decode('utf-8-sig')
print('CRLF count',raw2.count(b'\r\n'),'lone LF',raw2.count(b'\n')-raw2.count(b'\r\n'))
code=[l for l in t.split('\n') if not l.strip().startswith('//')]
for tok in ['FPVIe_RELAY_SENSE_ON','FPVIe_CONTACTMODE','FPVIe_HIGH_MV','FPVIe_LOW_MV','rampi_capv','rampv_capv']:
    print('  code %-24s %d'%(tok,sum(l.count(tok) for l in code)))
print('  code SetClamp:',sum(1 for l in code if 'SetClamp(50, 50)' in l))
print('  functions:',t.count('DUT_API int TM600_HS_RDSON'),t.count('DUT_API int TM601_LS_RDSON'))