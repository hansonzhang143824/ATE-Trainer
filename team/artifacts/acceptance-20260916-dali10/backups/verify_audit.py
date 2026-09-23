import sys,io,os,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'HASH-AUDIT.md'); r=open(p,'rb').read()
print('HASH-AUDIT.md %d B / %s'%(len(r),hashlib.sha256(r).hexdigest()))
t=r.decode('utf-8-sig')
print('  FOUR DISCIPLINES heading:','## FOUR DISCIPLINES' in t)
print('  rule 4 present:','Never cite your own previously printed number' in t)
print('  20483 marked void:','now VOID' in t)
print('  caveat withdrawn:','Caveat withdrawn' in t)
print('  schema note for t9:','sizeBytes' in t)
# sanity: target untouched, and I did not touch the two owned artifacts
s=open(r'D:\PROJECT6-DALI\ForCodexDebug\source\test.cpp','rb').read()
print()
print('target test.cpp baseline intact:',hashlib.sha256(s).hexdigest()=='5c9cb3f9339f6db373afcff7504ef6b34924a4ca3042b5926cb612c819ac3317')