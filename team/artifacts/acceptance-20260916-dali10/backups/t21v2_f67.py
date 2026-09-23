import sys,io,os,re,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'implementation-payload-TM600-TM601.cpp')
u=open(p,'rb').read().decode('utf-8-sig').replace('\r\n','\n')
# F6: replace the pulse-arithmetic header block with an explicitly THEORETICAL statement
old=('//   Pulse-width arithmetic for this payload (measured, not assumed) - CAPTAIN RULING (b) APPLIED:\n'
     '//     settle   delay_ms(1)                    = 1.000 ms\n'
     '//     MeasureVI(200, 5) acquisition           = 200 x 5 us = 1.000 ms   (MEAS_NORMAL\n'
     '//                                               completes inside the call, so it adds time)\n'
     '//     -> effective 1 A pulse                  = 2 ms <= 2 ms HARD CAP  OK\n')
new=('//   Pulse-width budget for this payload -- THEORETICAL, NOT MEASURED (captain ruling (b) applied):\n'
     '//     settle   delay_ms(1)                    = 1.000 ms\n'
     '//     MeasureVI(200, 5) acquisition           = 200 x 5 us = 1.000 ms   (MEAS_NORMAL\n'
     '//                                               completes inside the call, so it adds time)\n'
     '//     -> nominal total                        = 2.000 ms, i.e. EXACTLY the 2 ms HARD CAP\n'
     '//   F6 -- MARGIN IS ZERO ON PAPER. These are nominal SDK/spec figures and they EXCLUDE the\n'
     '//   driver, call and relay latency that a real instrument adds, so the true pulse is >= 2.000 ms\n'
     '//   and cannot be shown to satisfy the cap by calculation alone. This payload must therefore NOT\n'
     '//   be described as "pulse-compliant, measured": compliance is a BRING-UP VERIFICATION ITEM --\n'
     '//   scope the actual force-ON to force-OFF interval on hardware and confirm <= 2 ms before any\n'
     '//   claim. Recorded with U11 as a bring-up limitation, not as a verified result.\n')
n=u.count(old); print('F6 header block found:',n)
if n==1: u=u.replace(old,new)
# F7: artifact landing note
anchor='// MANIFEST BOUNDARY SENTENCE - reproduce VERBATIM in implementation-manifest.json:'
f7=('// F7 -- ARTEFACT LANDING (must be stated in the manifest and the report):\n'
    '//   dali_tm_meta.json and test_conditions.yaml are generated into the DSH WORKSPACE at\n'
    '//   project/DALI/meta/, NOT into the VS debug tree. They are workspace-side build/report\n'
    '//   artefacts consumed by the gates and the manifest; they are not part of the VS project and\n'
    '//   are not compiled. The only VS-tree change from this task is source/test.cpp.\n'
    '//\n')
n2=u.count(anchor); print('F7 anchor found:',n2)
if n2==1: u=u.replace(anchor,f7+anchor)
open(p,'wb').write(b'\xef\xbb\xbf'+u.replace('\n','\r\n').encode('utf-8'))
r=open(p,'rb').read(); v=r.decode('utf-8-sig')
print()
print('payload %d B / %s'%(len(r),hashlib.sha256(r).hexdigest()))
print('F6 wording present:','THEORETICAL, NOT MEASURED' in v and 'MARGIN IS ZERO ON PAPER' in v)
print('F7 note present:','ARTEFACT LANDING' in v)
print('BOM',r[:3]==b'\xef\xbb\xbf','| loneLF',r.count(b'\n')-r.count(b'\r\n'))