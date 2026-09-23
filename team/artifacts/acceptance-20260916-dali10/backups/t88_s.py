import sys,io,os,re
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
t=open(os.path.join(d,'review-handoff-note-plan-side.md'),'rb').read().decode('utf-8-sig')
print('=== search for the sixth self-correction in ANY wording ===')
for pat in ['Self-correction (sixth','sixth, mine','sixth','Self-correction']:
    print('  %-24s %d'%(pat,t.count(pat)))
print()
print('=== every Self-correction occurrence, in context ===')
for m in re.finditer(r'Self-correction[^\n]{0,160}',t):
    print('  - %s'%m.group(0)[:165])
print()
print('=== and the "sixth" mention, wherever it is ===')
for i,l in enumerate(t.split('\n')):
    if 'sixth' in l.lower():
        print('  L%-5d %s'%(i+1,l.strip()[:170]))