# -*- coding: utf-8 -*-
"""t28 patcher 2 — 在 implementation-manifest.json 登记"生成后必须重放 meta 修正"(a) 项。

要求: 保留原文件的缩进/键序/行尾; 纯追加顶层键 (schema: additionalProperties 允许);
改后必须通过 `python scripts/validate_team_artifact.py implementation-manifest <file>`。
"""
import hashlib
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.abspath(os.path.join(HERE, '..'))
MANIFEST = os.path.join(RUN, 'implementation-manifest.json')

ANCHOR = '\n  "limitations": ['

BLOCK = '''
  "generationReplayRequirement": {
    "id": "a",
    "addedBy": "t28 (gate-guard task: input-sync RS-1..RS-4 + manifest registration)",
    "revision": "manifest-amendment-1",
    "statement": "MANDATORY: after ANY regeneration of project/DALI/meta/dali_tm_meta.json (or test_conditions.yaml), the run-scope meta corrections of this run MUST be replayed, and scripts/check_input_sync.py MUST be re-run before the gates are trusted.",
    "why": "Measured, not assumed: a plain rerun of scripts/gen_testitems_meta.py restores the PRE-override meta byte for byte (probe team/artifacts/acceptance-20260916-dali10/t26-regen-probe/dali_tm_meta.regen.json = 146180 B / 1c8496645492f7b75abf3a89f95679291490399d62f4a1a34d6cc5d8b1aa2693). That silently erases (i) the TM601 powered_pins VBUS removal, (ii) the TM600/TM601 mi_pins corrections, (iii) the frozen-ATE hardwareInit alignment. Before t28 the input-sync gate could NOT see this: its two links (meta._syncStamp.dftSha256 / yaml._sync.metaSha256) are refreshed in the same regeneration pass, so it still printed IN SYNC with exit 0.",
    "replayOrder": [
      "1) python scripts/gen_testitems_meta.py   (regenerate meta from the DFT intent layer)",
      "2) python scripts/gen_test_conditions.py (regenerate yaml; its _sync stamp is refreshed in the same pass)",
      "3) RE-APPLY the run-scope override so that TM600_HS_RDSON / TM601_LS_RDSON match meta-excitation-override.json (ATE stimulus alignment; TM601 powered_pins without VBUS; mi_pins TM600=[SW], TM601=[PMID_SW,SW])",
      "4) VERIFY: python scripts/check_input_sync.py must print IN SYNC with exit 0 - the RS assertions (RS-1..RS-4) are the detector for a missed replay"
    ],
    "detector": {
      "script": "scripts/check_input_sync.py",
      "assertions": "RS-1..RS-4 (group RS)",
      "spec": "team/artifacts/acceptance-20260916-dali10/meta-excitation-override.json -> recommendedGateAssertions",
      "onFailureStatus": "RS-FAIL",
      "classification": "RS-FAIL is counted as NEW-RED in the gate summary and forces exit 1 (it is NOT a warning and NOT a baseline-exempt known red)"
    },
    "redProofEvidence": {
      "harness": "team/artifacts/acceptance-20260916-dali10/gate-logs-t28/t28_red_proof.py",
      "result": "same reverted input: pre-t28 gate => IN SYNC / exit 0 (undetectable); post-t28 gate => OUT OF SYNC / exit 1 with RS-FAIL on RS-1, RS-2, RS-3",
      "logBeforeFixed": "team/artifacts/acceptance-20260916-dali10/gate-logs-t28/redproof-before-fix.log",
      "logAfterFixed": "team/artifacts/acceptance-20260916-dali10/gate-logs-t28/redproof-after-fix.log",
      "probeSha256": "1c8496645492f7b75abf3a89f95679291490399d62f4a1a34d6cc5d8b1aa2693"
    },
    "scopeNote": "This registration changes documentation only: no source, no meta, no target tree, no gate baseline was modified by t28. The meta file itself (project/DALI/meta/dali_tm_meta.json) remains OUTSIDE the tasked scope and is untouched."
  },
'''


def main():
    raw = open(MANIFEST, 'rb').read()
    bom = raw[:3] == b'\xef\xbb\xbf'
    t = raw.decode('utf-8-sig')
    if '--verify-only' in sys.argv:
        print('  anchor 命中 %d 次' % t.count(ANCHOR))
        print('  已存在 generationReplayRequirement: %s' % ('generationReplayRequirement' in t))
        return
    if 'generationReplayRequirement' in t:
        raise SystemExit('ERROR: manifest 已包含 generationReplayRequirement, 拒绝重复插入')
    if t.count(ANCHOR) != 1:
        raise SystemExit('ERROR: anchor 命中 %d 次 (应 1)' % t.count(ANCHOR))
    old = json.loads(t)          # 改前必须是合法 JSON
    t2 = t.replace(ANCHOR, BLOCK + ANCHOR)
    new = json.loads(t2)         # 改后必须仍是合法 JSON
    assert set(old.keys()) - set(new.keys()) == set(), '键丢失!'
    assert set(new.keys()) - set(old.keys()) == {'generationReplayRequirement'}
    out = t2.encode('utf-8')
    if bom:
        out = b'\xef\xbb\xbf' + out
    with open(MANIFEST, 'wb') as f:
        f.write(out)
    print('PATCHED %s\n  before=%s (%d B, %d keys)\n  after =%s (%d B, %d keys)\n  bom=%s crlf=%d'
          % (MANIFEST, hashlib.sha256(raw).hexdigest(), len(raw), len(old),
             hashlib.sha256(out).hexdigest(), len(out), len(new), bom, out.count(b'\r\n')))


if __name__ == '__main__':
    main()
