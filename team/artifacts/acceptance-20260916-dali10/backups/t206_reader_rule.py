# -*- coding: utf-8 -*-
"""Add a reader-facing one-liner for t42/t44 readers (append-only), attributed to shared practice, with an external anchor and no authority claim."""
import json, hashlib, os, datetime

A = r"team/artifacts/acceptance-20260916-dali10"
C = os.path.join(A, "setup-contract.json")
raw = open(C, "rb").read()
d = json.loads(raw.decode("utf-8"))
byname = {e.get("alias"): (e.get("resolution") or {}).get("closedRelayNumbers") for e in d["aliasResolution"]}
closed = byname.get("bst2sw")
print("bst2sw (by name):", closed, "| contract:", len(raw), "B /", hashlib.sha256(raw).hexdigest()[:24], "@", datetime.datetime.fromtimestamp(os.stat(C).st_mtime).strftime("%Y-%m-%d %H:%M:%S"))

f34 = os.path.join(A, "acceptance-report.json")
rep = json.load(open(f34, encoding="utf-8"))
before = len(rep["limitations"])

L55 = ("L55 (reader rule for the t42 / t44 family; added at test-strategy-architect's relay, which attributes it to BOTH sides' shared practice - the plan-side note's section 2.5 and the reviewer's t55 correction file - not to any single author): "
       "any [48,61,76] appearing in those artefacts is the OLD INCOMPLETE SHORTHAND (it omits the SW side's K60_BUSL0_VCP); the authoritative closed set is [48,60,61,76] (BST [48,76] in the ACM200 family, SW [60,61] in the FPVIe[L] family) and the TM600 gate expectation is {48,60,61,76,83}. "
       "Cite the artefacts, not the shorthand. HOW TO CITE THEM: by full path + owner + recompute at use time - no hash or size is hard-coded here, and this entry does NOT claim to be the determination of record (per the run rule that a record must not pose as a determination); the external anchors are the live contract field "
       "aliasResolution[alias=='bst2sw'].resolution.closedRelayNumbers (measured now: %s; contract %d B / %s) and the plan-side note held by test-strategy-architect." % (
           closed, len(raw), hashlib.sha256(raw).hexdigest()))
rep["limitations"].append(L55)
json.dump(rep, open(f34, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
b34 = open(f34, "rb").read()
print("\nt34 limitations:", before, "->", len(rep["limitations"]))
print("t34:", len(b34), "B /", hashlib.sha256(b34).hexdigest(), "@", datetime.datetime.fromtimestamp(os.stat(f34).st_mtime).strftime("%Y-%m-%d %H:%M:%S"))

ap = os.path.join(A, "gate-logs-t28", "setupArchitect-anchors.json")
doc = json.load(open(ap, encoding="utf-8"))
doc["readerRuleCheckCriterion"] = ("A detector for reader rules must detect an ASSERTION, not the co-occurrence of two strings: co-occurrence is not relationship. Qualified form - in the same sentence or clause: (1) the old value is NAMED and DEMOTED (superseded / old / omitted / previously written), "
                                   "(2) the new value is BOUND AS AUTHORITATIVE (authoritative / in force), (3) an external anchor sits in the same sentence or immediately adjacent, and (4) the text does NOT say 'this document is authoritative'. "
                                   "The earlier co-occurrence-style instrument (two value strings plus an anchor word in one paragraph) was falsified by schematic-expert's survey and is superseded by this relational form.")
doc["gateReadFieldByNam"] = closed
doc["generatedAt"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
json.dump(doc, open(ap, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
ab = open(ap, "rb").read()
print("anchors:", len(ab), "B /", hashlib.sha256(ab).hexdigest())

LOG = os.path.join(A, "gate-logs-t28", "setupArchitect-freeze-snapshots.json")
pre = open(LOG, "rb").read(); lg = json.loads(pre.decode("utf-8"))
def canon(e):
    return hashlib.sha256(json.dumps(e, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()
entry = {"snapshotIndex": len(lg["entries"]) + 1, "takenAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "kind": "full",
         "reason": "added the t42/t44 reader rule to the carrier (append-only L55) with an external anchor and no authority claim; recorded the relational detector criterion",
         "contractRevision": d.get("revision"),
         "gateReadField": {"where": "aliasResolution[alias=='bst2sw'].resolution.closedRelayNumbers", "value": closed, "expectedForTM600": [48, 60, 61, 76, 83]},
         "selfAnchor": {"ledgerSizeBytesBeforeThisWrite": len(pre), "ledgerSha256BeforeThisWrite": hashlib.sha256(pre).hexdigest(), "entriesBeforeThisWrite": len(lg["entries"])},
         "prevEntryCanonicalSha256": canon(lg["entries"][-1]),
         "readerRuleAdded": {"limitation": "L55", "attribution": "both sides' shared practice (plan-side note section 2.5 + reviewer's t55 correction file), relayed by test-strategy-architect",
                             "hardCodedIdentity": "none - cited by path + owner + recompute at use time; the entry states it is not the determination of record",
                             "externalAnchor": "live contract field aliasResolution[alias=='bst2sw'].resolution.closedRelayNumbers, measured this round"},
         "artifacts": {"acceptance-report.json": {"path": f34.replace("\\", "/"), "sizeBytes": len(b34), "sha256": hashlib.sha256(b34).hexdigest()},
                       "gate-logs-t28/setupArchitect-anchors.json": {"path": ap.replace("\\", "/"), "sizeBytes": len(ab), "sha256": hashlib.sha256(ab).hexdigest()}}}
entry["ledgerSelfProof"] = {"rule": "chain + self anchors", "entryCanonicalSha256": canon(entry)}
lg["entries"].append(entry)
json.dump(lg, open(LOG, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
nb = open(LOG, "rb").read()
print("ledger:", len(lg["entries"]), "entries |", len(nb), "B /", hashlib.sha256(nb).hexdigest())
