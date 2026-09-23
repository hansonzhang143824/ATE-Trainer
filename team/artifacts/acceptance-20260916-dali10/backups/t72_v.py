import sys,io,os,hashlib,time
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
n=os.path.join(d,'review-handoff-note-plan-side.md')
r=open(n,'rb').read(); t=r.decode('utf-8-sig')
print('=== their new note (they say 54,692 B / 674af1e1... @22:39:05) ===')
print('  %d B / %s @%s'%(len(r),hashlib.sha256(r).hexdigest(),time.strftime('%H:%M:%S',time.localtime(os.stat(n).st_mtime))))
print('  match:', hashlib.sha256(r).hexdigest()=='674af1e1ae8f89f6bffa104bbfd503c51136e6750373aa8caff05882f2b848bd')
print()
print('=== their three claimed zero-counts ===')
for pat in ['execute by the INTERSECTION','retain K109/K110 this round','keep --check-extra disabled','RETAIN `K109`/`K110`','INTERSECTION']:
    print('  %-34s %d'%(pat,t.count(pat)))
print()
print('=== AND the line I flagged last round (L406 forward-looking [48,61,76]) — did it survive? ===')
print('  "[48,61,76]" occurrences: %d'%t.count('[48,61,76]'))
for i,l in enumerate(t.split('\n')):
    if '[48,61,76]' in l and ('is to become' in l or 'to become' in l or '将' in l):
        print('  !! L%-5d %s'%(i+1,l.strip()[:180]))
print()
print('=== and does it still contradict L403-style text? ===')
for i,l in enumerate(t.split('\n')):
    if 'is to become' in l: print('  L%-5d %s'%(i+1,l.strip()[:180]))