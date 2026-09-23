import sys,io,os,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
for n in ['implementation-payload-TM600-TM601.cpp','implementation-payload-TM600-TM601.pulse2ms-variant.cpp']:
    p=os.path.join(d,n)
    if os.path.exists(p):
        r=open(p,'rb').read(); print('%-58s %6d B %s'%(n,len(r),hashlib.sha256(r).hexdigest()))
    else: print('%-58s DELETED (its content is now the delivered payload)'%n)
p=os.path.join(d,'implementation-payload-TM600-TM601.cpp')
u=open(p,'rb').read().decode('utf-8-sig'); code=[l for l in u.split('\n') if not l.strip().startswith('//')]
print()
print('settle=delay_ms(1):',sum(l.count('delay_ms(1)') for l in code),' delay_ms(2):',sum(l.count('delay_ms(2)') for l in code))
print('arithmetic comment present:','1 ms + 1 ms = 2 ms <= 2 ms HARD CAP' in u)
print('deviation labelled:','deliberate deviation' in u.lower())
print('BST rail drive in code:',[l.strip()[:60] for l in code if 'SW12_U1REF_BST_ACM.Set' in l][:2])
print('FPVI1 references in code:',sum(1 for l in code if 'FPVI1' in l))