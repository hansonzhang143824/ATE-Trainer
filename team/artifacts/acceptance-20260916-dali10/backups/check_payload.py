import sys,io
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
p=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10\implementation-payload-TM600-TM601.cpp'
t=open(p,'rb').read().decode('utf-8-sig')
for tok in ['FPVIe_RELAY_SENSE_ON','FPVIe_CONTACTMODE','FPVIe_HIGH_MV','FPVIe_LOW_MV','FPVIe_100MV','FPVIe_MV_X10','FPVIe_RELAY_ON']:
    print('  %-24s %d'%(tok,t.count(tok)))