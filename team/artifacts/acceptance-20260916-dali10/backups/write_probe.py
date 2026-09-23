import hashlib
p=r'D:\PROJECT6-DALI\ForCodexDebug\source\test.cpp'
raw=open(p,'rb').read()
print('read OK:',len(raw),'bytes; python plaintext sha256',hashlib.sha256(raw).hexdigest())
p2=r'D:\PROJECT6-DALI\ForCodexDebug\source\__t5_write_probe.tmp'
open(p2,'wb').write(b'probe')
print('write probe OK')
import os; os.remove(p2); print('probe removed')