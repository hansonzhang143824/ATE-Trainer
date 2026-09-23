import sys,io,os,json,hashlib,time
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
ap=os.path.join(d,'APPLY-TM600-TM601.md')
before=open(ap,'rb').read()
b_sha=hashlib.sha256(before).hexdigest()
print('=== BEFORE ===')
print('  %d B / %s'%(len(before),b_sha))
txt=before.decode('utf-8-sig')
print('  ends with newline:', txt.endswith('\n'))
print('  contains old-shorthand markers: [48,61,76]=%d | [48,60,61,76]=%d | {48,60,61,76,83}=%d'%(
  txt.count('[48,61,76]'),txt.count('[48,60,61,76]'),txt.count('{48,60,61,76,83}')))
print('  line ending style: CRLF=%d loneLF=%d'%(before.count(b'\r\n'),before.count(b'\n')-before.count(b'\r\n')))

section = '''

---

## READER RULE — which relay set is the current target (added, append-only)

**Cite these values, not any shorthand.**

- **Authoritative closed set = `[48,60,61,76]`** — BST side `[48,76]` in the ACM200 family, SW side `[60,61]` in the FPVIe[L] family (**it includes `K60`**).
- **Gate expectation = `{48,60,61,76,83}`** (the union of the two aliases the gate reads: `pmid2sw {83,60,61}` and `bst2sw {48,60,61,76}`).
- **Historical shorthands are not targets.** `[48,61,76]` is the **old incomplete shorthand** — it omits the SW side's `K60`. `[110,61]` is the earlier cross-family pair, incomplete under either reading.

**Why this matters:** a stale wording that carries an in-band label is a *record* and may be kept; a stale wording **without** one reads as a *live target*. The criterion is the annotation, not the mere presence of the old string.

**Why a reader rule is needed at all:** the gate performs a **subset** check, so it cannot see either a **missing member** of the expectation set or **extra closures**. Defects of that class cannot be caught at the gate layer and must be caught in writing or review — which is what this rule does.

**Citation discipline:** cite this document and the plan/contract **by path and owner, and recompute at use time**. Do not treat any size or hash printed in it as current — a pinned measurement of a moving artefact becomes a new source of drift.

**Source:** shared practice across the review, plan and implementation sides, not attributable to a single author. **Payload note:** the frozen payload closes the ch5 set and contains no `K109`/`K110`.

**[SUPERSEDED, retained as history]** The payload-hash row earlier in this document predates the `t38` revision and is **not** current. The landing owner must refresh it at landing. This is recorded rather than deleted, so the trail shows it was once wrong and was flagged.
'''
after=(txt+section).replace('\r\n','\n').replace('\n','\r\n').encode('utf-8')
open(ap,'wb').write(after)
r2=open(ap,'rb').read()
print()
print('=== AFTER ===')
print('  %d B / %s'%(len(r2),hashlib.sha256(r2).hexdigest()))
print('  CRLF=%d loneLF=%d'%(r2.count(b'\r\n'),r2.count(b'\n')-r2.count(b'\r\n')))
t2=r2.decode('utf-8-sig')
print('  new section present:', 'READER RULE' in t2)
print('  no new hardcoded hash in appended text:', hashlib.sha256(r2).hexdigest() not in t2)

# update my manifest entry for APPLY
mp=os.path.join(d,'implementation-manifest.json')
M=json.loads(open(mp,'rb').read().decode('utf-8-sig'))
for e in M['handoffCitationRisk']['authoritativeCurrentValues']:
    if e['artefact']=='APPLY-TM600-TM601.md':
        e['size']=len(r2); e['sha256']=hashlib.sha256(r2).hexdigest()
        e['mtime']=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(os.stat(ap).st_mtime))
        e['revisionNote']=('Instructional document. A READER RULE section was APPENDED (append-only; no existing line '
         'modified, no history rewritten) stating the authoritative closed set, the gate expectation, and the citation '
         'discipline. The payload-hash row is still known-stale and flagged; the landing owner refreshes it at landing.')
open(mp,'wb').write((json.dumps(M,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
mr=open(mp,'rb').read()
print()
print('=== manifest updated ===')
print('  %d B / %s'%(len(mr),hashlib.sha256(mr).hexdigest()))
for e in json.loads(mr.decode('utf-8'))['handoffCitationRisk']['authoritativeCurrentValues']:
    print('    %-38s %7d B / %s'%(e['artefact'],e['size'],e['sha256'][:16]))