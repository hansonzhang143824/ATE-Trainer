# -*- coding: utf-8 -*-
"""Record the captain's 'IR frozen — no fifth revision' decision in the hash sidecar ONLY.

Does NOT rebuild dft-ir.json (captain instruction: avoid further hash churn). This script
documents the provenance of every published dft-ir.json digest, corrects the v4 identification
in the captain's ledger entry, and carries the two late-arriving rulings (BD-04 closed,
BD-05 closed by user ruling) as "authoritative elsewhere" pointers.
"""
import os, json, hashlib, sys, datetime
sys.stdout.reconfigure(encoding='utf-8')

ROOT = r"D:/Newtest/DSH/ATE-Coding-Plat"
RUN = "acceptance-20260916-dali10"
ART = os.path.join(ROOT, 'team', 'artifacts', RUN, 'dft-ir.json')
SIDE = os.path.join(ROOT, 'team', 'artifacts', RUN, 'dft-raw', 'dft-ir-hashes.json')

b = open(ART, 'rb').read()
cur = hashlib.sha256(b).hexdigest()
d = json.loads(open(ART, encoding='utf-8').read())

rep = json.load(open(SIDE, encoding='utf-8-sig'))
rep['deliverable']['sha256'] = cur
rep['deliverable']['sizeBytes'] = len(b)
rep['deliverable']['frozenBy'] = ('captain decision, 2026-09-16: NO fifth IR revision (avoid further hash churn). '
                                  'Late rulings are carried by test-plan.json (user rulings) and RUN-LEDGER.md (ruling ledger); '
                                  't9 must not treat this IR\'s blockingDecisions.open as the final state.')
rep['hashHistory'] = [
  {'revision': 'v1', 'sha256': 'f3faedc26675a4ad06d66569c19ec17ee1c06211336eb4feba4fb40e30d2e3c8', 'sizeBytes': 88109,
   'note': 'first build (t1 handoff)'},
  {'revision': 'v2', 'sha256': '478f88a4576a4ca269705737b1859064d96b18f9c0eedfe1d3af764ea5a0f755', 'sizeBytes': 88101,
   'note': 'TM1205 md hash corrected'},
  {'revision': 'v3', 'sha256': '85db02e38d49803e174c8c5645471041ea62911e651bafb9efd6dc777469521e', 'sizeBytes': 99058,
   'note': 'captain follow-up (PA-01/PA-02, plaintext anchors, CR-01 symbols, MV&MI)'},
  {'revision': 'v4', 'sha256': '0a1c3b1e474c508c63d639d69e3b905ce94cb5b8085c98745c05a6625669597e', 'sizeBytes': 107133,
   'note': 'implementer-review response (forceAndSense split, DD-01, C-03 corroboration)'},
  {'revision': 'v5', 'sha256': '82398d2f882abc2bc452ed307e47ae64ff25d7a13553abfe61b73fdd04d0d568', 'sizeBytes': 116140,
   'note': 'post-ruling R-01..R-05 (BD-01/02/03 closed, DD-01 closed, FS-01 narrowed)'},
  {'revision': 'v6-CURRENT', 'sha256': cur, 'sizeBytes': len(b),
   'note': 'captain fourth augmentation (CR-02..CR-06 ruling records, TM601 PGND-High/SW-Low polarity + fixture evidence, FS-01 resolved)'},
]
rep['provenanceCorrection'] = {
  'issue': ('the captain ledger registered "v4 = 116140 B / 82398d2f…" and described v4 as still carrying '
            'items.TM601.forceAndSense.force.pins=[PMID,SW] with consistentWithCheckNode=false'),
  'correction': ('82398d2f… (116140 B) is the v5 revision. The actual current artifact is %s (%d B), which already contains '
                 'the captain fourth augmentation: CR-02..CR-06, force.pins=[PGND (High), SW (Low)], the SUPERSEDED-BY-RULING '
                 '.sv notation (kept verbatim), fixtureEvidence from schematic-ir.json paths[], and FS-01=resolved-with-fixture-evidence.'
                 % (cur[:16], len(b))),
  'action': 'mirror this table into RUN-LEDGER.md; always re-hash before citing',
}
rep['lateRulingsNotInIR'] = [
  {'id': 'BD-04', 'irState': 'open (in conflicts C-02 and blockingDecisions)', 'authoritativeState': 'CLOSED by captain ruling',
   'ruling': 'TM108/TM109 rising threshold = OVERVIEW 4.4 V; DFT.csv 4.15 V retained verbatim as a registered conflict',
   'basis': 'same authority rule as the user BD-01 ruling, reinforced by the DFT.csv TM109 row being self-contradictory (ramps vac3 for a VAC2_PRST item, DMUX copied from TM108)',
   'carriedBy': ['team/artifacts/%s/test-plan.json (t4, user rulings authoritative)' % RUN, 'RUN-LEDGER.md'],
   'note': 'stated by the captain as an analogy to the user criterion and therefore overridable by the user'},
  {'id': 'BD-05', 'irState': 'open (built before the ruling — lag, not disagreement)', 'authoritativeState': 'CLOSED by user ruling',
   'ruling': 'golden SetClamp(50,50) re-issued after every FV/FI switch, +/-0.5 V compliance, provisional engineering default, not a pass/fail criterion, no hardware run, production tree untouched',
   'carriedBy': ['team/artifacts/%s/test-plan.json (t4)' % RUN, 'RUN-LEDGER.md'],
   'note': 'captain decided not to request a fifth IR revision; if one is ever made, add a notices entry only — do not rebuild the body'},
]
rep['notRebuilt'] = {'reason': 'captain instruction: no fifth revision', 'artifactUntouched': True,
                     'generatedAt': datetime.datetime.now().astimezone().isoformat(timespec='seconds')}
with open(SIDE, 'w', encoding='utf-8') as f:
    json.dump(rep, f, ensure_ascii=False, indent=1)
print('sidecar updated (artifact untouched):', SIDE)
print('current digest', cur, len(b))
