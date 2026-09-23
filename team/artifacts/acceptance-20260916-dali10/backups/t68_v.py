import sys,io,os,re,hashlib,time
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
n=os.path.join(d,'review-handoff-note-plan-side.md'); r=open(n,'rb').read(); t=r.decode('utf-8-sig')
print('=== their note (they say 46,465 B / a5caa9c8... @22:23:45) ===')
print('  %d B / %s @%s'%(len(r),hashlib.sha256(r).hexdigest(),time.strftime('%H:%M:%S',time.localtime(os.stat(n).st_mtime))))
print()
print('=== verify the corrected passage exists ===')
for pat in ['WRITTEN as an intermediate state','SUPERSEDED by the','was on disk from 20:48:18']:
    print('  %-34s %d'%(pat,t.count(pat)))
print()
print('=== their claim: plan v25 "操作值 [48,60,61,76] 两侧：BST [48,76] ∈ ACM200 / SW [60,61] ∈ FPVIe[L]" ===')
for pat in ['v25','closedRelayNumbers','[48, 61, 76]','[48,61,76]','[48, 60, 61, 76]']:
    print('  note mentions %-22s %d'%(pat,t.count(pat)))
print()
p=os.path.join(d,'test-plan.json')
if os.path.exists(p):
    pr=open(p,'rb').read(); import json
    J=json.loads(pr.decode('utf-8-sig'))
    print('  ACTUAL test-plan.json: %d B / %s'%(len(pr),hashlib.sha256(pr).hexdigest()))
    print('  they say: 185,689 B / 707ce845... @21:54:50')
    print('  revision field:',str(J.get('revision'))[:70])