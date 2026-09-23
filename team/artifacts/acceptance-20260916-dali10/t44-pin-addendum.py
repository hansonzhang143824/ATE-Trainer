#!/usr/bin/env python3
"""t44 hash pin for the t42 addendum. Reads/writes only run-directory files."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

RUN = Path("team/artifacts/acceptance-20260916-dali10")
MD = RUN / "t44-t42-addendum.md"
T42 = RUN / "t42-acm200-pin-attribution.md"


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


pin = {
    "runId": "acceptance-20260916-dali10",
    "task": "t44",
    "producedBy": "schematic-expert",
    "purpose": ("Hash pin for the t42 addendum. Records that t42's verdict artefact was NOT modified "
                "(its reported hash stays valid) and that this addendum carries the hardening evidence "
                "for t43's independent review."),
    "hashMethod": ("sha256 over the file's raw bytes, read through python. The DALI sources are "
                   "DLP-transparent-encrypted, so PowerShell sees ciphertext; all hashes here are "
                   "python-plaintext/byte hashes. Measured at the timestamp below."),
    "measuredAt": datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds"),
    "addendum": {
        "path": "team/artifacts/acceptance-20260916-dali10/t44-t42-addendum.md",
        "size": MD.stat().st_size,
        "sha256": sha(MD),
    },
    "unchangedVerdictArtefact": {
        "path": "team/artifacts/acceptance-20260916-dali10/t42-acm200-pin-attribution.md",
        "size": T42.stat().st_size,
        "sha256": sha(T42),
        "note": "byte-identical to the hash reported when t42 completed; t44 did not touch it",
    },
    "verdictCarriedForward": ("SW12_U1REF_BST_ACM drives ACM200 channel 5 -> BST needs [48,76]; K110 is "
                              "not required for this instrument. BST-SW closed set = [48,61,76]."),
    "evidenceLayersAdded": [
        "Layer 1 behavioural: test.cpp:7000/7087/7170/7513 close K48_ACM5_AMP_REF+K76_ACM_BST; "
        ":6997/:7598/:7621 name SW12_U1REF_BST_ACM and ACM200_FH5 together",
        "Layer 3 documentation: exhaustive enumeration of source-attributed BST macros - ACM200 ones are "
        "K_BST_ACM=[48,76] and K_BST2_ACM=[43]; every K110-bearing macro is FPVIe[L] or QVM[L]; "
        "K_BST_ACM has 0 call sites (intent, not behaviour)",
        "Layer 5 control group: macro channel == ACM alias number == netlist pin suffix for 5/5 instruments",
        "Layer 4 separation: ch5 net has no K110; ch18 net has no K48/K76",
    ],
    "correctionIssued": ("'current SetOn closes K109/K110' holds for the PAYLOAD "
                         "(implementation-payload-TM600-TM601.cpp:219, sha 2d0984d992d5d8cb..., 39,457 B) "
                         "but NOT for the deployed tree (test.cpp:9081, sha 15c7d2b8d37b1564..., 469,714 B, "
                         "closes neither 48/76 nor 109/110). Payload = wrong leg + missing leg; deployed = "
                         "missing leg only."),
    "noteForT43": ("Review t42 together with this addendum. t42's own hash is unchanged, so any earlier "
                   "recomputation of it still holds; cite this addendum's hash for the added evidence. "
                   "The two UNKNOWNs that need a ruling (not mine to decide): whether TM600/TM601 must drive "
                   "BST from ACM200 at all, and whether switching to PB0_BST_ACM (ch18) + [110] is permitted."),
}

out = RUN / "t44-t42-addendum-pin.json"
out.write_text(json.dumps(pin, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("wrote", out)
print("addendum sha256 :", pin["addendum"]["sha256"], pin["addendum"]["size"])
print("t42 sha256      :", pin["unchangedVerdictArtefact"]["sha256"], pin["unchangedVerdictArtefact"]["size"])
