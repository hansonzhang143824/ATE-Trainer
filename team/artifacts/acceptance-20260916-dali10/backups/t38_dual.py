import pathlib,hashlib,time
p=pathlib.Path(r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10\implementation-payload-TM600-TM601.cpp')
b=p.read_bytes()
print("  length =",len(b))
print("  hash   =",hashlib.sha256(b).hexdigest())
print("  mtime  =",time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(p.stat().st_mtime)))