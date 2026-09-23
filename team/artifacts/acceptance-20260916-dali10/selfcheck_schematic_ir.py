#!/usr/bin/env python3
"""Self-check the generated schematic IR: evidence hashes, coverage, section sanity."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(".").resolve()
IR = ROOT / "team" / "artifacts" / "acceptance-20260916-dali10" / "schematic-ir.json"
d = json.loads(IR.read_text(encoding="utf-8"))

checked = 0
problems: list = []
drift_notices: list = []

# Evidence records owned by another agent and regenerated during the run: a byte-hash drift there is
# expected and reported as a notice, unless the anchored claim digest also moves. Content drift on a
# mutable path is still a hard failure, caught by the claimDigest re-check below.
mutable_paths = {
    m["path"] for m in d.get("validation", {}).get("evidenceStability", {}).get("mutableEvidence", [])
}
anchors: dict = {}


def walk(o) -> None:
    global checked
    if isinstance(o, dict):
        if {"path", "sha256", "locator"} <= set(o):
            checked += 1
            s = str(o["sha256"])
            path = o["path"]
            if not re.fullmatch(r"[A-Fa-f0-9]{64}", s):
                problems.append(("badhex", path, s[:24]))
            else:
                p = Path(path)
                if not p.is_file():
                    problems.append(("missing-file", path))
                else:
                    h = hashlib.sha256(p.read_bytes()).hexdigest()
                    if h != s.lower():
                        if path in mutable_paths:
                            drift_notices.append(("byte-drift-expected", path, f"pinned={s[:12]}", f"now={h[:12]}"))
                        else:
                            problems.append(("hash-mismatch", path, h[:12], s[:12]))
        if "claimDigest" in o and "claims" in o:
            anchors[o["path"]] = o
        for v in o.values():
            walk(v)
    elif isinstance(o, list):
        for v in o:
            walk(v)


def verify_anchors() -> None:
    """Re-derive each anchored claim set from the live file and compare digests."""
    for path, rec in anchors.items():
        p = Path(path)
        if not p.is_file():
            problems.append(("anchor-missing-file", path))
            continue
        try:
            doc = json.loads(p.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            problems.append(("anchor-unreadable", path, str(exc)[:60]))
            continue
        live = {}
        items = {i.get("tm"): i for i in doc.get("items", [])}
        for tm in ("TM600", "TM601"):
            chans = items.get(tm, {}).get("channels", [])
            live[f"{tm}.forcePins"] = chans[0].get("pins") if chans else None
            live[f"{tm}.iset"] = [
                {"pin": s.get("pin"), "value": s.get("value"), "unit": s.get("unit")}
                for s in items.get(tm, {}).get("stimuli", []) if s.get("kind") == "iset"
            ]
        live["conflictIds"] = sorted(c.get("id") for c in doc.get("conflicts", []) if c.get("id"))
        live["ruledPairMarker"] = "sw2pgnd" in p.read_text(encoding="utf-8")
        digest = hashlib.sha256(json.dumps(live, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()
        if digest != rec["claimDigest"]:
            problems.append(("claim-digest-mismatch", path, f"pinned={rec['claimDigest'][:12]}", f"now={digest[:12]}"))
            for k in sorted(set(live) | set(rec["claims"])):
                if live.get(k) != rec["claims"].get(k):
                    problems.append(("claim-changed", path, k, f"pinned={rec['claims'].get(k)!r}"[:90],
                                     f"now={live.get(k)!r}"[:90]))
        else:
            drift_notices.append(("claim-digest-verified", path, rec["claimDigest"][:12]))

        # The digest comparison above only proves live == pinned, which is trivially true for a record the
        # build just wrote. These expectation asserts are what actually makes the anchor discriminating:
        # they encode what THIS IR claims about the DFT artefact, independently of when it was built.
        for key, expected in (rec.get("expectations") or {}).items():
            if live.get(key) != expected:
                problems.append(("expectation-violated", path, key,
                                 f"expected={expected!r}"[:90], f"live={live.get(key)!r}"[:90]))
        for cid in rec.get("expectationConflicts") or []:
            if cid not in live.get("conflictIds", []):
                problems.append(("expectation-violated", path, f"conflict {cid}", "expected present",
                                 f"live={live.get('conflictIds')!r}"[:90]))
        for tm, pin, value, unit in rec.get("expectationIset") or []:
            found = [s_ for s_ in live.get(f"{tm}.iset", []) if s_.get("pin") == pin]
            if not found or found[0].get("value") != value or found[0].get("unit") != unit:
                problems.append(("expectation-violated", path, f"{tm}.iset[{pin}]",
                                 f"expected={value}{unit}", f"live={found!r}"[:90]))


walk(d)
verify_anchors()
print("evidence entries checked:", checked, "| problems:", problems)
print("notices on mutable, other-owned evidence:", drift_notices or "none")
print("nets without members:", [n["name"] for n in d["nets"] if not n["members"]])
print("components without pins:", [c["designator"] for c in d["components"] if not c["pins"]])
print("paths missing resources key:", [p["id"] for p in d["paths"] if "resources" not in p])
print("paths with non-list resources:", [p["id"] for p in d["paths"] if not isinstance(p["resources"], list)])
print("derived paths:", [(p["id"], p["confidence"]) for p in d["derivedPaths"]])
print("discharge:")
for x in d["discharge"]:
    print("  ", x["rail"], x["cap"]["designator"], x["cap"]["value"],
          "| gate", x["gatingRelay"], "|", (x.get("gatingRelayDefaultState") or "")[:48])
    print("     bleedToAgndF=", [f'{b["designator"]}={b["value"]}' for b in x["bleedToAgndF"]],
          "| rc=", x["rcViaBleedToGround"],
          "| rcSeries=", x.get("rcUpperBoundViaSeriesPath"))
print("hazard kinds:", sorted({h["kind"] for h in d["hazards"]}))
print("hazards count:", len(d["hazards"]))
print("openQuestions:", len(d["openQuestions"]), "| unresolvedTopology:", len(d["unresolvedTopology"]))
print("scope:", d["scope"])
print("scope pin coverage:", d["validation"]["scopePinCoverage"])
print("file size:", IR.stat().st_size)
