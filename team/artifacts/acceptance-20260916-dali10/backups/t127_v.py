import sys,io,re
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
print('=== THEIR PROOF: two strings with IDENTICAL local context around "-" but different arity ===')
a='n - x'; b='return -x'
m=re.search(r'(?<=[\w\)\]])\s*-(?!>)',a); n=re.search(r'(?<=[\w\)\]])\s*-(?!>)',b)
print('  %-14r -> match=%s'%(a,bool(m)))
print('  %-14r -> match=%s'%(b,bool(n)))
print()
print('  local context around the minus:')
for s in (a,b):
    i=s.index('-')
    print('    %-14r  ...%r | minus | %r...'%(s,s[max(0,i-3):i],s[i+1:i+4]))
print('  => identical: "n" + space + "-" in both. Yet the first is BINARY, the second is a keyword tail.')
print('  => NO local character rule can separate them. Their proof holds.')
print()
print('=== AND THEIR FULL WITNESS SET on my replacement pattern ===')
cases=[('len(a) - len(b)',1),('x-y',1),('(a)-b',1),('arr[i]-b',1),('errors) -> None',0),
       ('f(-a)',0),('a*-b',0),('-x',0),('return -x',0),('a - -b',1)]
ok=0;bad=[]
for s,want in cases:
    got=len(re.findall(r'(?<=[\w\)\]])\s*-(?!>)',s))
    status='OK' if got==want else 'FAIL'
    if got==want: ok+=1
    else: bad.append((s,want,got))
    print('  %-20r want=%d got=%d  %s'%(s,want,got,status))
print()
print('  passed %d/%d; failures: %s'%(ok,len(cases),bad))