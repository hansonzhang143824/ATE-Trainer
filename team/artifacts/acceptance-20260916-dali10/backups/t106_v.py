import sys,io,os,hashlib,time
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
print('=== 1) their identities ===')
for f in ['implementation-payload-TM600-TM601.cpp','implementation-manifest.json','APPLY-TM600-TM601.md']:
    p=os.path.join(d,f); r=open(p,'rb').read()
    print('  %-40s %7d B / %s @%s'%(f,len(r),hashlib.sha256(r).hexdigest()[:16],time.strftime('%H:%M:%S',time.localtime(os.stat(p).st_mtime))))
print()
print('=== 2) their merge: is the substring-collision family real in BOTH directions? ===')
print('  (i) containment read as EQUALITY -> OVER-count  : 97636  inside 0000097636')
s='0000097636'
print('      "97636" in "0000097636" ->', '97636' in s)
print()
print('  (ii) containment read as IDENTITY -> UNDER-report : VAT_LOOP_INDICTOR vs VBAT_LOOP_INDICTOR')
a='TM643_VAT_LOOP_INDICTOR'   # plausible mis-spelling
b='TM643_VBAT_LOOP_INDICTOR'  # the real deployed name
print('      real name contains "VAT_LOOP_INDICTOR"?', 'VAT_LOOP_INDICTOR' in b)
print('      is "VAT_LOOP_INDICTOR" a real distinct relay?', 'no - it is a SUBSTRING of the real name')
print('      => a search for the real name finds it; a search using the truncated form would also "find" it')
print('         yet a name-EQUALITY test would REJECT the real name => under-report/miss')
print()
print('  Both are the same root: presence-of-substring treated as identity.')
print('  Direction differs: (i) false positive in a count, (ii) false negative in a membership test.')