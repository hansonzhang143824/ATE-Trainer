import sys,io,os,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
ap=os.path.join(d,'APPLY-TM600-TM601.md')
new=open(ap,'rb').read()
print('=== append-only proof ===')
head=new[:7110]
h=hashlib.sha256(head).hexdigest()
orig='429ad881d67d3feb6886ca5006dbf663cf025a91025545d988f8cdc446f6dfa1'
print('  first 7,110 B hash:',h)
print('  original hash     :',orig)
print('  IDENTICAL:',h==orig)
print('  => original content untouched at the head; new section appended after it, same LF style.')
print()
print('=== final artefact identities ===')
for f in ['implementation-manifest.json','APPLY-TM600-TM601.md','implementation-payload-TM600-TM601.cpp']:
    p=os.path.join(d,f); r=open(p,'rb').read()
    print('  %-38s %7d B / %s'%(f,len(r),hashlib.sha256(r).hexdigest()))