import sys,io,hashlib,os
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
src=os.path.join(d,'implementation-payload-TM600-TM601.cpp')
dst=os.path.join(d,'implementation-payload-TM600-TM601.pulse2ms-variant.cpp')
t=open(src,'rb').read().decode('utf-8-sig')
# regenerate the variant from the updated payload so both carry the same header
new=t.replace('delay_ms(2);                                             // settle per the golden',
              'delay_ms(1);                                             // settle shortened from the golden 2 ms so the WHOLE 1 A pulse stays within the 2 ms cap (see header)')
hdr=('// VARIANT: pulse-compliant timing (delay_ms(1)).\n'
     '// Use this variant if the "1 A pulse must not exceed 2 ms" cap is read as bounding the WHOLE pulse:\n'
     '//   delay_ms(1) settle 1.000 ms + MeasureVI(200,5) acquisition 1.000 ms = ~2 ms total.\n'
     '// Trade-off: contradicts test-plan.json step 3 ("Wait 2 ms for settling - this IS the pulse cap")\n'
     '// and the contract 2 ms settle, so the plan must be amended if this variant is adopted.\n'
     '// The DELIVERED payload keeps the golden 2 ms because that form is the one authorised verbatim in\n'
     '// test-plan-tm600-tm601-measurement-excerpt.md. Otherwise the two files are identical.\n')
open(dst,'wb').write(b'\xef\xbb\xbf'+(hdr+new).encode('utf-8'))
for p in (src,dst):
    raw=open(p,'rb').read()
    print('%-58s %6d B %s'%(os.path.basename(p),len(raw),hashlib.sha256(raw).hexdigest()))
import difflib
a=[l for l in open(src,'rb').read().decode('utf-8-sig').split('\n') if not l.strip().startswith('//')]
b=[l for l in open(dst,'rb').read().decode('utf-8-sig').split('\n') if not l.strip().startswith('//')]
dd=[l for l in difflib.unified_diff(a,b,lineterm='',n=0) if l.startswith(('+','-')) and not l.startswith(('+++','---'))]
print('code-level diff lines:',len(dd))
for l in dd: print('   ',l[:110])
# compliance re-check
code=[l for l in t.split('\n') if not l.strip().startswith('//')]
print('code K87/K88/K89 mentions:',[n for n in ('K87','K88','K89') if any(n in l for l in code)])
print('code SetOn lists unchanged:',sum(1 for l in code if 'cbite.SetOn(' in l))