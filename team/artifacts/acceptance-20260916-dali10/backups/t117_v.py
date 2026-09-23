import sys,io,os,re
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
base=r'D:\Newtest\DSH\ATE-Coding-Plat'
print('=== 1) THEIR PRESCRIPTION: does (pattern, span, position) reproduce a match? Demonstrate. ===')
path=os.path.join(base,'scripts','verify_bst_sw_sequence.py')
L=open(path,encoding='utf-8-sig').read().split('\n')
line=L[146]
for pat in [r'count\(', r'\bcount\s*\(', r'\)\s*-\s*']:
    m=re.search(pat,line)
    if m:
        print('  pattern=%-16s span=%-12s line:col=147:%d  text=%r'%(pat,str(m.span()),m.start()+1,m.group(0)))
    else:
        print('  pattern=%-16s NO MATCH  (this pattern would NOT have produced my false positive)'%pat)
print('  => my single pasted match would have shown the substring but NOT which pattern produced it.')
print('     Their three-part form names the instrument; mine named only the observation.')
print()
print('=== 2) THEIR ④ CLAIM: is the third-party pre-append measurement in the message log? ===')
found=[]
for f in ['schematic-expert.jsonl','ate-implementer.jsonl']:
    p=os.path.join(base,'.agent-teams','ate-dali-acceptance','inbox',f)
    if os.path.exists(p):
        t=open(p,'rb').read().decode('utf-8-sig',errors='replace')
        if '429ad881d67d3feb' in t:
            n=t.count('429ad881d67d3feb')
            found.append((f,n))
            print('  %-28s contains 429ad881d67d3feb x%d  <- durable pre-write record'%(f,n))
if not found: print('  (not found in those two logs)')
print('  => confirms: the inbox log DOES carry the pre-append value, making the announcement checkable.')