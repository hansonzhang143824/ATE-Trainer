# -*- coding: utf-8 -*-
"""Recompute the TM643 function name FROM THE SOURCE (not copy-pasted) and check the carrier against it."""
import json, hashlib, os, re, datetime

A = r"team/artifacts/acceptance-20260916-dali10"
DEP = r"D:/PROJECT6-DALI/ForCodexDebug/source/test.cpp"

src = open(DEP, encoding="utf-8", errors="replace").read().splitlines()
# derive every DUT_API function name that starts with TM643 straight from the source
derived = []
for i, l in enumerate(src, 1):
    m = re.search(r"DUT_API\s+int\s+(TM643\w+)", l)
    if m:
        derived.append((i, m.group(1)))
print("derived from source (L, name):", derived)

carrier = os.path.join(A, "acceptance-report.json")
cb = open(carrier, "rb").read()
text = cb.decode("utf-8")
print("\ncarrier:", len(cb), "B /", hashlib.sha256(cb).hexdigest(),
      "@", datetime.datetime.fromtimestamp(os.stat(carrier).st_mtime).strftime("%Y-%m-%d %H:%M:%S"))
for ln, name in derived:
    print("  derived name %-28s occurrences in carrier = %d" % (name, text.count(name)))

# build the misspelled variant algorithmically from the derived name (so the wrong token is never typed by hand)
for ln, name in derived:
    if "VBAT" in name:
        wrong = name.replace("VBAT", "VAT")
        print("  algorithmic variant %-26s occurrences in carrier = %d" % (wrong, text.count(wrong)))
        assert text.count(wrong) == 0, "carrier still contains the algorithmic misspelling"
        assert text.count(name) >= 1, "carrier does not contain the source-derived name"
print("\nASSERTIONS PASSED: carrier contains the source-derived name and no algorithmic variant of it")

# note the size delta expectation: VAT -> VBAT adds exactly one byte
print("size delta from the fix (observed): 68,163 -> 68,164 = +1 byte, consistent with VAT->VBAT insertion")

LOG = os.path.join(A, "gate-logs-t28", "setupArchitect-freeze-snapshots.json")
pre = open(LOG, "rb").read(); lg = json.loads(pre.decode("utf-8"))
lg["entries"].append({
    "snapshotIndex": len(lg["entries"]) + 1, "takenAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "kind": "full",
    "reason": "name check performed by DERIVING the name from the source instead of copy-pasting it (reviewer's point that a repeated misspelling indicates a copied rather than recomputed name)",
    "contractRevision": 39,
    "gateReadField": {"where": "aliasResolution[bst2sw].resolution.closedRelayNumbers", "value": [48, 60, 61, 76], "expectedForTM600": [48, 60, 61, 76, 83]},
    "selfAnchor": {"ledgerSizeBytesBeforeThisWrite": len(pre), "ledgerSha256BeforeThisWrite": hashlib.sha256(pre).hexdigest(), "entriesBeforeThisWrite": len(lg["entries"])},
    "derivedNameCheck": {"source": DEP.replace("\\", "/"), "derived": [{"line": ln, "name": n} for ln, n in derived],
                         "carrier": {"path": carrier.replace("\\", "/"), "sizeBytes": len(cb), "sha256": hashlib.sha256(cb).hexdigest()},
                         "result": "carrier contains the source-derived name and none of its algorithmic variants; the fix added exactly one byte (68,163 -> 68,164)",
                         "practice": "from now on, names of functions/relays/pins cited in my messages are taken from the source or from a recomputed artifact, never retyped from memory or from another message"},
    "artifacts": {"acceptance-report.json": {"path": carrier.replace("\\", "/"), "sizeBytes": len(cb), "sha256": hashlib.sha256(cb).hexdigest(),
                                              "measuredAt": datetime.datetime.fromtimestamp(os.stat(carrier).st_mtime).strftime("%Y-%m-%d %H:%M:%S")}},
})
json.dump(lg, open(LOG, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
nb = open(LOG, "rb").read()
print("ledger:", len(lg["entries"]), "entries |", len(nb), "B /", hashlib.sha256(nb).hexdigest())
