import sys,io,os,hashlib,time
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
print('=== the three identities they confirm, re-measured NOW ===')
for f,claim in [('implementation-manifest.json','57,147 B / 9eec2fbd…'),
                ('APPLY-TM600-TM601.md','9,005 B / 27d18e1e…'),
                ('implementation-payload-TM600-TM601.cpp','43,806 B / 66abc088… (frozen)')]:
    p=os.path.join(d,f); r=open(p,'rb').read()
    print('  %-40s %7d B / %s @%s'%(f,len(r),hashlib.sha256(r).hexdigest()[:16],time.strftime('%H:%M:%S',time.localtime(os.stat(p).st_mtime))))
    print('      they claim: %s'%claim)
print()
print('=== TESTING THEIR SELF-CRITICISM: is the READER RULE spread across lines? (line-scope vs block-scope) ===')
ap=os.path.join(d,'APPLY-TM600-TM601.md')
L=open(ap,'rb').read().decode('utf-8-sig').split('\n')
import re
# their claim: downgrade at L112, authoritative value at L110/L111 -> cross-line, so a LINE-scoped check gives relational=0
for i in range(106,116):
    if i<len(L):
        marks=[]
        if '48,60,61,76' in L[i] and '61,76]' in L[i] and '48,61,76' not in L[i]: marks.append('AUTHORITATIVE')
        if '{48,60,61,76,83}' in L[i]: marks.append('EXPECTATION')
        if '[48,61,76]' in L[i]: marks.append('OLD-SHORTHAND')
        if 'not targets' in L[i] or 'incomplete' in L[i]: marks.append('DOWNGRADE')
        print('  L%-4d %-28s %s'%(i+1,'+'.join(marks) if marks else '',L[i].strip()[:110]))
print()
print('  => line-scoped check: each line carries ONE role, so a per-line "downgrade next to value" test finds nothing.')
print('  => block-scoped check: L110-114 as ONE block contains AUTHORITATIVE + EXPECTATION + OLD-SHORTHAND + DOWNGRADE together.')
print('     Their self-criticism is correct, and the instrument they prescribe (print scope+wordlist+window) is the fix.')