import hashlib,os
p=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10\implementation-payload-TM600-TM601.cpp'
r=open(p,'rb').read()
print('  payload %d B / %s'%(len(r),hashlib.sha256(r).hexdigest()))
print('  frozen value 66abc088ae6bd5f9b9d7201673003fc0be2450fd6f1f222c6a4a902cbe4f0cc4 -> MATCH:',hashlib.sha256(r).hexdigest()=='66abc088ae6bd5f9b9d7201673003fc0be2450fd6f1f222c6a4a902cbe4f0cc4')