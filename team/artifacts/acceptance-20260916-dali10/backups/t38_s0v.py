import sys,io,os,re,hashlib,time
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'t40-tm601-bst-evidence.md')
t=open(p,'rb').read().decode('utf-8-sig')
print('=== section 0 opening lines (verify t40+t42 wording) ===')
for i,l in enumerate(t.split('\n')[:26]):
    if l.strip(): print('%3d| %s'%(i+1,l[:150]))
print()
print('  contains "t40 + t42":', 't40 + t42' in t)
print('  contains "pending t39+t40" (must be gone):', 'pending t39+t40' in t)
print('  contains the pin-5 conditional block:', 'SCOPE OF THE OPEN QUESTIONS' in t)
print('  file: %d B / %s @%s'%(os.path.getsize(p),hashlib.sha256(open(p,'rb').read()).hexdigest(),time.strftime('%H:%M:%S',time.localtime(os.stat(p).st_mtime))))