import sys,io,hashlib,os
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
p=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10\implementation-payload-TM600-TM601.cpp'
raw=open(p,'rb').read()
print('payload bytes',len(raw),'sha256',hashlib.sha256(raw).hexdigest())
t=raw.decode('utf-8-sig')
print('functions:',t.count('DUT_API int TM600_HS_RDSON'),t.count('DUT_API int TM601_LS_RDSON'))
for tok in ['FPVIe_RELAY_SENSE_ON','FPVIe_CONTACTMODE','FPVIe_HIGH_MV','FPVIe_LOW_MV','FPVIe_100MV']:
    print('  %-24s %d'%(tok,t.count(tok)))
print('code-only check: rampi_capv in CODE (not comments):',
      len([l for l in t.split('\n') if 'rampi_capv' in l and not l.strip().startswith('//')]))
print('FPVIE_RELAY_ON in CODE:',len([l for l in t.split('\n') if 'FPVIE_RELAY_ON' in l and not l.strip().startswith('//')]))