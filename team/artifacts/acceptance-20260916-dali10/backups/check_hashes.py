import sys,io,os,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
for n in ['schematic-ir-sensing.json','schematic-ir.json','setup-contract.json','test-plan.json']:
    p=os.path.join(d,n)
    if not os.path.exists(p): print('%-30s ABSENT'%n); continue
    raw=open(p,'rb').read()
    print('%-30s %8d B  %s  mtime=%s'%(n,len(raw),hashlib.sha256(raw).hexdigest(),__import__('time').strftime('%H:%M:%S',__import__('time').localtime(os.path.getmtime(p)))))
print()
print("captain claim (2nd notice): sensing = 47156 B / ad9859e9317fee99afacbc686b1c265efd15c444dab5a4f7712af5147e470140")