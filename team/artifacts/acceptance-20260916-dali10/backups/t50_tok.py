import sys,io,os,re
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
L=open(r'D:\PROJECT6-DALI\ForCodexDebug\source\test.cpp','rb').read().decode('utf-8-sig').split('\n')
o=next(i for i,l in enumerate(L) if l.startswith('DUT_API int TM640_BOOST_HS_OCP('))
depth=0; started=False
for i in range(o,len(L)):
    t=re.sub(r'//.*$','',L[i]); depth+=t.count('{')-t.count('}')
    if '{' in t: started=True
    if started and depth==0: end=i; break
raw=L[o:end+1]; stripped=[re.sub(r'//.*$','',x) for x in raw]
print('=== TM640 L%d-%d token accounting, all four ways ==='%(o+1,end+1))
for pat,name in [(r'\bK48\b','\\bK48\\b (word-boundary)'),(r'K48(?![0-9])','K48(?![0-9]) alias-inclusive'),(r'K48','K48 plain substring')]:
    a=len(re.findall(pat,' '.join(raw))); b=len(re.findall(pat,' '.join(stripped)))
    print('  %-28s raw(incl comments)=%d  stripped=%d'%(name,a,b))
print()
print('  lines that mention K48/K76:')
for i,x in enumerate(raw):
    if 'K48' in x or 'K76' in x: print('    L%d [%s]| %s'%(o+1+i,'COMMENT' if not stripped[i].strip() else 'CODE',x.strip()[:120]))