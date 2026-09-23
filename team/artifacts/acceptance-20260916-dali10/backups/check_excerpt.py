import sys,io,os,hashlib,re
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
print('=== claimed vs live ===')
for n,claim in [('test-plan.json','161516/0578bd5e'),('test-plan-tm600-tm601-measurement-excerpt.md','8423/9554d4d6'),('setup-contract.json','328723/7f505fdb'),('test-plan.v1.json','98641/19e6f2c3')]:
    p=os.path.join(d,n)
    r=open(p,'rb').read()
    print('  %-52s live %7d B %s   (claim %s)'%(n,len(r),hashlib.sha256(r).hexdigest()[:16],claim))
print()
ex=os.path.join(d,'test-plan-tm600-tm601-measurement-excerpt.md')
t=open(ex,'rb').read().decode('utf-8-sig')
print('=== excerpt: delay_ms lines and Amendment 1 ===')
for l in t.split('\n'):
    if 'delay_ms' in l or 'Amendment' in l or 'required-on' in l or '87/88/89' in l:
        print('  ',l.strip()[:150])
print()
u=open(os.path.join(d,'implementation-payload-TM600-TM601.cpp'),'rb').read().decode('utf-8-sig')
code=[l for l in u.split('\n') if not l.strip().startswith('//')]
print('payload now: delay_ms(2)=%d delay_ms(1)=%d'%(sum(l.count('delay_ms(2)') for l in code),sum(l.count('delay_ms(1)') for l in code)))