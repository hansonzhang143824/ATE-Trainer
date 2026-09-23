import sys,io,os,re,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
base=r'D:\Newtest\DSH\ATE-Coding-Plat'
d=os.path.join(base,'team','artifacts','acceptance-20260916-dali10')
tgt=os.path.join(r'D:\PROJECT6-DALI\ForCodexDebug','source','test.cpp')
cur=open(tgt,'rb').read().decode('utf-8-sig')
pay=open(os.path.join(d,'implementation-payload-TM600-TM601.cpp'),'rb').read().decode('utf-8-sig')
body=pay[pay.find('DUT_API int TM600_HS_RDSON'):]
s=cur.find('DUT_API int TM600_HS_RDSON'); pre=cur.rfind('\n//',0,s)
j=cur.find('DUT_API int TM601_LS_RDSON',s); e=cur.find('\nDUT_API int',j+10)
if e<0: e=len(cur)
patched=cur[:pre]+'\n'+body.rstrip('\n')+'\n'+(cur[e:] if e<len(cur) else '')
sbx=os.path.join(d,'gate-check-t21','source','test.cpp')
open(sbx,'w',encoding='utf-8',newline='').write(patched)
r=open(sbx,'rb').read(); print('sandbox rebuilt: %d B / %s'%(len(r),hashlib.sha256(r).hexdigest()))
# range pairing table from the payload's executable code
code=[l for l in pay.split('\n') if not l.strip().startswith('//')]
RNG={'FXVIe_PLUS_10V':10,'FXVIe_PLUS_20V':20,'FXVIe_PLUS_30V':30,'FXVIe_PLUS_40V':40,
     'ACM200_10V':10,'ACM200_20V':20,'ACM200_40V':40,'FPVIe_1V':1,'FPVIe_2V':2,'FPVIe_5V':5,
     'FPVIe_10V':10,'FPVIe_20V':20,'FPVIe_40V':40,'FPVIe_100V':100}
rows=[]
for l in code:
    m=re.search(r'(\w+)\.Set\(FV,\s*([-\d.]+),\s*(\w+),',l)
    if m:
        inst,v,rng=m.group(1),float(m.group(2)),m.group(3)
        rows.append((inst,v,rng,RNG.get(rng)))
print()
print('=== Set(FV, v, range) pairing table: range >= 2x v (0 V exempt) ===')
bad=0
seen=set()
for inst,v,rng,rg in rows:
    key=(v,rng)
    if key in seen: continue
    seen.add(key)
    if v==0: verdict='n/a (zero, no 2x requirement)'
    elif rg is None: verdict='UNKNOWN RANGE'; bad+=1
    elif rg>=2*v: verdict='OK (%.0f >= %.1f)'%(rg,2*v)
    else: verdict='VIOLATION (%.0f < %.1f)'%(rg,2*v); bad+=1
    print('  %-22s v=%-5s range=%-18s %s'%(inst,v,rng,verdict))
print('  violations:',bad)