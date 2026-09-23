import sys,io,hashlib,os
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
src=os.path.join(d,'implementation-payload-TM600-TM601.cpp')
dst=os.path.join(d,'implementation-payload-TM600-TM601.pulse2ms-variant.cpp')
t=open(src,'rb').read().decode('utf-8-sig')
n=t.count('delay_ms(2);                                             // settle per the golden')
n2=t.count('delay_ms(2);                                             // settle per the golden')+t.count('delay_ms(2);')
print('occurrences of the settle line:',n,'/ total delay_ms(2):',n2)
# Replace only the two settle calls in code, adjusting comments to disclose the rationale.
new=t.replace('delay_ms(2);                                             // settle per the golden',
              'delay_ms(1);                                             // settle shortened from the golden 2 ms so the WHOLE 1 A pulse stays within the 2 ms cap (see header)')
hdr=('// VARIANT: pulse-compliant timing (delay_ms(1)).\n'
     '// Use this variant if the "1 A pulse must not exceed 2 ms" cap is read as bounding the WHOLE pulse:\n'
     '//   delay_ms(1) settle 1.000 ms + MeasureVI(200,5) acquisition 1.000 ms = ~2 ms total.\n'
     '// Rule basis: the user\'s wording "delay <=2 ms 内完成测量 / the 1 A pulse must not exceed 2 ms".\n'
     '// Trade-off: it contradicts test-plan.json step 3 ("Wait 2 ms for settling - this IS the pulse cap")\n'
     '// and the contract\'s 2 ms settle, so the plan must be amended if this variant is adopted.\n'
     '// The DELIVERED payload (implementation-payload-TM600-TM601.cpp) keeps the golden 2 ms because that\n'
     '// form is the one authorised verbatim in test-plan-tm600-tm601-measurement-excerpt.md. One of the two\n'
     '// must be chosen by the Captain; both are otherwise identical.\n')
open(dst,'wb').write(b'\xef\xbb\xbf'+ (hdr+new).encode('utf-8'))
for p in (src,dst):
    raw=open(p,'rb').read()
    print('%-56s %6d B %s'%(os.path.basename(p),len(raw),hashlib.sha256(raw).hexdigest()))
v=open(dst,'rb').read().decode('utf-8-sig')
print('variant delay_ms(1) count:',v.count('delay_ms(1)'),' delay_ms(2) count:',v.count('delay_ms(2)'))