import sys,io,os,re
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
path=r'D:\Newtest\DSH\ATE-Coding-Plat\scripts\verify_bst_sw_sequence.py'
line=open(path,encoding='utf-8-sig').read().split('\n')[146]
print('L147 = %r'%line)
print()
print('=== THEIR CORRECTION: my "subtraction" pattern captured the tail of an ARROW ===')
m=re.search(r'\)\s*-\s*',line)
print('  \\)\\s*-\\s*  -> match=%r span=%s  context=%r'%(m.group(0),m.span(),line[max(0,m.start()-6):m.end()+6]))
print('  => the captured "-" is part of "->" : %s'%('YES - it is the arrow tail' if line[m.start():m.end()+1].find('->')>=0 or line[m.end()]=='>' else 'no'))
print('  char after the match:', repr(line[m.end()]) if m.end()<len(line) else 'EOL')
print()
print('=== TEST A PROPER FIX: operator must not be inside -> or be unary ===')
pats=[r'(?<![-<>])-(?!>)', r'\)\s*-\s*', r'\s-\s']
for p in pats:
    ms=[x.group(0) for x in re.finditer(p,line)]
    print('  %-18s matches=%d %s'%(p,len(ms),ms[:4]))
print()
print('  => a lookaround form correctly rejects the arrow; the bare form does not.')
print('     So ANCHORING must apply to the OPERATOR as well as the operand - their point.')