import sys,io,os,re
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
base=r'D:\Newtest\DSH\ATE-Coding-Plat'
p=os.path.join(base,'team','artifacts','acceptance-20260916-dali10','acceptance-report.json')
print('=== THEIR FINDING: acceptance-report.json holds both superseded and current payload hashes ===')
if os.path.exists(p):
    t=open(p,'rb').read().decode('utf-8-sig',errors='replace')
    name='implementation-payload-TM600-TM601.cpp'
    print('  file size: %d B; name occurrences: %d'%(len(t),t.count(name)))
    for m in re.finditer(re.escape(name),t):
        win=t[max(0,m.start()-400):m.start()+400]
        hs=re.findall(r'\b[0-9a-f]{32,64}\b',win)
        print('  --- occurrence at %d ---'%m.start())
        for h in set(hs):
            tag=''
            if h.startswith('66abc088'): tag='  <== CURRENT'
            elif h.startswith(('2d0984d9','5a668fe6','6034af71','c03632d9','272667f3')): tag='  <== SUPERSEDED'
            print('      %s%s'%(h[:24],tag))
        # look for nearby wording implying history
        for w in ['superseded','SUPERSEDED','historical','earlier','previous','prior','frozen']:
            if w in win: print('      [wording nearby: %s]'%w)
else:
    print('  NOT FOUND')