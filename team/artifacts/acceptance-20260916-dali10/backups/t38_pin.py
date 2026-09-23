import sys,io,os,json,re
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
base=r'D:\Newtest\DSH\ATE-Coding-Plat'
J=json.loads(open(os.path.join(base,'team','artifacts','acceptance-20260916-dali10','setup-contract.json'),'rb').read().decode('utf-8-sig'))
print('=== A) EVERY ACM200-side route in the contract, with needsClosed ===')
def walk(o,path=''):
    if isinstance(o,dict):
        if 'needsClosed' in o and isinstance(path,str) and 'ACM200' in path:
            print('  %-64s %s'%(path[-64:],o['needsClosed']))
        for k,v in o.items(): walk(v,path+'/'+str(k))
    elif isinstance(o,list):
        for i,v in enumerate(o): walk(v,path+'[%d]'%i)
for tm in ('TM600','TM601'):
    print(' --',tm)
    walk(J['tmDeltas'][tm].get('pinRouteTable') or {},'/'+tm)
print()
print('=== B) the channel macro pin mapping ===')
s=json.dumps(J,ensure_ascii=False)
for key in ['_PIN_CHANNEL_DEFINE_SW12_U1REF_BST_ACM_']:
    for m in re.finditer(re.escape(key),s):
        print('  ...',s[max(0,m.start()-60):m.start()+160].replace('\\n',' ')[:220])
print()
print('=== C) does anything in either delta need 48 or 76? ===')
for tm in ('TM600','TM601'):
    d=json.dumps(J['tmDeltas'][tm],ensure_ascii=False)
    print('  %s: relaySet has 48=%s 76=%s | occurrences of "48" as relay: %d'%(tm,48 in (J['tmDeltas'][tm].get('relaySet') or []),76 in (J['tmDeltas'][tm].get('relaySet') or []),len(re.findall(r'\b48\b',d))))
print()
print('=== D) TM600 BST route entries (both AMC200-side and FPVIe-side) ===')
r=J['tmDeltas']['TM600'].get('pinRouteTable',{}).get('BST',{})
for k,v in (r.items() if isinstance(r,dict) else []):
    print('  %-60s %s'%(k,v))