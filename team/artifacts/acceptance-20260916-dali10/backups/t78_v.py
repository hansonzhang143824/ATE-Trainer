import sys,io,os,hashlib,time
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
n=os.path.join(d,'review-handoff-note-plan-side.md')
r=open(n,'rb').read(); t=r.decode('utf-8-sig')
h=hashlib.sha256(r).hexdigest()
print('=== CURRENT note, measured now ===')
print('  %d B / %s @%s'%(len(r),h,time.strftime('%H:%M:%S',time.localtime(os.stat(n).st_mtime))))
print('  they cite: 65,653 B / 5fc81a11791959ef8a78647b212d84459cc9061d9f5d4156bc507b2e1ece1c08 @23:01:56')
print('  match:', h=='5fc81a11791959ef8a78647b212d84459cc9061d9f5d4156bc507b2e1ece1c08')
print()
print('=== their claimed counts ===')
for pat in ['is to become','{48,60,61,76,83}','rev >= 29','holds for every contract revision from 29 onward','is to become `[48,61,76]`']:
    print('  %-52s %d'%(pat,t.count(pat)))
print()
print('=== the correction block, read verbatim (is the old wording quoted, not asserted?) ===')
for i,l in enumerate(t.split('\n')):
    if 'Correction (my own slip' in l or 'is to become' in l:
        print('  L%-5d %s'%(i+1,l.strip()[:190]))
print()
print('=== MY LAST MESSAGE (sent before theirs) claimed these facts — do they still hold? ===')
print('  I reported: "is to become" once at L509, inside the correction block  -> still true:', t.count('is to become')==1)
print('  I reported the file at 64,670 B -> the file was 64,670 B when I read it; now', len(r),'B (moved after my read)')