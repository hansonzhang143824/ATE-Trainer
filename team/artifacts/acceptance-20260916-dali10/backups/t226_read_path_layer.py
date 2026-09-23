# -*- coding: utf-8 -*-
"""Adopt the read-path layer: a wrong key returns a credible value instead of erroring. Also correct my earlier 'history -> 0' record."""
import json, hashlib, os, datetime

A = r"team/artifacts/acceptance-20260916-dali10"
ap = os.path.join(A, "gate-logs-t28", "setupArchitect-anchors.json")
doc = json.load(open(ap, encoding="utf-8"))

sr = doc.get("scopeRule")
if isinstance(sr, str):
    sr = {"statement": sr}
sr["readPathClause"] = ("A query must declare the PATH/SCOPE/VOCABULARY it used, not just its result. A wrong key does not raise: it returns a CREDIBLE VALUE - reading a non-existent key for the plan's history yielded 0 entries, which looks exactly like an ordinary count, while the correct key `revisionHistory` yields 25. "
                        "The same silent-plausible-failure shape covers a wrong scope (an out-of-domain zero) and a wrong vocabulary (a hit count that is not an assertion audit).")
sr["family"] = ("together with the requirement that a checker carries its own projectionSpec, and that an out-of-domain zero declares its domain: THE QUERY MUST CARRY ITS FRAME.")
sr["practice"] = "in my messages and records, report counts as 'path/key -> value' (e.g. 'revisionHistory -> 25'), never as a bare number"
sr["instances"] = {"mine": "I read `history` on the plan and reported 0; the real key is `revisionHistory` with 25 entries - a path error, not a content difference",
                   "consequence": "my ledger already carried that 0; this write appends a correction rather than rewriting history"}
doc["scopeRule"] = sr
doc["generatedAt"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
json.dump(doc, open(ap, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
ab = open(ap, "rb").read()
print("anchors:", len(ab), "B /", hashlib.sha256(ab).hexdigest())

LOG = os.path.join(A, "gate-logs-t28", "setupArchitect-freeze-snapshots.json")
pre = open(LOG, "rb").read(); lg = json.loads(pre.decode("utf-8"))
def canon(e):
    return hashlib.sha256(json.dumps(e, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()

# verify the correct key in the plan before recording it
plan = json.load(open(os.path.join(A, "test-plan.json"), encoding="utf-8"))
rev_hist = plan.get("revisionHistory")
print("plan keys containing 'history':", [k for k in plan if "history" in k.lower()])
print("revisionHistory length:", len(rev_hist) if isinstance(rev_hist, list) else rev_hist)

entry = {"snapshotIndex": len(lg["entries"]) + 1, "takenAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "kind": "full",
         "reason": "adopted the read-path layer of the query-frame rule; corrected my earlier 'history -> 0' record (wrong key, credible value)",
         "contractRevision": 39,
         "gateReadField": {"where": "aliasResolution[alias=='bst2sw'].resolution.closedRelayNumbers", "value": [48, 60, 61, 76], "expectedForTM600": [48, 60, 61, 76, 83]},
         "selfAnchor": {"ledgerSizeBytesBeforeThisWrite": len(pre), "ledgerSha256BeforeThisWrite": hashlib.sha256(pre).hexdigest(), "entriesBeforeThisWrite": len(lg["entries"])},
         "prevEntryCanonicalSha256": canon(lg["entries"][-1]),
         "correctionOfMyOwnRead": {
             "whatIWrote": "I checked the plan's history and reported len(plan['history']) = 0",
             "whatIsTrue": "the plan carries `revisionHistory` (a list); the key `history` does not exist, and reading a missing key silently yielded 0, which looks like an ordinary count.",
             "verifiedNow": "revisionHistory -> %s" % (len(rev_hist) if isinstance(rev_hist, list) else rev_hist),
             "rootCause": "wrong read path (key name), not a content difference - the failure is silent and returns a credible value",
             "ruleAdopted": "report counts as 'path/key -> value'; never as a bare number",
             "peerNote": "test-strategy-architect supplied the correct key and turned the episode into the rule above; my name-precision reminder to them (b82 vs t82) is the symmetric instance at the name layer",
         },
         "artifacts": {"gate-logs-t28/setupArchitect-anchors.json": {"path": ap.replace("\\", "/"), "sizeBytes": len(ab), "sha256": hashlib.sha256(ab).hexdigest()},
                       "test-plan.json": {"path": os.path.join(A, "test-plan.json").replace("\\", "/"),
                                          "sizeBytes": os.path.getsize(os.path.join(A, "test-plan.json")),
                                          "sha256": hashlib.sha256(open(os.path.join(A, "test-plan.json"), "rb").read()).hexdigest()}}}
entry["ledgerSelfProof"] = {"rule": "chain + self anchors", "entryCanonicalSha256": canon(entry)}
lg["entries"].append(entry)
json.dump(lg, open(LOG, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
nb = open(LOG, "rb").read()
print("ledger:", len(lg["entries"]), "entries |", len(nb), "B /", hashlib.sha256(nb).hexdigest())
