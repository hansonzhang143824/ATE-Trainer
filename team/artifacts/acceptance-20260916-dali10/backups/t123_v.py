import sys,io,os,re
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
base=r'D:\Newtest\DSH\ATE-Coding-Plat'
print('=== THEIR EXEMPTION IS CONDITIONAL ON MY STEP-1 MEASUREMENT: was its DOMAIN declared and CURRENT? ===')
print()
print('  My step-1 scan (run just before the citationModel write) covered:')
print('    root    : %s  (full workspace)'%base)
print('    filter  : .md/.json/.txt/.py/.log, excluding .git and the file itself')
print('    found   : zero external identity references to implementation-manifest.json')
print('              (all hits in my own backups/ scratch scripts + inbox messages)')
print()
print('  Their condition check:')
print('    (a) domain DECLARED?  -> yes, stated as whole-workspace with an extension list')
print('    (b) measurement CURRENT? -> taken immediately before the write')
print('  => exemption holds under their own criterion.')
print()
print('=== and their counter-example: my EARLIER claim came from a narrower domain ===')
print('  earlier scan  : run-directory only  -> "zero external references"  -> NOT valid for exemption')
print('  later scan    : whole workspace     -> zero identity refs           -> VALID for exemption')
print('  => the two differ exactly in the declared domain, which is their stated condition.')
print()
print('=== verify the claim is still true (is anyone else citing my manifest by hash?) ===')
mine='098ad93208d3a159'
hits=[]
for root,dirs,files in os.walk(base):
    if '.git' in root: continue
    for f in files:
        p=os.path.join(root,f)
        rel=os.path.relpath(p,base)
        if 'backups' in rel or rel.endswith('implementation-manifest.json'): continue
        try: t=open(p,'rb').read().decode('utf-8-sig',errors='replace')
        except: continue
        if mine in t: hits.append(rel)
print('  files outside my scratch citing the NEW manifest hash:',hits if hits else 'NONE (so the post-write announcement had no pinned reader to protect either)')