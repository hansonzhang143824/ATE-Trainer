# -*- coding: utf-8 -*-
"""Record the cross-verified audit disciplines (D1..D6) in the dft-ir hash sidecar for t7/t9.

Does not touch dft-ir.json (frozen). Idempotent: re-running replaces the block.
"""
import json, os, hashlib, sys, datetime
sys.stdout.reconfigure(encoding='utf-8')

ROOT = r"D:/Newtest/DSH/ATE-Coding-Plat"
RUN = "acceptance-20260916-dali10"
SIDE = os.path.join(ROOT, 'team', 'artifacts', RUN, 'dft-raw', 'dft-ir-hashes.json')
ART = os.path.join(ROOT, 'team', 'artifacts', RUN, 'dft-ir.json')

RULE_MSG = ("never assert that a field is on disk from another party's stdout - re-read the file")

rep = json.loads(open(SIDE, encoding='utf-8-sig').read())
rep['t9HandoffDisciplines'] = {
    'why': 'this run produced at least 8 stale-hash incidents; these are the rules that survived cross-verification between dft-expert and ate-implementer',
    'rules': [
        {'id': 'D1', 'rule': 'with several writers on one sidecar, none may build from scratch - read-modify-write and preserve unknown keys',
         'origin': 'dft-expert writer-chain defect: dft_ir_hashes.py rebuilt the sidecar and silently dropped 4 auxiliary blocks'},
        {'id': 'D2', 'rule': RULE_MSG,
         'origin': 'cross-verified during the sidecar incident'},
        {'id': 'D3', 'rule': 'after changing a writer, prove survival by running the OTHER writers afterwards and re-reading (idempotence proof)',
         'origin': 'agreed in the dft-expert / ate-implementer thread'},
        {'id': 'D4', 'rule': 'never cite a number you printed earlier - re-read the file immediately before quoting it (complement of D2)',
         'origin': 'dft-expert quoted a writer-stdout value (20483 B / 4ebc1089...) in the very message where it had just stated this rule; that value is VOID'},
        {'id': 'D5', 'rule': 'match artifacts by sha256, never by a size-field name (deliverable.size and sizeBytes coexist in this run)',
         'origin': 'dft-expert; adopted as t9 reconciliation guidance'},
        {'id': 'D6', 'rule': 'a file regenerated inside this run is valid only at its measurement instant - schematic-ir.json and test-plan.json were rebuilt repeatedly',
         'origin': 'dft-expert; recorded in HASH-AUDIT.md'},
    ],
    'adoptedBy': {'party': 'ate-implementer', 'where': 'team/artifacts/%s/HASH-AUDIT.md' % RUN,
                  'note': 'that file reported 9403 B at adoption time; recompute before citing (D6 applies to it too)'},
    'voidValues': [{'value': 'dft-raw/dft-ir-hashes.json 20483 B / 4ebc1089...', 'status': 'VOID - writer stdout, not a disk read; do not cite'}],
    'recordedAt': datetime.datetime.now().astimezone().isoformat(timespec='seconds'),
}
with open(SIDE, 'w', encoding='utf-8') as f:
    json.dump(rep, f, ensure_ascii=False, indent=1)

b = open(SIDE, 'rb').read()
a = open(ART, 'rb').read()
print('sidecar', len(b), hashlib.sha256(b).hexdigest())
print('keys', len(rep.keys()), [k for k in rep.keys()])
print('dft-ir.json unchanged', len(a), hashlib.sha256(a).hexdigest())
print('sidecar deliverable.sha256 == live dft-ir:', rep['deliverable']['sha256'] == hashlib.sha256(a).hexdigest())
