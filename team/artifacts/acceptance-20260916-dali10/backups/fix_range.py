import sys,io,os,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'implementation-payload-TM600-TM601.cpp')
t=open(p,'rb').read().decode('utf-8-sig')
old='    FPVI0.Set(FV, 0, FPVIe_1V, FPVIe_10A, FPVIe_RELAY_ON);'
new=('    // Range rule (units.md:3-5): range >= 2x the set value, nearest-to-2x smallest step.\n'
     '    // A 0 V / 0 A initialization has no 2x requirement, so the MINIMAL compliant step is used\n'
     '    // (FPVIe_10UA), which is also the unified off-range current side required by R-POFF-06.\n'
     '    FPVI0.Set(FV, 0, FPVIe_1V, FPVIe_10UA, FPVIe_RELAY_ON);')
n=t.count(old)
print('occurrences to change:',n)
t2=t.replace(old,new)
open(p,'wb').write(b'\xef\xbb\xbf'+(t2.replace('\r\n','\n').replace('\n','\r\n')).encode('utf-8'))
raw=open(p,'rb').read(); u=raw.decode('utf-8-sig')
print('bytes',len(raw),'BOM',raw[:3]==b'\xef\xbb\xbf','CRLF',raw.count(b'\r\n'),'loneLF',raw.count(b'\n')-raw.count(b'\r\n'))
print('sha256',hashlib.sha256(raw).hexdigest())
print('FPVIe_10A remaining in code:',sum(1 for l in u.split('\n') if 'FPVIe_10A' in l and not l.strip().startswith('//')))
print('FPVIe_10UA in code:',sum(1 for l in u.split('\n') if 'FPVIe_10UA' in l and not l.strip().startswith('//')))
# regenerate variant from the corrected payload
dst=os.path.join(d,'implementation-payload-TM600-TM601.pulse2ms-variant.cpp')
v=u.replace('delay_ms(2);                                             // settle per the golden',
            'delay_ms(1);                                             // settle shortened from the golden 2 ms so the WHOLE 1 A pulse stays within the 2 ms cap (see header)')
hdr=('// VARIANT: pulse-compliant timing (delay_ms(1)). Range/relay/register content is identical to the\n'
     '// delivered payload, including the corrected 0 V/0 A initialization range.\n'
     '// delay_ms(1) settle 1.000 ms + MeasureVI(200,5) acquisition 1.000 ms = ~2 ms total.\n'
     '// Trade-off: contradicts test-plan.json step 3 and the contract 2 ms settle; plan must be amended.\n')
open(dst,'wb').write(b'\xef\xbb\xbf'+(hdr+v.replace('\r\n','\n').replace('\n','\r\n')).encode('utf-8'))
r2=open(dst,'rb').read()
print()
print('variant %d B %s CRLF=%d loneLF=%d'%(len(r2),hashlib.sha256(r2).hexdigest(),r2.count(b'\r\n'),r2.count(b'\n')-r2.count(b'\r\n')))