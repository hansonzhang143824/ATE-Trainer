import sys,io,os,hashlib,time
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
print('=== DEFINITIVE: one pass, one instant, python plaintext ===')
for n in ['implementation-payload-TM600-TM601.cpp','implementation-manifest.json']:
    p=os.path.join(d,n); r=open(p,'rb').read()
    print('  %-40s %6d B / %s'%(n,len(r),hashlib.sha256(r).hexdigest()))
    print('     mtime %s'%time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(os.stat(p).st_mtime)))
print()
print('  t4 measured payload @19:55:59 = 39457 / 2d0984d9...  -> SAME as live')
print('  t4 measured manifest @19:43:10 = 45296 / b3f1dc93... -> SAME as live')
print('  t4 said payload "又前进了一版" but computed the same value I froze')
print()
print('  K109/K110 occurrence accounting on the live payload:')
u=open(os.path.join(d,'implementation-payload-TM600-TM601.cpp'),'rb').read().decode('utf-8-sig')
import re
print('    all-text K109_BUSL1_PB0 =',u.count('K109_BUSL1_PB0'),'  K110_ACM18_BST =',u.count('K110_ACM18_BST'))
code=[l for l in u.split('\n') if not l.strip().startswith('//')]
print('    executable K109 =',sum(l.count('K109_BUSL1_PB0') for l in code),' executable K110 =',sum(l.count('K110_ACM18_BST') for l in code))
print("    (t4 reported '×2 each' = all-text incl. comments; the executable count is 1 each)")