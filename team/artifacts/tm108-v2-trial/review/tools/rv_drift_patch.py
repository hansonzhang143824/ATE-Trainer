# -*- coding: utf-8 -*-
import os, json, hashlib, sys

R = r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\tm108-v2-trial\review'
PJ = os.path.join(R, 't8-review-findings.json')
PM = os.path.join(R, 't8-review-findings.md')

# ---------------- JSON ----------------
s = open(PJ, 'rb').read().decode('utf-8')

DRIFT = '''  "revisionDrift": {
    "status": "CRITICAL RECORD - the reviewed artifacts were rewritten by another party WHILE this review was running",
    "reviewedRevision": {
      "testCpp": { "sha256_plaintext": "b79b911a65a33abd62697f8576bd04b5022194751c9bfc5b174ecdab96d05d5a", "bytes": 477123, "crlf": 9434, "mtimeLocal": "2026-09-17 21:29:56", "preservedAt": "review/copy/test.cpp" },
      "implementationManifest": { "sha256_plaintext": "a4f5286da293f0e564849e37afce263e7bce38d08753503189a25e1bcbeba556", "bytes": 25688 }
    },
    "observedLiveRevision": {
      "testCpp": { "sha256_plaintext": "456fba2ce30aea904ed852175dad5724cea06347d989beff0b7af752dc486eaa", "bytes": 477760, "crlf": 9440, "bareLf": 3, "bom": true, "mtimeLocal": "2026-09-17 21:39:39", "preservedAt": "review/copy/test.cpp.r2-live" },
      "implementationManifest": { "sha256_plaintext": "58c54c48d1d72177551b32463ea62133a105fad4883f838a15e669d42638778e", "bytes": 41935, "mtimeLocal": "2026-09-17 21:41:13", "deviations": ["DEV-1","DEV-2","DEV-3","DEV-4","DEV-5","DEV-6","DEV-7"], "selfChecksCount": 13, "openItemsCount": 15 },
      "manifestMovedTwiceInsideTheReviewWindow": "25688 B (a4f5286d...) -> 36494 B (26171fca...) -> 41935 B (58c54c48...), i.e. the manifest was still being rewritten between two consecutive verification reads",
      "bindingToObservedLiveRevisionHolds": true,
      "bindingNote": "the NEW manifest changes[0].afterSha256 == 456fba2c... == the observed live file, so the new pair is internally consistent; but that pair is NOT the pair this review examined"
    },
    "consequence": "This review is a valid review of revision b79b911a... + manifest a4f5286d... only. The hash-bound pair I inspected no longer exists on disk, so the review cannot serve as the gate for the current disk state. See RF-05.",
    "repairsObservedInTheNewerRevision": {
      "RF-02": "REPAIRED. The unverified framework behaviour is now explicitly marked assumed: the new revision contains 'ASSUMED, NOT verified (compile-diagnostician's item)' (1x) and 'That behaviour is ASSUMED here and NOT verified' (1x), and BOTH old assertive strings are gone ('released implicitly with the cbite scope' 0x, 'the cbite scope ends with the function' 0x). This conforms to RF-02's repair condition (wording only; no release call added).",
      "RF-03": "REPAIRED. 'Step 4: Measure (library AWG ramp, capture on the observation candidate)' is present exactly once inside TM108, with a note recording why the sibling wording was deliberately not reused, so the item's step scheme is 1..6 again.",
      "RF-04": "NOT VERIFIED. RF-04 concerns numbers in t7-selfcheck.md and implementation-manifest.json, and both artifacts have been rewritten to states this review has not read. Its status must be re-checked in the next pass.",
      "RF-01": "NOT RESOLVED, and unresolvable by a code edit - by design it is a contract-vs-capability finding. Re-verified against the new revision: SetTestResult is still the only log-writing call anywhere in the file (188 raw / 187 in code), LogData is still 91 raw / 0 in code, the TM108 span still holds exactly 3 SetTestResult sites, and the logPlan-deferring comment is still present ('carried by the trace comments in this function' 1x, 'failureContext' 1x, 'bstSwStatus' 1x, 'sweepGeometry' 2x)."
    },
    "commentOnlyDisciplinePreservedOnTheNewRevision": "non-comment line sequence still identical to the pre-change backup (5628 items each), BOM present, bare LF still 3 - so the newer revision is still a comments-only change relative to the backup",
    "requiredAction": "Freeze a single revision, complete every repair, and re-run t8 against that frozen pair; no writes to test.cpp or the manifest may occur while the re-review is in flight."
  },

'''

anchor = '  "reviewStatus": "needs-revision",'
assert s.count(anchor) == 1
s = s.replace(anchor, DRIFT + anchor, 1)

