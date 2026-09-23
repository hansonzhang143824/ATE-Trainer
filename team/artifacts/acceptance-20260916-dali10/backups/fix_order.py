import sys,io,os,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'implementation-payload-TM600-TM601.cpp')
t=open(p,'rb').read().decode('utf-8-sig')
# 1) swap TM600's last two RELAY_OFF lines so FPVI0 (the measurement channel) releases last
old=('    FPVI0.Set(FV, 0, FPVIe_1V, FPVIe_10MA, FPVIe_RELAY_OFF);\r\n'
     '    FPVI1.Set(FV, 0, FPVIe_1V, FPVIe_10MA, FPVIe_RELAY_OFF);')
new=('    FPVI1.Set(FV, 0, FPVIe_1V, FPVIe_10MA, FPVIe_RELAY_OFF);  // channel 1 (BST-SW loop) releases first\r\n'
     '    FPVI0.Set(FV, 0, FPVIe_1V, FPVIe_10MA, FPVIe_RELAY_OFF);  // measurement channel releases LAST (R-POFF-04)')
n=t.count(old)
print('swaps found:',n)
if n==1: t=t.replace(old,new)
# 2) make the negative list explicit next to the SetOn calls
old2='    cbite.SetOn(K83_BUSH0_PMID, K60_BUSL0_VCP, K61_ACM8_SW, K13_VBAT_Cap, K85_CAP_PMID, K57_CAP_BST_SW, 126, -1);'
new2=('    // EXPLICIT NEGATIVE LIST (must never be actuated here): relays 87, 88, 89, 90, 91 - the\n'
      '    // local-sense cross-shorts, the sense-float and the two PC-route relays. None appears in any\n'
      '    // minimal endpoint macro above; they occur only in composite macros, which are forbidden.\n'
      '    cbite.SetOn(K83_BUSH0_PMID, K60_BUSL0_VCP, K61_ACM8_SW, K13_VBAT_Cap, K85_CAP_PMID, K57_CAP_BST_SW, 126, -1);')
if t.count(old2)==1: t=t.replace(old2,new2)
open(p,'wb').write(b'\xef\xbb\xbf'+(t.replace('\r\n','\n').replace('\n','\r\n')).encode('utf-8'))
raw=open(p,'rb').read(); u=raw.decode('utf-8-sig'); code=[l for l in u.split('\n') if not l.strip().startswith('//')]
print('payload',len(raw),'B BOM',raw[:3]==b'\xef\xbb\xbf','loneLF',raw.count(b'\n')-raw.count(b'\r\n'))
print('sha256',hashlib.sha256(raw).hexdigest())
seq=[]; cur=None; order={}
for l in code:
    if 'DUT_API int' in l: cur=l.split('int ')[1].split('(')[0]; order[cur]=[]
    if cur and 'RELAY_OFF' in l: order[cur].append(l.split('.Set')[0].strip())
for k,v in order.items(): print('  %-20s %s  FPVI0 last=%s'%(k,v,v[-1].startswith('FPVI0')))
# regenerate variant
dst=os.path.join(d,'implementation-payload-TM600-TM601.pulse2ms-variant.cpp')
v=u.replace('delay_ms(2);                                             // settle per the golden',
            'delay_ms(1);                                             // settle shortened for the whole-pulse 2 ms cap (see header)')
hdr=('// VARIANT: pulse-compliant timing (delay_ms(1)). Range/relay/register content identical to the\n'
     '// delivered payload, including the corrected 0 V/0 A init range and the FPVI0-last teardown.\n')
open(dst,'wb').write(b'\xef\xbb\xbf'+(hdr+v.replace('\r\n','\n').replace('\n','\r\n')).encode('utf-8'))
r2=open(dst,'rb').read(); print('variant',len(r2),'B loneLF',r2.count(b'\n')-r2.count(b'\r\n'),hashlib.sha256(r2).hexdigest())