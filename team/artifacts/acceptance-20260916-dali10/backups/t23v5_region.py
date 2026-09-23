import sys,io,os,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'implementation-payload-TM600-TM601.cpp')
u=open(p,'rb').read().decode('utf-8-sig').replace('\r\n','\n')
i=u.find('// F5 SIGN PREMISE: MVRET stays SIGNED')
j=u.find('\n',u.find('hs_rdson[site] = ERROR_RES',i))
j=u.find('\n',j+1)
print('=== region to replace (lines) ===')
for k,l in enumerate(u[i:j].split('\n')): print('%3d| %s'%(k+1,l[:130]))