import sys,io,os,hashlib,time
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
print('=== live vs quoted, all four contested artifacts ===')
rows=[
 ('dft-ir.json','82398d2f882abc2bc452ed307e47ae64ff25d7a13553abfe61b73fdd04d0d568',116140,'dft-expert msg2'),
 ('schematic-ir-sensing.json','ad9859e9317fee99afacbc686b1c265efd15c444dab5a4f7712af5147e470140',47156,'captain x2'),
 ('test-plan.json','2e93a46c54c79b9028940840f6cf162d15304f89df3c3e88dd5fdea5f5061eda',121694,'t10 task output'),
]
for n,quoted,qsize,src in rows:
    p=os.path.join(d,n)
    raw=open(p,'rb').read(); h=hashlib.sha256(raw).hexdigest()
    print('%-30s live=%7d %s' % (n,len(raw),h[:16]))
    print('%-30s quot=%7d %s  (source: %s)  MATCH=%s' % ('',qsize,quoted[:16],src,h==quoted and len(raw)==qsize))
    print('%-30s mtime=%s now=%s' % ('',time.strftime('%H:%M:%S',time.localtime(os.path.getmtime(p))),time.strftime('%H:%M:%S')))
print()
print('=== is dft-raw/dft-ir-hashes.json the sidecar, and what does IT say? ===')
sp=os.path.join(d,'dft-raw','dft-ir-hashes.json')
if os.path.exists(sp):
    s=open(sp,'rb').read()
    print('sidecar %d B sha256 %s'%(len(s),hashlib.sha256(s).hexdigest()))
    print(s.decode('utf-8-sig')[:900])
else: print('sidecar ABSENT at',sp)