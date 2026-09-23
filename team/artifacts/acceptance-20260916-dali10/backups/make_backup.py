import hashlib,os,shutil
SRC=r'D:\PROJECT6-DALI\ForCodexDebug\source\test.cpp'
BAK=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10\backups\test.cpp.before_TM600_TM601.bak'
raw=open(SRC,'rb').read()
print('src sha256',hashlib.sha256(raw).hexdigest(),'bytes',len(raw))
open(BAK,'wb').write(raw)
b=open(BAK,'rb').read()
print('bak sha256',hashlib.sha256(b).hexdigest(),'bytes',len(b),'identical',b==raw)
print('bak path',BAK)