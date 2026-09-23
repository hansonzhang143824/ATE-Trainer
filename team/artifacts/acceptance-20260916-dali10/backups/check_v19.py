import sys,io,os,hashlib,json
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'test-plan.json'); r=open(p,'rb').read()
print('test-plan.json live: %d B / %s'%(len(r),hashlib.sha256(r).hexdigest()))
print('  claim: 164399 / d2aef4ad5f3e48f9...')
J=json.loads(r.decode('utf-8-sig'))
print('  revision:',str(J.get('revision'))[:90])
it=[x for x in J['items'] if x.get('tm')=='TM600'][0]
print('  TM600 settle param:',[x.get('value') for x in it['parameters'] if x.get('name')=='settle'])
print('  pulseCap.metric:',str((it.get('measurement') or {}).get('pulseCap',{}).get('metric'))[:150])
print()
u=open(os.path.join(d,'implementation-payload-TM600-TM601.cpp'),'rb').read().decode('utf-8-sig')
code=[l for l in u.split('\n') if not l.strip().startswith('//')]
print('payload: delay_ms(1)=%d delay_ms(2)=%d'%(sum(l.count('delay_ms(1)') for l in code),sum(l.count('delay_ms(2)') for l in code)))
print('  delay_ms(3) count:',sum(l.count('delay_ms(3)') for l in code),'| delay_ms(5):',sum(l.count('delay_ms(5)') for l in code))
print('  clamp comment has stricter-than-golden:', 'STRICTER THAN THE GOLDEN' in u or 'stricter than the golden' in u.lower())
print('  pulse-window note present:', 'outside the pulse' in u.lower() or 'not in the pulse' in u.lower())