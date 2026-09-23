import sys,io,os
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
t=open(os.path.join(d,'review-handoff-note-plan-side.md'),'rb').read().decode('utf-8-sig').split('\n')
print('=== L396-412 (context of the disputed line) ===')
for i in range(395,412):
    if i<len(t): print('  L%-4d %s'%(i+1,t[i].rstrip()[:175]))