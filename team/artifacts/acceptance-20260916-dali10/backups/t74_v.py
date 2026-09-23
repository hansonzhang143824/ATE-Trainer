import sys,io,os,hashlib,time
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
n=os.path.join(d,'review-handoff-note-plan-side.md')
r=open(n,'rb').read(); t=r.decode('utf-8-sig')
print('=== their note ===')
print('  %d B / %s @%s'%(len(r),hashlib.sha256(r).hexdigest(),time.strftime('%H:%M:%S',time.localtime(os.stat(n).st_mtime))))
print('  they say: 56,971 B / 19f954764ebf638f749f5c6ab1c0be07499337635c1d257e31bd307638d568b5 @22:44:57')
print('  match:', hashlib.sha256(r).hexdigest()=='19f954764ebf638f749f5c6ab1c0be07499337635c1d257e31bd307638d568b5')
print()
print('=== did L424 (the forward-looking [48,61,76] with rev 25) get fixed? ===')
for i,l in enumerate(t.split('\n')):
    if 'is to become' in l: print('  L%-5d <<< STILL PRESENT: %s'%(i+1,l.strip()[:180]))
for i,l in enumerate(t.split('\n')):
    if '[48,61,76]' in l:
        fwd=' <<< FORWARD-LOOKING' if 'to become' in l else ''
        print('  L%-5d %s%s'%(i+1,l.strip()[:120],fwd))
print()
print('=== their four binding rules present? ===')
for pat in ['2.0','2.1','2.2','2.3']:
    print('  section §%s present: %s'%(pat, ('§'+pat) in t or ('## '+pat) in t or ('\n'+pat+'.') in t))
for pat in ['MACRO EXPANSION' if False else 'macro expansion','strip method','enumerating its wordings','per-owner']:
    print('  %-28s %d'%(pat,t.lower().count(pat.lower())))
print()
print('=== and the four-run claim ===')
for pat in ['29, 33, 37 and 39','four times','ten contract revisions']:
    print('  %-28s %d'%(pat,t.count(pat)))