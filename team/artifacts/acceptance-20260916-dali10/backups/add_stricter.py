import sys,io,os,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'implementation-payload-TM600-TM601.cpp')
t=open(p,'rb').read().decode('utf-8-sig')
old='    // Re-issued after every force/measure mode switch (the switch clears it back to 102%).'
new=('    // Re-issued after every force/measure mode switch (the switch clears it back to 102%).\n'
     '    // STRICTER THAN THE GOLDEN PRECEDENT: the archived golden sets the clamp only once;\n'
     '    // the re-issue is a manual requirement (knowledge/sources/fpvie.md:141-168), not a deviation.')
n=t.count(old)
print('occurrences of the target comment:',n)
t2=t.replace(old,new)
open(p,'wb').write(t2.encode('utf-8').replace(b'\r\n',b'\n').replace(b'\n',b'\r\n') if False else t2.encode('utf-8'))
raw=open(p,'rb').read()
print('bytes',len(raw),'sha256',hashlib.sha256(raw).hexdigest())
u=raw.decode('utf-8-sig')
print('STRICTER THAN THE GOLDEN present:',u.count('STRICTER THAN THE GOLDEN PRECEDENT'))
print('BOM kept:',raw[:3]==b'\xef\xbb\xbf')
# regenerate variant from updated payload
dst=os.path.join(d,'implementation-payload-TM600-TM601.pulse2ms-variant.cpp')
v=u.replace('delay_ms(2);                                             // settle per the golden',
            'delay_ms(1);                                             // settle shortened from the golden 2 ms so the WHOLE 1 A pulse stays within the 2 ms cap (see header)')
hdr=('// VARIANT: pulse-compliant timing (delay_ms(1)).\n'
     '// delay_ms(1) settle 1.000 ms + MeasureVI(200,5) acquisition 1.000 ms = ~2 ms total.\n'
     '// Trade-off: contradicts test-plan.json step 3 and the contract 2 ms settle; plan must be amended.\n'
     '// The DELIVERED payload keeps the golden 2 ms (authorised verbatim in the excerpt). Otherwise identical.\n')
open(dst,'wb').write(b'\xef\xbb\xbf'+(hdr+v).encode('utf-8'))
for f in (p,dst):
    r=open(f,'rb').read(); print('%-58s %6d B %s'%(os.path.basename(f),len(r),hashlib.sha256(r).hexdigest()))