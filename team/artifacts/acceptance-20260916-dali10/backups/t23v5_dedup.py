import sys,io,os,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'implementation-payload-TM600-TM601.cpp')
u=open(p,'rb').read().decode('utf-8-sig').replace('\r\n','\n')
I=' '*8
for f,var in (('hs_rdson','PMID-SW'),('ls_rdson','SW-PGND')):
    old=I+f+'[site] = (i_meas[site] > 0.1) ? (v_meas[site] / i_meas[site] * 1e3) : 0.0;  // mohm\n'
    n=u.count(old); print('  removing orphaned ternary for %-8s found=%d'%(f,n))
    u=u.replace(old,'')
open(p,'wb').write(b'\xef\xbb\xbf'+u.replace('\n','\r\n').encode('utf-8'))
r=open(p,'rb').read(); v=r.decode('utf-8-sig'); code=[l for l in v.split('\n') if not l.strip().startswith('//')]
print()
print('payload %d B / %s'%(len(r),hashlib.sha256(r).hexdigest()))
print('ternary/0.0 left:',sum(1 for l in code if ': 0.0;' in l))
print('ERROR_RES uses:',sum(l.count('ERROR_RES') for l in code))
print('rdson assignments:',[l.strip()[:70] for l in code if 'rdson[site] =' in l])
print('BOM',r[:3]==b'\xef\xbb\xbf','| loneLF',r.count(b'\n')-r.count(b'\r\n'))