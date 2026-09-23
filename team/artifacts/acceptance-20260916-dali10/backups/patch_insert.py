import sys,io,re,os,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
p=r'C:\Users\nvt10241\AppData\Local\Temp\insert_tm600_601.py'
t=open(p,'rb').read().decode('utf-8-sig')
print('current block handling:')
for i,l in enumerate(t.split('\n')):
    if 'BLOCK' in l or 'replace' in l and '\\n' in l:
        print('  %d: %s'%(i+1,l.strip()[:120]))
# patch: replace the block-normalisation line to accept any line endings
old="block = BLOCK.replace('\\n', '\\r\\n')"
new=("block = BLOCK.replace('\\r\\n', '\\n').replace('\\r', '\\n').replace('\\n', '\\r\\n')\n"
     "# normalise whatever line endings the payload file carries, so no lone LF reaches the target")
n=t.count(old)
print('target line occurrences:',n)
if n:
    t2=t.replace(old,new)
    open(p,'wb').write(t2.encode('utf-8'))
    print('patched OK')
    t3=open(p,'rb').read().decode('utf-8-sig')
    print('verify patch present:','normalise whatever line endings' in t3)
else:
    print('PATTERN NOT FOUND — inspect manually')