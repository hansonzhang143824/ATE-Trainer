import sys,io,os,re,json,glob
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
base=r'D:\Newtest\DSH\ATE-Coding-Plat'
print('=== 1) DFT.csv TM601 row: does it declare bst2sw? ===')
csvp=os.path.join(base,'project','DALI','input','DFT.csv')
rows=open(csvp,'rb').read().decode('utf-8-sig',errors='replace').split('\n')
hdr=rows[0]
print('  header tokens:',hdr[:220])
# find TM601 / TM600 rows
for i,l in enumerate(rows):
    if 'TM601' in l or 'TM600' in l:
        bst='bst2sw' in l
        print('  L%d [%s] bst2sw=%s'%(i+1,'TM601' if 'TM601' in l else 'TM600',bst))
        if bst:
            m=re.search(r'vset\[[^\]]*bst2sw[^\]]*\]',l)
            if m: print('       ->',m.group(0))
print()
print('=== 2) contract: any bst2sw anywhere, and which TMs use it ===')
J=json.loads(open(os.path.join(base,'team','artifacts','acceptance-20260916-dali10','setup-contract.json'),'rb').read().decode('utf-8-sig'))
for i,e in enumerate(J.get('aliasResolution') or []):
    if e.get('alias')=='bst2sw':
        print('  aliasResolution[%d] bst2sw usedByTm=%s'%(i,json.dumps(e.get('usedByTm'),ensure_ascii=False)))
s=json.dumps(J,ensure_ascii=False)
print('  bst2sw occurrences in the whole contract:',s.count('bst2sw'))
print()
print('=== 3) TM601 delta: does it reference the ACM instrument at all? ===')
t6=json.dumps(J['tmDeltas']['TM601'],ensure_ascii=False)
for tok in ['SW12_U1REF_BST_ACM','ACM200','bst_sw','bst2sw','BST']:
    print('  %-22s %d'%(tok,t6.count(tok)))