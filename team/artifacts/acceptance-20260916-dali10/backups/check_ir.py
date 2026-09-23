import sys,io,os,hashlib,json,re,csv
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'dft-ir.json')
raw=open(p,'rb').read()
print('dft-ir.json now: %d B  sha256 %s'%(len(raw),hashlib.sha256(raw).hexdigest()))
print("dft-expert claims: 116140 B / 82398d2f882abc2bc452ed307e47ae64ff25d7a13553abfe61b73fdd04d0d568")
print("match:",len(raw)==116140 and hashlib.sha256(raw).hexdigest()=='82398d2f882abc2bc452ed307e47ae64ff25d7a13553abfe61b73fdd04d0d568')
J=json.loads(raw.decode('utf-8-sig'))
def find(o,key,path=''):
    out=[]
    if isinstance(o,dict):
        for k,v in o.items():
            if k==key: out.append((path+'/'+k,v))
            else: out+=find(v,key,path+'/'+k)
    elif isinstance(o,list):
        for i,v in enumerate(o): out+=find(v,key,path+'[%d]'%i)
    return out
print()
print('=== blockingDecisions status ===')
for pth,v in find(J,'blockingDecisions'):
    if isinstance(v,list):
        for b in v:
            if isinstance(b,dict): print('  %-8s %-8s %s'%(b.get('id'),b.get('status'),str(b.get('resolution') or b.get('question'))[:80]))
print()
print('=== TM601 forceAndSense ===')
for it in J.get('items',[]):
    if it.get('tm')=='TM601':
        fs=it.get('forceAndSense') or {}
        print('  force.pins:',json.dumps(fs.get('force',{}).get('pins'),ensure_ascii=False))
        print('  force.ruledPair:',fs.get('force',{}).get('ruledPair'))
        print('  consistentWithCheckNode:',fs.get('force',{}).get('consistentWithCheckNode'))
        print('  sense.pins:',json.dumps(fs.get('sense',{}).get('pins'),ensure_ascii=False))
        print('  selfConsistency:',str(fs.get('selfConsistency'))[:160])