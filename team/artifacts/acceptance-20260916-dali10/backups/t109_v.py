import sys,io,os,re
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
base=r'D:\Newtest\DSH\ATE-Coding-Plat'
print('=== 1) reproduce THEIR mechanism claim: is the A-B form negative-prone? ===')
correct='TM643_VBAT_LOOP_INDICTOR'
wrong='TM643_VAT_LOOP_INDICTOR'
for label,text in [('file with only the CORRECT spelling',correct),
                   ('file with only the MISSPELLING',wrong)]:
    a=text.count('VAT_LOOP_INDICTOR'); b=text.count('VBAT_LOOP_INDICTOR')
    print('  %-38s count(VAT)=%d count(VBAT)=%d  A-B=%d'%(label,a,b,a-b))
print('  => A-B can be NEGATIVE. A count that can go negative is not a count. Confirmed.')
print()
print('=== 2) does any GATE SCRIPT I run contain that form? (my delivery must not depend on it) ===')
sd=os.path.join(base,'scripts')
pat=re.compile(r'(\w+)\s*-\s*(\w+)')
sus=[]
for f in sorted(os.listdir(sd)):
    if not f.endswith('.py'): continue
    t=open(os.path.join(sd,f),encoding='utf-8-sig',errors='replace').read().split('\n')
    for i,l in enumerate(t):
        if re.search(r'count\(|\.count|len\(',l) and re.search(r'\)\s*-\s*',l) and 'len(' in l:
            sus.append((f,i+1,l.strip()[:120]))
print('  candidate count-subtraction lines in scripts/: %d'%len(sus))
for f,ln,l in sus[:10]: print('    %-30s L%-4d %s'%(f,ln,l))
print()
print('=== 3) and the name-normalisation question: does any gate compare relay names by substring? ===')
for f in sorted(os.listdir(sd)):
    if not f.endswith('.py'): continue
    t=open(os.path.join(sd,f),encoding='utf-8-sig',errors='replace').read()
    if re.search(r'count\(\s*["\']V',t) or 'names - ' in t:
        print('    %s mentions a name-difference form'%f)