RF05_ANCHOR = '''"note": "Non-blocking documentation defect. If the line convention is intentionally 0-based, saying so once in the manifest readerDiscipline block would close items (1) and (4)."
    }
  ],'''
assert s.count(RF05_ANCHOR) == 1
RF05 = '''"note": "Non-blocking documentation defect. If the line convention is intentionally 0-based, saying so once in the manifest readerDiscipline block would close items (1) and (4)."
    },
    {
      "id": "RF-05",
      "severity": "high",
      "TM": "TM108",
      "category": "process / gate integrity - the reviewed artifact was rewritten during the review, so no valid gate exists for the current revision",
      "blocking": true,
      "evidence": "The pair this review examined was test.cpp = b79b911a65a33abd62697f8576bd04b5022194751c9bfc5b174ecdab96d05d5a (477123 B, CRLF 9434, mtime 21:29:56) with implementation-manifest.json = a4f5286da293f0e564849e37afce263e7bce38d08753503189a25e1bcbeba556 (25688 B). During this review - not by me, I wrote only under team/artifacts/tm108-v2-trial/review/ - test.cpp was replaced by 456fba2ce30aea904ed852175dad5724cea06347d989beff0b7af752dc486eaa (477760 B, CRLF 9440, mtime 21:39:39) and the manifest was rewritten TWICE, observed as 25688 B (a4f5286d...) then 36494 B (26171fca...) then 41935 B (58c54c48..., mtime 21:41:13), the last happening between two consecutive verification reads of mine. Both revisions are preserved for audit: review/copy/test.cpp (as reviewed) and review/copy/test.cpp.r2-live (as newly observed). The newer pair is internally consistent (its changes[0].afterSha256 equals the newer live file), but it is NOT the pair this review examined, and my gate G-01/G-02/G-03 hash binding therefore no longer describes the state on disk. A reviewer cannot pass a gate on an artifact that is being rewritten underneath it, and the newest manifest may itself have been superseded after my last read (RR-14). I did re-verify against the newer revision where I could: RF-01 is unresolved there too (SetTestResult still the only log-writing call, 187 in code; LogData 0 in code; 3 SetTestResult sites in the TM108 span; the logPlan-deferring comment intact), and RF-02 and RF-03 are repaired there.",
      "violatedRule": "team/ROLE_ROUTING.md:32-34 (a role must validate a handoff against the declared artifacts and hashes, and a blocking verdict must stop the sequence) together with the t8 contract section 4.7, which makes the deliverable the hash-bound pair (code + manifest) and treats a manifest naming a different revision as a blocking finding rather than a formality; charter section 5 also requires the reviewer to be able to re-check the reviewed artifact by snapshot",
      "responsibleOwner": "captain (artifact freeze and dispatch discipline) with ate-implementer (the writer of both files)",
      "repairCondition": "Declare a single frozen revision (one test.cpp hash + one manifest hash), complete every remaining repair against it first, and make no further writes to test.cpp or implementation-manifest.json while the re-review is in flight; then re-run t8 on that frozen pair. The re-review must re-verify all of RF-01, RF-02, RF-03 and RF-04 plus the hash binding on the frozen revision, because this review's own evidence is anchored to b79b911a... and cannot be carried over automatically.",
      "note": "This finding is not a criticism of the code content - it is the reason the review cannot be closed as a pass. It is reported by me rather than silently absorbed because treating an older revision's review as the gate for a newer revision is exactly the failure mode the hash binding exists to prevent."
    }
  ],'''
s = s.replace(RF05_ANCHOR, RF05, 1)

RR_ANCHOR = 'Closing action: compile-diagnostician records the include path actually used.", "ownerToVerify": "compile-diagnostician" }'
assert s.count(RR_ANCHOR) == 1
s = s.replace(RR_ANCHOR, RR_ANCHOR + ''',
    { "id": "RR-14", "severity": "high", "subject": "the reviewed pair is no longer on disk, and the newest manifest was still changing when this review ended", "detail": "Both revisions are preserved (review/copy/test.cpp = as reviewed, review/copy/test.cpp.r2-live = as newly observed) but neither can be assumed current: the manifest was observed at three different sizes and hashes inside this review window (25688 B a4f5286d..., 36494 B 26171fca..., 41935 B 58c54c48...), so it may have been superseded again after my last read. Any consumer must re-hash test.cpp and implementation-manifest.json before acting on this review, and must not treat the RF-02/RF-03 repairs I observed as verified for whatever revision is current at the time of reading.", "ownerToVerify": "captain (freeze) + ate-implementer" }''', 1)

G_ANCHOR = '''. DMUX_SEL=22 is implemented as the signed value with the CSV counterpart recorded as not applied and F2 carried (test.cpp:2232-2234)."
    }
  ],'''
