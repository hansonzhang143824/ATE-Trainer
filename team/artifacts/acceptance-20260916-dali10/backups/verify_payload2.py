import sys,io,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
p=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10\implementation-payload-TM600-TM601.cpp'
raw=open(p,'rb').read()
t=raw.decode('utf-8-sig')
print('payload bytes',len(raw),'sha256',hashlib.sha256(raw).hexdigest())
print('functions:',t.count('DUT_API int TM600_HS_RDSON'),t.count('DUT_API int TM601_LS_RDSON'))
print('boundary sentence present:','本次交付＝debug 代码生成与编译闭环' in t)
print('U9 present:','U9  whether plain FPVIe_RELAY_ON' in t)
# code-level compliance again
def code_lines(s): return [l for l in s.split('\n') if not l.strip().startswith('//')]
cl=code_lines(t)
for tok in ['FPVIe_RELAY_SENSE_ON','FPVIe_CONTACTMODE','FPVIe_HIGH_MV','FPVIe_LOW_MV','rampi_capv','rampv_capv','FPVIE_RELAY_ON']:
    print('  code %-24s %d'%(tok,sum(l.count(tok) for l in cl)))
print('  code FPVI0.SetClamp %d'%sum(l.count('SetClamp') for l in cl))
print('  code delay_ms(2)   %d'%sum(l.count('delay_ms(2)') for l in cl))
print('  code MeasureVI(200, 5, FPVIe_MV_X10) %d'%sum(l.count('MeasureVI(200, 5, FPVIe_MV_X10)') for l in cl))
print('  code long holds (delay_ms(>=10)) %d'%sum(1 for l in cl if 'delay_ms(' in l and l.split('delay_ms(')[1][0].isdigit() and int(l.split('delay_ms(')[1].split(')')[0])>=10))