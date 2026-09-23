import sys,io,json
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
p=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10\test-plan.json'
J=json.loads(open(p,'rb').read().decode('utf-8-sig'))
for it in J.get('items',[]):
    if it.get('tm') in ('TM600','TM601'):
        print('#### %s'%it.get('tm'))
        for key in ('relayUnion','relayMinimalMacros','negativeRelayList','relayState'):
            if key in it: print('  %s: %s'%(key,json.dumps(it[key],ensure_ascii=False)[:600]))
        # search any field mentioning minimal macro / negative list / OPEN
        for k,v in it.items():
            s=json.dumps(v,ensure_ascii=False)
            if 'minimal' in s.lower() or 'negative' in s.lower() or 'OPEN' in s:
                print('  [%s] %s'%(k,s[:600]))