assert s.count(G_ANCHOR) == 1
s = s.replace(G_ANCHOR, '''. DMUX_SEL=22 is implemented as the signed value with the CSV counterpart recorded as not applied and F2 carried (test.cpp:2232-2234)."
    },
    {
      "id": "G-13",
      "name": "reviewed revision == revision currently on disk",
      "method": "python byte-mode sha256 of the live file and the manifest, compared against the pair this review examined, and re-checked across the review window",
      "status": "FAIL",
      "evidence": "The live file is 456fba2ce30aea904ed852175dad5724cea06347d989beff0b7af752dc486eaa (477760 B) and the manifest is 58c54c48d1d72177551b32463ea62133a105fad4883f838a15e669d42638778e (41935 B), while this review examined b79b911a... (477123 B) and a4f5286d... (25688 B). The manifest was observed at three distinct sizes/hashes during the window. The reviewed pair no longer exists on disk. See RF-05 and RR-14."
    }
  ],''', 1)

d = json.loads(s)
print('JSON valid. inputs=%d findings=%d risks=%d gates=%d status=%s' % (
    len(d['reviewedInputs']), len(d['findings']), len(d['residualRisks']), len(d['gateResults']), d['reviewStatus']))
print('  blocking findings:', [f['id'] for f in d['findings'] if f.get('blocking')])
open(PJ, 'wb').write(s.encode('utf-8'))
print('  JSON bytes=%d sha256=%s' % (os.path.getsize(PJ), hashlib.sha256(open(PJ, 'rb').read()).hexdigest()))

# ---------------- MD ----------------
t = open(PM, 'rb').read().decode('utf-8')

TOP = '''
> ### ⚠ REVISION DRIFT — the reviewed pair no longer exists on disk
>
> This review examined **`test.cpp` `b79b911a…d5a` (477123 B) + `implementation-manifest.json` `a4f5286d…556` (25688 B)**, preserved for audit at `review/copy/test.cpp`.
> **While the review was running — not by me; I wrote only under `review/` — `test.cpp` was replaced and the manifest was rewritten twice.**
>
> | | as reviewed | currently on disk (last read) |
> |---|---|---|
> | `test.cpp` | `b79b911a…d5a`, 477123 B, mtime 21:29:56 | **`456fba2c…eaa`, 477760 B, mtime 21:39:39** |
> | manifest | `a4f5286d…556`, 25688 B | **`58c54c48…78e`, 41935 B, mtime 21:41:13** |
>
> The manifest was observed at **three** sizes/hashes inside this window (`a4f5286d…` → `26171fca…` → `58c54c48…`). The newer pair is internally consistent, but it is **not** the pair this review examined, so **my hash binding no longer describes the state on disk** and this review cannot serve as the gate for the current revision. See **`RF-05`**, gate **`G-13`**, risk **`RR-14`**, and the `revisionDrift` block in the JSON.
>
> Re-checked against the newer revision where I could: **`RF-02` and `RF-03` are repaired** there; **`RF-01` is not** (and cannot be — it is a contract-vs-capability finding); `RF-04` **not verified**. The terminal verdict is unchanged.
'''

mark = '## 1. Independence, read-only discipline and hash snapshot'
assert t.count(mark) == 1
t = t.replace(mark, TOP + '\n' + mark, 1)

