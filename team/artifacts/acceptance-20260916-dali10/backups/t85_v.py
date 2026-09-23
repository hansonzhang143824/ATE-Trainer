import sys,io,os,hashlib,time
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
n=os.path.join(d,'review-handoff-note-plan-side.md')
r=open(n,'rb').read(); t=r.decode('utf-8-sig'); h=hashlib.sha256(r).hexdigest()
print('=== their anchor ===')
print('  %d B / %s @%s'%(len(r),h,time.strftime('%H:%M:%S',time.localtime(os.stat(n).st_mtime))))
print('  they cite 78,058 B / d26308f7412d0f0fed1a08b9771faa00d6640fbe2baf53ab6d13b50b03f54716 @23:33:44')
print('  match:', h=='d26308f7412d0f0fed1a08b9771faa00d6640fbe2baf53ab6d13b50b03f54716')
print()
print('=== did the version qualifier on the coordinates land? ===')
print('  "AS OF THEIR RESPECTIVE REVISIONS" count:', t.count('AS OF THEIR RESPECTIVE REVISIONS'))
print('  "L406" count:', t.count('L406'), '| "L509" count:', t.count('L509'))
print()
print('=== the rewritten premise (read the sentence) ===')
i=t.find('five times')
if i>0:
    print('  ', ' '.join(t[max(0,i-160):i+330].split())[:470])