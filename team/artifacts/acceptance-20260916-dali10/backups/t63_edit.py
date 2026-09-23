import sys,io,os,json,hashlib,time
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
mp=os.path.join(d,'implementation-manifest.json')
before=open(mp,'rb').read()
M=json.loads(before.decode('utf-8-sig'))
ch=M['handoffCitationRisk']
ch['countingMethod']=('TWO BINDING COUNTING RULES. (1) STRIP: counts use the PROPER comment strip re.sub(r"//.*$","",text,flags=re.M) - inline trailing '
 'comments removed, not merely lines that begin with //. A line-leading-only strip leaves text like "// ERROR_RES = 9999" counted and '
 'over-reports ERROR_RES as 4 instead of 2. (2) ENUMERATION: a count must NOT rely on token text search; it must enumerate via MACRO EXPANSION plus '
 'an explicit alias list. Instance: TM641 (L7623) and TM643 (L7734) close K48/K76 through the composite K_FPVIH_TO_BST_A (StdAfx.h:377 = 46,48,76), '
 'which a literal search for "K48" or even \\bK48\\b cannot see - the word-boundary form fails because "_" is a word character. Both rules are the '
 'same failure class: a criterion whose implementation detail is unstated cannot certify a revision. Every key must therefore be quoted WITH its '
 'strip method, its definition, and (where macros are involved) the enumeration method. Cross-check for ACM Sets: unstripped = stripped + comment mentions.')
ch['scopeWindows']={
 'rule':'State the SCOPE of every count, not just its value - function body vs file level, mentions-including-comments vs executable, and the revision.',
 'instances':[
  'TM600 instrument mentions: 6 (5 code + 1 comment) - a "5" and a "6" were both quoted with different scopes.',
  'K48/K76 in TM607/608/609/640: 2 mentions each at line level (1 code + 1 comment) vs 1 executable line; both correct.',
  'K109_BUSL1_PB0 all-text 3 vs executable 0 on the current frozen payload.',
  'the six-function collision set (any leg closure, incl. composite-only) vs the four-function pattern set (drives AND closes explicitly) - they must not be collapsed.'],
 'note':'Recorded because four separate apparent disagreements in this run turned out to be scope differences rather than factual ones. Collision questions use the SIX; pattern questions use the FOUR.'}
open(mp,'wb').write((json.dumps(M,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
after=open(mp,'rb').read()
print('manifest %d B -> %d B / %s'%(len(before),len(after),hashlib.sha256(after).hexdigest()))
J=json.loads(after.decode('utf-8'))
c=J['handoffCitationRisk']
print('  rule 1 (strip) present:', 'PROPER comment strip' in c['countingMethod'])
print('  rule 2 (enumeration/macro) present:', 'MACRO EXPANSION' in c['countingMethod'])
print('  scopeWindows added:', 'scopeWindows' in c)
p=os.path.join(d,'implementation-payload-TM600-TM601.cpp'); pr=open(p,'rb').read()
print('  payload untouched:', hashlib.sha256(pr).hexdigest()=='66abc088ae6bd5f9b9d7201673003fc0be2450fd6f1f222c6a4a902cbe4f0cc4')