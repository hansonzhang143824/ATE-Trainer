import sys,io,os,re
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
print('=== THEIR FORMALISM: every pattern must carry an ACCEPTING and a REJECTING witness ===')
print()
print('  Pattern: \\bcount\\s*\\(   (the anchored count call)')
for label,text,expect in [('ACCEPTING witness: x.count(token)','x.count(token)',1),
                          ('REJECTING witness: require_exact_count(','require_exact_count(',0)]:
    ms=[m.span() for m in re.finditer(r'\bcount\s*\(',text)]
    ok = (len(ms)==expect)
    print('    %-42s matches=%d expected=%d  %s  spans=%s'%(label,len(ms),expect,'OK' if ok else 'FAIL',ms))
print()
print('  Pattern: (?<![-<>])-(?!>)   (a real subtraction operator)')
for label,text,expect in [('ACCEPTING witness: len(a) - len(b)','len(a) - len(b)',1),
                          ('REJECTING witness: errors) -> None','errors) -> None',0),
                          ('REJECTING witness: -x unary','return -x',0)]:
    ms=[m.span() for m in re.finditer(r'(?<![-<>])-(?!>)',text)]
    ok=(len(ms)==expect)
    print('    %-42s matches=%d expected=%d  %s'%(label,len(ms),expect,'OK' if ok else 'FAIL'))
print()
print('  => both patterns now carry a positive and a negative witness; the pair is reproducible.')
print('     Their point: only a negative witness on the NEAREST lookalike proves the anchoring.')