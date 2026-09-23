import sys,io,os,re
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
inc=r'C:\AccoTEST\AccoTEST System\INCLude'
def rd(p):
    try: return open(p,'rb').read().decode('utf-8-sig',errors='replace')
    except Exception as e: return ''
g=rd(os.path.join(inc,'ATDriverPackGlobal.h'))
print('=== enum MeasRet in ATDriverPackGlobal.h ===')
m=re.search(r'enum\s+MeasRet\s*\{(.*?)\}',g,re.S)
print('  ', [v.strip() for v in m.group(1).split(',') if v.strip()] if m else 'NOT FOUND')
print('  MEASTYPERET present:', 'MEASTYPERET' in g)
h=rd(os.path.join(inc,'FPVIe.h'))
print('=== FPVIe_RET_RESULT declared (FPVIe.h) ===')
m2=re.search(r'enum\s+FPVIe_RET_RESULT\s*\{(.*?)\}',h,re.S)
print('  ', [v.strip() for v in m2.group(1).split(',') if v.strip()] if m2 else 'NOT FOUND')
print('=== any FPVIe public method taking FPVIe_RET_RESULT? ===')
hits=[l.strip() for l in h.split('\n') if 'FPVIe_RET_RESULT' in l]
for l in hits: print('   ',l[:110])
print()
print('=== K88 usage: does it carry both SH0 and SL0 (single sense relay per channel)? ===')
src=r'D:\PROJECT6-DALI\ForCodexDebug\source'
s=rd(os.path.join(src,'StdAfx.h'))
for n in ('K87_FPVI0_FH_SL_SHORT','K88_FPVI0_Sense_FLOAT','K89_FPVI0_FL_SH_SHORT','K86_FPVI0_H_SHORT','K86_FPVI0_L_SHORT'):
    for l in s.split('\n'):
        if re.match(r'\s*#define\s+'+n+r'\s',l): print('   ',l.strip())