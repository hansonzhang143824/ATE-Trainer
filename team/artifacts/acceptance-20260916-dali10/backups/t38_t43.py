import sys,io,os,json,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'implementation-manifest.json')
before=open(p,'rb').read()
M=json.loads(before.decode('utf-8-sig'))
lg=M['handoffCitationRisk']['landingGate']
lg['status']='BLOCKED pending t43 - the payload must NOT be treated as electrically correct or cleared to land.'
lg['gates']=['t43 (independent review + adjudication: ch5 vs ch18; K109/K110 disposition; whether ch18+[110] is permitted; rev 25 before payload)']
lg['completed']=['t40 (rule-reviewer, final revision 37430005...)','t42 (schematic-expert, pin attribution - PASS)','t44 (supplement)','t39 (contract owner) - reached its conclusion under the ch18 premise, which t43 can overturn']
lg['gateHistoryNote']=('The gate was earlier stated as t39+t40 and then t40+t42; both are superseded. Per the captain, t43 is now the SOLE gate. '
 'The field name and the prohibition on "cleared to land" wording are retained deliberately.')
lg['acmSetsDefinition']={
 'ruling':('ACM Sets(<fn>) = the number of lines in that function body which, AFTER stripping inline comments (re.sub(r"//.*$","")) '
   'and dropping leading whitespace, are non-empty and contain ".Set". NOT the instrument-name occurrence count.'),
 'crossCheck':'unstripped count = stripped count + comment mentions (current tree: TM600 11 = 10 + 1; TM601 0 = 0 + 0)',
 'why':'the two definitions coincide on the current payload by coincidence (TM600 10/10, TM601 0/0) and diverge as soon as a comment inside the executable region mentions the instrument, or a non-.Set reference appears (e.g. an ACM200_RELAY_OFF-only call). A "usually equal" definition is a latent false pass, so the definition must be written verbatim wherever the key is used.'}
# also keep the countingMethod honest about the definition requirement
M['handoffCitationRisk']['countingMethod']=('Counts use the PROPER comment strip: re.sub(r"//.*$","",text,flags=re.M) - inline trailing comments removed, not merely '
 'lines that begin with //. A line-leading-only strip leaves text like "// ERROR_RES = 9999" counted and over-reports ERROR_RES as 4 instead of 2. '
 'BOTH the strip method AND each key\'s definition must be stated with the key: "executable code" without a stated strip, or "ACM Sets" without its '
 '.Set-line definition, can mis-certify a revision. Cross-check for ACM Sets: unstripped = stripped + comment mentions.')
open(p,'wb').write((json.dumps(M,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
r=open(p,'rb').read(); J=json.loads(r.decode('utf-8'))
print('manifest %d B -> %d B'%(len(before),len(r)))
print('  sha256 now: %s'%hashlib.sha256(r).hexdigest())
print('  landingGate.status:',J['handoffCitationRisk']['landingGate']['status'][:70])
print('  gates:',J['handoffCitationRisk']['landingGate']['gates'])
print('  completed entries:',len(J['handoffCitationRisk']['landingGate']['completed']))
print('  acmSetsDefinition present:', 'acmSetsDefinition' in J['handoffCitationRisk']['landingGate'])
print('  t43 mentioned:', 't43' in json.dumps(J,ensure_ascii=False))