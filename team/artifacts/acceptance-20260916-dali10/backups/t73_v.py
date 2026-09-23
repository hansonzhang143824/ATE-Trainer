import sys,io,os,hashlib,time,re
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
n=os.path.join(d,'review-handoff-note-plan-side.md')
r=open(n,'rb').read(); t=r.decode('utf-8-sig')
print('=== current note ===')
print('  %d B / %s @%s'%(len(r),hashlib.sha256(r).hexdigest(),time.strftime('%H:%M:%S',time.localtime(os.stat(n).st_mtime))))
print('  they say: 55,722 B / a15ce3029d499a8b0c5538c09fdad176f04961bb88979f4add9a3134a88660c3 @22:40:56')
print('  match:', hashlib.sha256(r).hexdigest()=='a15ce3029d499a8b0c5538c09fdad176f04961bb88979f4add9a3134a88660c3')
print()
print('=== their claimed counts ===')
for pat in ['RETAIN `K109`/`K110` this round','retain `K109`/`K110` this round','`--check-extra` not to be enabled','keep `--check-extra` disabled','INTERSECTION','UNION/intersection','contract `rev 25`','BLOCKED']:
    print('  %-40s %d'%(pat,t.count(pat)))
print()
print('=== THE LINE IN QUESTION ===')
for i,l in enumerate(t.split('\n')):
    if 'is to become' in l: print('  L%-5d %s'%(i+1,l.strip()[:200]))
print()
print('=== every [48,61,76] with a marker for forward-looking ===')
for i,l in enumerate(t.split('\n')):
    if '[48,61,76]' in l:
        fwd='<<< FORWARD-LOOKING' if ('is to become' in l or '将' in l or 'to become' in l) else ''
        print('  L%-5d %s %s'%(i+1,l.strip()[:130],fwd))