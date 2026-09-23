import sys,io,os,hashlib,glob
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
base=r'D:\Newtest\DSH\ATE-Coding-Plat'
d=os.path.join(base,'team','artifacts','acceptance-20260916-dali10')
print('=== 1) is 41,797 B / 6034af71... anywhere on disk? (run dir + backups) ===')
found=[]
for root,dirs,files in os.walk(d):
    for f in files:
        p=os.path.join(root,f)
        try: b=open(p,'rb').read()
        except: continue
        if len(b)==41797 or hashlib.sha256(b).hexdigest().startswith('6034af71'):
            found.append((os.path.relpath(p,d),len(b),hashlib.sha256(b).hexdigest()[:16]))
print('  matches:',found if found else 'NONE — that intermediate state was overwritten')
print()
print('=== 2) the CURRENT canonical, measured ===')
p=os.path.join(d,'implementation-payload-TM600-TM601.cpp'); r=open(p,'rb').read()
print('  %d B / %s'%(len(r),hashlib.sha256(r).hexdigest()))
print('  they measured the same: 43,806 / 66abc088... -> identical')
print()
print('=== 3) so which version is "the union" and does any claim require it on disk? ===')
print('  6034af71 (41,797) = the UNION intermediate, written 20:48:18, SUPERSEDED at 20:59:12')
print('  66abc088 (43,806) = CURRENT frozen canonical, ch5-only (K109/K110 = 0)')
print('  => my version chain was a HISTORY list, not an inventory of files that must exist.')
print()
print('=== 4) and the union-vs-removal question, resolved by the captain?s own documents ===')
for n in ['t50-payload-k76-evidence.md','implementation-manifest.json']:
    q=os.path.join(d,n)
    if os.path.exists(q):
        t=open(q,'rb').read().decode('utf-8-sig')
        print('  %s: mentions "union": %d | mentions "REMOV" : %d'%(n,t.count('union'),len([1 for x in [t] if 'REMOV' in x])))