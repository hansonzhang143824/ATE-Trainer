# -*- coding: utf-8 -*-
"""Clarification (tick): the occurrences of the sibling alias's value in my carrier are correct usages, not errors."""
import json, hashlib, os, datetime, re

A = r"team/artifacts/acceptance-20260916-dali10"
LOG = os.path.join(A, "gate-logs-t28", "setupArchitect-freeze-snapshots.json")
pre = open(LOG, "rb").read(); lg = json.loads(pre.decode("utf-8"))
def canon(e):
    return hashlib.sha256(json.dumps(e, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()

carrier = os.path.join(A, "acceptance-report.json")
t = open(carrier, encoding="utf-8").read()
ctx = []
for m in re.finditer(r"154,\s*155", t):
    ctx.append(t[max(0, m.start() - 90):m.end() + 60].replace("\n", " "))

entry = {"snapshotIndex": len(lg["entries"]) + 1, "takenAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "kind": "tick",
         "reason": "clarification of my own sweep: the sibling alias's closure value appears in the carrier as CORRECT usage, so a raw token count would have misread it as an error",
         "artifactsAbsent": True,
         "artifactsAbsentReason": "this entry carries no artefact value set; it corrects the interpretation of a count reported in the previous entry",
         "selfAnchor": {"ledgerSizeBytesBeforeThisWrite": len(pre), "ledgerSha256BeforeThisWrite": hashlib.sha256(pre).hexdigest(), "entriesBeforeThisWrite": len(lg["entries"])},
         "prevEntryCanonicalSha256": canon(lg["entries"][-1]),
         "sweepClarification": {
             "countReported": "previous entry said my carrier contains the value [154,155,60,61]",
             "whatItActuallyIs": "every occurrence in the carrier is a CORRECT usage: the value is the closed set of the sibling aliases sw2pgnd and pgnd2sw, cited when explaining that the SW end must be written as {60,61}, and as TM601_LS_RDSON's expectation [60,61,154,155]",
             "contexts": ctx,
             "theOnlyWrongAttribution": "my previous entry's own gateReadField, which attributed that value to the gate-read alias - corrected in the same entry and here",
             "lesson": "a raw token count is not an assertion audit - the same rule I applied to others' stale tokens applies to my own sweep; the count needed per-occurrence classification",
         }}
entry["ledgerSelfProof"] = {"rule": "chain + self anchors", "entryCanonicalSha256": canon(entry)}
lg["entries"].append(entry)
json.dump(lg, open(LOG, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
nb = open(LOG, "rb").read()
print("contexts found:", len(ctx))
for c in ctx:
    print("   ...", c[:150])
print("\nledger:", len(lg["entries"]), "entries |", len(nb), "B /", hashlib.sha256(nb).hexdigest())
