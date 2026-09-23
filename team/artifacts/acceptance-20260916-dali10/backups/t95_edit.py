import sys,io,os,json,re,hashlib,time
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
mp=os.path.join(d,'implementation-manifest.json')
before=open(mp,'rb').read()
M=json.loads(before.decode('utf-8-sig'))
h=M['handoffCitationRisk']

# --- recompute the current payload's own quantities, on current bytes ---
p=os.path.join(d,'implementation-payload-TM600-TM601.cpp')
raw=open(p,'rb').read(); u=raw.decode('utf-8-sig'); L=u.split('\r\n')
stripped=[re.sub(r'//.*$','',x) for x in L]; code=re.sub(r'//.*$','',u,flags=re.M)
t6=next(i for i,l in enumerate(L) if l.startswith('DUT_API int TM600_HS_RDSON'))
t7=next(i for i,l in enumerate(L) if l.startswith('DUT_API int TM601_LS_RDSON'))
def acmsets(a,b): return sum(1 for x in stripped[a:b] if 'SW12_U1REF_BST_ACM.Set' in x)
raw_sha=hashlib.sha256(raw).hexdigest()

h['authoritativeCurrentValues']=[{
 'artefact':'implementation-payload-TM600-TM601.cpp',
 'size':len(raw),'sha256':raw_sha,
 'mtime':time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(os.stat(p).st_mtime)),
 'revisionNote':'FROZEN under the captain stop-writing order; no writes since 21:09:24.',
 'mustContain':[
  'executable code (comments stripped): K48_ACM5_AMP_REF = 1',
  'executable code (comments stripped): K76_ACM_BST = 1',
  'executable code (comments stripped): K109_BUSL1_PB0 = 0',
  'executable code (comments stripped): K110_ACM18_BST = 0',
  'executable code (comments stripped): K46 = 0',
  'executable code: TM600 ACM Sets = %d'%acmsets(t6,t7),
  'executable code: TM601 ACM Sets = %d'%acmsets(t7,len(L)),
  'executable code: delay_ms(1) = 6',
  'executable code: delay_ms(2) = 0',
  'executable code: SetClamp(50, 50) = 2',
  'executable code: MeasureVI(200, 5, FPVIe_MV_X10) = 2',
  'executable code: bare 126 tokens = 0',
  'executable code: K126_V1P5_CAP = 2',
  'executable code: ERROR_RES = 2',
  'executable code: K5_VBUS_Cap + K44_Cap_SW2_BST2 + K45_Cap_SW1_BST1 = 0',
  'executable code: K57_CAP_BST_SW = 2',
  'cbite.SetOn calls = 2',
  'BOM present = 1; lone LF = 0; CRLF pairs = 566'],
 'revisionBoundInventoryWarning':('This inventory is REVISION-BOUND. An earlier generation (39,457 B / 2d0984d9... ) carried '
  'K109_BUSL1_PB0 = 1 and K110_ACM18_BST = 1 and did NOT carry K48/K76; a receipt quoting those counts describes that '
  'generation, not this one. Recompute every key on the current bytes before certifying.')},
 {'artefact':'t29-k110-evidence.md','size':13978,
  'sha256':'b8e400ca14f37ff9c355c692e0c52562ae4efef96fc6296532dc40588f1d948e',
  'mtime':'2026-09-16 20:11:00',
  'revisionNote':'Evidence/commentary artefact, not a deliverable. Re-measured at the revision above.',
  'revisionBoundInventoryWarning':('Its per-function rationale and revision history are point-in-time. Quote it for reasoning, '
  'not for current counts.')},
 {'artefact':'APPLY-TM600-TM601.md','size':7110,
  'sha256':'429ad881d67d3feb6886ca5006dbf663cf025a91025545d988f8cdc446f6dfa1','mtime':None,
  'revisionNote':('STALE BY DESIGN AND FLAGGED: its payload-hash row predates the t38 revision and has NOT been refreshed. '
  'The landing owner must refresh it at landing. Do not treat this hash as current.'),
  'revisionBoundInventoryWarning':'Instructional document; its embedded hash is known-stale.'}]

# --- removed from the authoritative list: t40 evidence was never MY artefact and has drifted ---
h['withdrawnFromAuthoritativeList']=[{
 'artefact':'t40-tm601-bst-evidence.md',
 'why':('REMOVED from authoritativeCurrentValues: it is ANOTHER MEMBER\'S evidence artefact, and its recorded value '
  '(11,691 B / de6bb17f...) no longer matches disk (12,921 B / 71c5b9ea9809a2d00853273ba557cac13dd4b37d442212c3176e1ffd0979da30 @20:15:48). '
  'I can vouch for MY artefacts; I cannot certify the drift history of someone else\'s. Referenced by path and owner only.'),
 'disposition':'Cite by path; recompute before use; the owning member owns its content.'}]

# --- t4's reader rule, ADDED not flipped, cited by path + owner, no hardcoded measurements ---
h['readerNoteOldRelaySetShorthand']={
 'rule':('Readers of the t42 / t44 family (and of t43 harness notes): any [48,61,76] there is the OLD INCOMPLETE SHORTHAND '
  '(it omits the SW side K60). The authoritative closed set is [48,60,61,76] (BST [48,76] in the ACM200 family / SW [60,61] '
  'in FPVIe[L]); the gate expectation is {48,60,61,76,83}. Cite those, not the shorthand.'),
 'whyItMatters':('A stale wording WITHOUT an in-band annotation reads as a live target; a stale wording WITH an in-band label '
  'is a record and may be kept. The criterion is the in-band annotation, not the mere presence of the old string.'),
 'source':('Shared practice across both sides: test-strategy-architect note section 2.5 plus the rule-reviewer t55 correction file. '
  'Not attributable to a single author.'),
 'citationDiscipline':('Cite these documents by PATH and OWNER, never by a hardcoded size or hash: a pinned measurement of a moving '
  'artefact becomes a new drift source. (Observed instance: a mirror size recorded as 97,636 B while the live file is far larger and '
  'still growing.)')}

open(mp,'wb').write((json.dumps(M,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
after=open(mp,'rb').read()
print('manifest %d B -> %d B / %s'%(len(before),len(after),hashlib.sha256(after).hexdigest()))
J=json.loads(after.decode('utf-8'))
hh=J['handoffCitationRisk']
print('  authoritativeCurrentValues now: %d entries'%len(hh['authoritativeCurrentValues']))
for e in hh['authoritativeCurrentValues']:
    print('    %-38s %7d B'%(e['artefact'],e['size']))
print('  added readerNoteOldRelaySetShorthand:', 'readerNoteOldRelaySetShorthand' in hh)
print('  added withdrawnFromAuthoritativeList:', 'withdrawnFromAuthoritativeList' in hh)