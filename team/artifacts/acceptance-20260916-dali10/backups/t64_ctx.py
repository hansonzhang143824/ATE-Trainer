import sys,io,os
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
t=open(os.path.join(d,'review-handoff-note-plan-side.md'),'rb').read().decode('utf-8-sig').split('\n')
for rng in [(7,16),(234,246)]:
    print('=== L%d-%d ==='%rng)
    for i in range(rng[0]-1,min(rng[1],len(t))): print('  L%-4d %s'%(i+1,t[i].strip()[:165]))
    print()