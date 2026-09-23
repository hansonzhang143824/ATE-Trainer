import sys,io,os,hashlib,time
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
n=os.path.join(d,'review-handoff-note-plan-side.md')
r=open(n,'rb').read(); t=r.decode('utf-8-sig'); h=hashlib.sha256(r).hexdigest()
print('=== their anchor ===')
print('  %d B / %s @%s'%(len(r),h,time.strftime('%H:%M:%S',time.localtime(os.stat(n).st_mtime))))
print('  they cite 75,735 B / f638a45c53f93a321f070e0f5304e1fe1b7a2973309b1b6a5a213c47ec352ffd @23:29:41')
print('  match:', h=='f638a45c53f93a321f070e0f5304e1fe1b7a2973309b1b6a5a213c47ec352ffd')
print()
print('=== is the §2.6 rule on disk? ===')
for pat in ['2.6','RE-CHECK','re-report','re-check before']:
    print('  %-22s %d'%(pat,t.count(pat)))
print()
print('=== final delivery, one more independent check of MY artefact ===')
p=os.path.join(d,'implementation-payload-TM600-TM601.cpp'); pr=open(p,'rb').read()
import re
code=re.sub(r'//.*$','',pr.decode('utf-8-sig'),flags=re.M)
h2=hashlib.sha256(pr).hexdigest()
print('  %d B / %s @%s'%(len(pr),h2,time.strftime('%H:%M:%S',time.localtime(os.stat(p).st_mtime))))
print('  frozen 66abc088:', h2=='66abc088ae6bd5f9b9d7201673003fc0be2450fd6f1f222c6a4a902cbe4f0cc4')
print('  BOM=%s loneLF=%d CRLF=%d'%(pr[:3]==b'\xef\xbb\xbf',pr.count(b'\n')-pr.count(b'\r\n'),pr.count(b'\r\n')))
print('  K48=%d K76=%d K109=%d K110=%d K46=%d'%(code.count('K48_ACM5_AMP_REF'),code.count('K76_ACM_BST'),code.count('K109_BUSL1_PB0'),code.count('K110_ACM18_BST'),code.count('K46')))