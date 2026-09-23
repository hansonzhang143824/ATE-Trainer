import sys,io,os
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
p=r'D:\Newtest\DSH\ATE-Coding-Plat\knowledge\sources\raw\STS8300 硬件手册_Rev2.13.pdf'
print('=== THEIR FALSE-POSITIVE CLAIM: is 97636 in the PDF an xref offset, not a reference? ===')
r=open(p,'rb').read()
print('  file size: %d B'%len(r))
print('  occurrences of b"97636": %d'%r.count(b'97636'))
print()
print('  --- each occurrence in byte context (60 bytes around) ---')
i=0
while True:
    i=r.find(b'97636',i)
    if i<0: break
    seg=r[max(0,i-30):i+40]
    print('  offset %-8d ...%s...'%(i,seg.decode('latin-1').replace('\r','\\r').replace('\n','\\n')))
    i+=1
print()
print('  --- is there an xref section nearby? ---')
j=r.rfind(b'xref',0,len(r))
print('  last "xref" token at byte %d; trailer at %d'%(j, r.rfind(b'trailer')))
import re
xrefs=[m.start() for m in re.finditer(rb'xref',r)]
print('  total "xref" occurrences: %d (first %s, last %s)'%(len(xrefs),xrefs[:3],xrefs[-3:] if xrefs else None))