# drift section + RF-05 before section 6 (waived findings)
DRIFTSEC = '''
## 5a. Revision drift — `RF-05`, `G-13`, `RR-14`

**What happened.** The deliverable is defined by the t8 contract §4.7 as the *hash-bound pair* (code + manifest). That pair moved under this review:

| | revision as reviewed | revision on disk at my last read |
|---|---|---|
| `test.cpp` | `b79b911a65a33abd62697f8576bd04b5022194751c9bfc5b174ecdab96d05d5a`, 477123 B, CRLF 9434, bare LF 3, mtime `21:29:56` | `456fba2ce30aea904ed852175dad5724cea06347d989beff0b7af752dc486eaa`, 477760 B, CRLF 9440, bare LF 3, mtime `21:39:39` |
| `implementation-manifest.json` | `a4f5286da293f0e564849e37afce263e7bce38d08753503189a25e1bcbeba556`, 25688 B | `58c54c48d1d72177551b32463ea62133a105fad4883f838a15e669d42638778e`, 41935 B, mtime `21:41:13` |
| manifest observed during the window | — | `a4f5286d…` → `26171fca…` (36494 B) → `58c54c48…` (41935 B) |

Both revisions are preserved for audit: `review/copy/test.cpp` (as reviewed) and `review/copy/test.cpp.r2-live` (as newly observed). I wrote to neither target file; every write of this task went under `team/artifacts/tm108-v2-trial/review/`.

**Consequence.** A reviewer cannot pass a gate on an artifact that is being rewritten underneath it, and the newest manifest may itself have been superseded after my last read (`RR-14`). The newer pair *is* internally consistent — its `changes[0].afterSha256` equals the newer live file — but it is not the pair I examined.

**What I re-verified against the newer revision.**

| Finding | Status in the newer revision |
|---|---|
| `RF-02` | **REPAIRED.** The new revision marks the framework behaviour as assumed — `ASSUMED, NOT verified (compile-diagnostician's item)` (1×) and `That behaviour is ASSUMED here and NOT verified` (1×) — and **both** old assertive strings are gone (`released implicitly with the cbite scope` 0×, `the cbite scope ends with the function` 0×). Conforms to the repair condition: wording only, no release call added. |
| `RF-03` | **REPAIRED.** `Step 4: Measure (library AWG ramp, capture on the observation candidate)` is present exactly once inside TM108, with a note recording why the sibling wording was deliberately not reused. The item's step scheme is 1..6 again (94 `Step 4: Measure` headings across the file). |
| `RF-04` | **NOT VERIFIED.** It concerns numbers in `t7-selfcheck.md` and `implementation-manifest.json`, and both have been rewritten to states this review has not read. Re-check in the next pass. |
| `RF-01` | **NOT RESOLVED**, and unresolvable by a code edit by design. Re-verified on the newer revision: `SetTestResult` is still the only log-writing call anywhere in the file (188 raw / **187 in code**), `LogData` still 91 raw / **0 in code**, the TM108 span still holds exactly **3** `SetTestResult` sites, and the logPlan-deferring comment is intact (`carried by the trace comments in this function` 1×, `failureContext` 1×, `bstSwStatus` 1×, `sweepGeometry` 2×). |
| comment-only discipline | **PRESERVED** on the newer revision: non-comment line sequence still identical to the pre-change backup (5628 items each), BOM present, bare LF still 3. |

**Required action.** Freeze a single revision, land every remaining repair, and re-run `t8` against that frozen pair — with no writes to `test.cpp` or the manifest while the re-review is in flight. This review's evidence is anchored to `b79b911a…` and cannot be carried over automatically.

**Finding `RF-05` (high, blocking, owner: captain for the artifact freeze, with `ate-implementer` as the writer of both files).** Violated rule: `ROLE_ROUTING.md:32-34` (a role must validate a handoff against the declared artifacts and hashes, and a blocking verdict stops the sequence) together with t8 contract §4.7, which makes the deliverable the hash-bound pair and treats a manifest naming a different revision as blocking. Repair condition as stated in the paragraph above.

'''
mark2 = '## 6. Waived findings'
assert t.count(mark2) == 1
t = t.replace(mark2, DRIFTSEC + mark2, 1)

# gate row
G_OLD = '| `G-11` | R3 §6 `logPlan` completeness |'
assert t.count(G_OLD) == 1
G_ROW = '''| `G-13` | Reviewed revision == revision currently on disk | **FAIL** | Live file is `456fba2c…eaa` (477760 B) and manifest `58c54c48…78e` (41935 B); this review examined `b79b911a…d5a` (477123 B) and `a4f5286d…556` (25688 B). The reviewed pair no longer exists on disk. See `RF-05`, `RR-14`. |
| `G-11` | R3 §6 `logPlan` completeness |'''
t = t.replace(G_OLD, G_ROW, 1)

# residual risk row
RR_OLD = '| `RR-12` | medium |'
assert t.count(RR_OLD) == 1
RR_ROW = '''| `RR-14` | **high** | The reviewed pair is no longer on disk and the newest manifest was **still changing** when this review ended (three distinct sizes/hashes in one window). Both revisions are preserved (`review/copy/test.cpp`, `review/copy/test.cpp.r2-live`) but neither may be assumed current. Any consumer must **re-hash `test.cpp` and the manifest before acting**, and must not treat the `RF-02`/`RF-03` repairs I observed as verified for whatever revision is current at read time. Owner: captain (freeze) + `ate-implementer`. |
| `RR-12` | medium |'''
t = t.replace(RR_OLD, RR_ROW, 1)

open(PM, 'wb').write(t.encode('utf-8'))
print('MD bytes=%d lines=%d sha256=%s' % (os.path.getsize(PM), t.count('\n') + 1,
                                          hashlib.sha256(open(PM, 'rb').read()).hexdigest()))
for probe in ('REVISION DRIFT', 'RF-05', 'G-13', 'RR-14', 'revisionDrift'):
    print('  contains %-16s %d' % (probe, t.count(probe)))
