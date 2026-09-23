import sys,io,os,json,hashlib,re,time
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'implementation-manifest.json')
M=json.loads(open(p,'rb').read().decode('utf-8-sig'))
pay=os.path.join(d,'implementation-payload-TM600-TM601.cpp'); rp=open(pay,'rb').read()
u=rp.decode('utf-8-sig'); code=[l for l in u.split('\n') if not l.strip().startswith('//')]
def n(sub,src): return sum(l.count(sub) for l in src)
# verify each key live BEFORE writing the list, so the list states measured facts
keys=[('t29 PER-FUNCTION JUSTIFICATION (comment, revision-generation key)',u.count('t29 PER-FUNCTION JUSTIFICATION')),
 ('executable code (comments stripped): K109_BUSL1_PB0',n('K109_BUSL1_PB0',code)),
 ('executable code (comments stripped): K110_ACM18_BST',n('K110_ACM18_BST',code)),
 ('executable code: TM601 ACM Sets',sum(1 for l in u[u.find('DUT_API int TM601_LS_RDSON'):].split('\n') if 'SW12_U1REF_BST_ACM.Set' in l and not l.strip().startswith('//'))),
 ('executable code: TM600 ACM Sets',sum(1 for l in u[:u.find('DUT_API int TM601_LS_RDSON')].split('\n') if 'SW12_U1REF_BST_ACM.Set' in l and not l.strip().startswith('//'))),
 ('executable code: delay_ms(1)',n('delay_ms(1)',code)),
 ('executable code: delay_ms(2)',n('delay_ms(2)',code)),
 ('executable code: SetClamp(50, 50)',n('SetClamp(50, 50)',code)),
 ('executable code: MeasureVI(200, 5, FPVIe_MV_X10)',n('MeasureVI(200, 5, FPVIe_MV_X10)',code)),
 ('executable code: bare 126 tokens',len(re.findall(r'(?<![\dA-Za-z_])126(?![\dA-Za-z_])',' '.join(code)))),
 ('executable code: K126_V1P5_CAP',n('K126_V1P5_CAP',code)),
 ('executable code: ERROR_RES',n('ERROR_RES',code)),
 ('executable code: K5_VBUS_Cap + K44_Cap_SW2_BST2 + K45_Cap_SW1_BST1',n('K5_VBUS_Cap',code)+n('K44_Cap_SW2_BST2',code)+n('K45_Cap_SW1_BST1',code)),
 ('executable code: K57_CAP_BST_SW',n('K57_CAP_BST_SW',code))]
print('=== MEASURED keys on the live payload (these are what get written) ===')
for lbl,v in keys: print('  %-72s %d'%(lbl,v))
blk=M['handoffCitationRisk']
blk['criterion']=('PRIMARY RULE (co-authored with test-strategy-architect, amended): cite an artefact by CONTENT KEY, not by a single hash - the owner keeps '
 'revising it, so a hash anchor races. A payload file is the right revision only if it satisfies EVERY key below, counted with COMMENTS STRIPPED '
 '("executable code"). Specifying the count without "executable code" would let a file whose relay list has been deleted still pass because the '
 'justification comment still mentions the relay names - the same failure class as prose standing in for executable fact.')
blk['authoritativeCurrentValues'][0]['mustContain']=['%s = %d'%(lbl,v) for lbl,v in keys]
blk['authoritativeCurrentValues'][0]['mustContainNote']=('Counts above are MEASURED on this file at this instant, with comments stripped for the executable entries; the '
 'first entry is a comment and is deliberately a whole-text count because it is the revision-generation key. A payer that satisfies the comment key '
 'but fails an executable key is the WRONG REVISION.')
open(p,'wb').write((json.dumps(M,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
r=open(p,'rb').read()
print()
print('manifest %d B / %s'%(len(r),hashlib.sha256(r).hexdigest()))
print('valid JSON:',bool(json.loads(r.decode('utf-8'))))