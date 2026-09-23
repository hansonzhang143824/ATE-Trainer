#!/usr/bin/env python3
"""Negative tests for the cross-owned evidence anchor.

Proves the anchor is not a rubber stamp:
  A) the live dft-ir.json satisfies the expectations this IR asserts;
  B) unrelated-field churn does NOT move the content digest;
  C) reverting the ruled TM601 polarity DOES move the digest AND trips an expectation assert;
  D) changing the TM600 1 A iset DOES trip an expectation assert.

The tampering is done on in-memory copies and on a scratch copy written under this run directory;
dft-ir.json itself (owned by dft-expert) is never modified.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(".").resolve()
RUN = ROOT / "team/artifacts/acceptance-20260916-dali10"
IR = RUN / "schematic-ir.json"
DFT = RUN / "dft-ir.json"
SCRATCH = RUN / "schematic-validation/_anchor_negative_test_scratch.json"


def find_anchor(o):
    if isinstance(o, dict):
        if o.get("claimDigest") and "claims" in o and str(o.get("path", "")).endswith("dft-ir.json"):
            return o
        for v in o.values():
            r = find_anchor(v)
            if r:
                return r
    elif isinstance(o, list):
        for v in o:
            r = find_anchor(v)
            if r:
                return r
    return None


anchor = find_anchor(json.loads(IR.read_text(encoding="utf-8")))
assert anchor, "no anchored evidence record in the IR"

dft_bytes_before = hashlib.sha256(DFT.read_bytes()).hexdigest()
doc = json.loads(DFT.read_text(encoding="utf-8"))


def derive(d: dict, raw_len_note: bool = True) -> dict:
    items = {i.get("tm"): i for i in d.get("items", [])}
    live = {}
    for tm in ("TM600", "TM601"):
        chans = items.get(tm, {}).get("channels", [])
        live[f"{tm}.forcePins"] = chans[0].get("pins") if chans else None
        live[f"{tm}.iset"] = [
            {"pin": s.get("pin"), "value": s.get("value"), "unit": s.get("unit")}
            for s in items.get(tm, {}).get("stimuli", []) if s.get("kind") == "iset"
        ]
    live["conflictIds"] = sorted(c.get("id") for c in d.get("conflicts", []) if c.get("id"))
    live["ruledPairMarker"] = "sw2pgnd" in json.dumps(d, ensure_ascii=False)
    return live


def digest_of(live: dict) -> str:
    return hashlib.sha256(json.dumps(live, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()


def expectation_failures(live: dict) -> list:
    fails = []
    for key, expected in (anchor.get("expectations") or {}).items():
        if live.get(key) != expected:
            fails.append(("expectation-violated", key, expected, live.get(key)))
    for cid in anchor.get("expectationConflicts") or []:
        if cid not in live.get("conflictIds", []):
            fails.append(("expectation-violated", f"conflict {cid}", "present", "absent"))
    for tm, pin, value, unit in anchor.get("expectationIset") or []:
        found = [s for s in live.get(f"{tm}.iset", []) if s.get("pin") == pin]
        if not found or found[0].get("value") != value or found[0].get("unit") != unit:
            fails.append(("expectation-violated", f"{tm}.iset[{pin}]", f"{value}{unit}", found))
    return fails


live = derive(doc)
base_digest = digest_of(live)
print("A) live satisfies this IR's expectations  :", not expectation_failures(live))
print("   claim digest matches the pinned value   :", base_digest == anchor["claimDigest"])

mut = json.loads(json.dumps(doc))
mut["generatedAt"] = "1999-01-01T00:00:00+08:00"
mut["notices"] = ["unrelated churn"]
b_live = derive(mut)
print("B) unrelated churn keeps digest+expects   :", digest_of(b_live) == base_digest and not expectation_failures(b_live))

mut2 = json.loads(json.dumps(doc))
for it in mut2["items"]:
    if it.get("tm") == "TM601":
        it["channels"][0]["pins"] = ["PMID (High)", "SW (Low)"]
c_live = derive(mut2)
c_fails = expectation_failures(c_live)
print("C) reverting TM601 polarity moves digest  :", digest_of(c_live) != base_digest)
print("   ...and trips an expectation             :", bool(c_fails), c_fails[:1])

mut3 = json.loads(json.dumps(doc))
for it in mut3["items"]:
    if it.get("tm") == "TM600":
        for s in it.get("stimuli", []):
            if s.get("kind") == "iset":
                s["value"] = 0.5
d_live = derive(mut3)
d_fails = expectation_failures(d_live)
print("D) changing the 1 A iset trips expectation:", bool(d_fails), d_fails[:1])

# persist the tampered variant as a scratch artefact so the discrimination is auditable
SCRATCH.write_text(json.dumps({"note": "in-memory tampered copy for the anchor negative test; "
                                        "NOT the real dft-ir.json",
                               "tamperedLiveClaims": c_live,
                               "tamperedDigest": digest_of(c_live),
                               "expectationFailures": [list(map(str, f)) for f in c_fails]},
                              ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

ok = (not expectation_failures(live)) and base_digest == anchor["claimDigest"] \
     and digest_of(b_live) == base_digest and not expectation_failures(b_live) \
     and digest_of(c_live) != base_digest and bool(c_fails) and bool(d_fails)
print()
print("NEGATIVE TEST:", "PASS (anchor and expectations are discriminating)" if ok else "FAIL")
assert hashlib.sha256(DFT.read_bytes()).hexdigest() == dft_bytes_before, "dft-ir.json was modified!"
print("dft-ir.json untouched:", dft_bytes_before[:16], "| scratch:", SCRATCH.name)
raise SystemExit(0 if ok else 1)
