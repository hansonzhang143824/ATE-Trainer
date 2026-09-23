import sys,io,json,hashlib,os,time
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'test-plan.json'); raw=open(p,'rb').read()
print('test-plan.json %d B sha256 %s mtime=%s'%(len(raw),hashlib.sha256(raw).hexdigest(),time.strftime('%H:%M:%S',time.localtime(os.path.getmtime(p)))))
J=json.loads(raw.decode('utf-8-sig'))
print('revision:',J.get('revision'))
want={'TM600':{'PMID rail':'15','supply rail':'4.2','gate-drive rail':'5'},
      'TM601':{'supply rail':'4.2','PMID rail':'9','gate-drive rail':'5'}}
for it in J.get('items',[]):
    tm=it.get('tm')
    if tm in ('TM600','TM601'):
        print('\n#### %s stimulus (vs ruling ATE values)'%tm)
        for s in it.get('stimulus',[]):
            print('   %-38s kind=%-18s value=%-6s  %s'%(str(s.get('driven'))[:38],s.get('kind'),s.get('value'),str(s.get('source'))[:60]))