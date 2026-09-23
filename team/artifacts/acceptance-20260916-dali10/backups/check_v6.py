import sys,io,os,glob,hashlib,json,time
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'test-plan.json'); r=open(p,'rb').read()
J=json.loads(r.decode('utf-8-sig'))
print('live test-plan.json: %d B / %s'%(len(r),hashlib.sha256(r).hexdigest()))
print('revision:',str(J.get('revision'))[:100])
print('mtime:',time.strftime('%H:%M:%S',time.localtime(os.path.getmtime(p))))
print()
print("architect's v6 claim: 134802 B / d84035516c04795c511cba598a86e11602728bc088512bee57266fc73e68a478")
print('  matches live:', len(r)==134802)
pv=os.path.join(d,'test-plan.v6.json')
if os.path.exists(pv):
    rv=open(pv,'rb').read()
    print('  test-plan.v6.json (preserved): %d B / %s'%(len(rv),hashlib.sha256(rv).hexdigest()))
print()
print('stimulusRulingNote present in live:', 'stimulusRulingNote' in json.dumps(J))
print('revisionHistory entries:', len(J.get('revisionHistory') or []))
print()
print('=== retained versions ===')
for q in sorted(glob.glob(os.path.join(d,'test-plan.v*.json'))):
    print('  %-24s %7d B'%(os.path.basename(q),os.path.getsize(q)))