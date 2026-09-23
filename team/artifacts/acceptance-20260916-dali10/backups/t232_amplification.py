# -*- coding: utf-8 -*-
"""One write closing two pending items: correction entries are ticks (reviewer), and the self-amplification of counts (plan side) - both recorded in the ledger's own schema block."""
import json, hashlib, os, datetime
from collections import Counter

A = r"team/artifacts/acceptance-20260916-dali10"
LOG = os.path.join(A, "gate-logs-t28", "setupArchitect-freeze-snapshots.json")
pre = open(LOG, "rb").read()
lg = json.loads(pre.decode("utf-8"))

def dist(entries):
    c = Counter(e.get("kind") if isinstance(e, dict) else None for e in entries)
    return {"full": c.get("full"), "tick": c.get("tick"), "missingKind": c.get(None), "other": {k: v for k, v in c.items() if k not in ("full", "tick", None)}}

before = dist(lg["entries"])
print("distribution before this write:", before)

s = lg.setdefault("schema", {})
s["rule"] = (str(s.get("rule", "")) + " TWO CLARIFICATIONS (folded in together): "
             "(1) a CORRECTION-type entry - one that carries no artefact value set, only corrects a statistic - is also a tick; the tick count therefore grows with the number of corrections, and a reader who sees it rise must not infer that artefact writes occurred. "
             "(2) SELF-AMPLIFICATION: any count of a class that the recording process itself adds to must grow. This was already visible in prose counts during this run (an intersection count 0->1->3; a phrase count 1->2; a value count 12->13->15) and it now appears in STRUCTURED data: my own correction entry is itself a tick, so recording a correction increments the statistic the correction is about. "
             "Only a DECLARED decision rule together with a DECLARED moment makes such growth explainable instead of mysterious - which is why the rule is stated here rather than left implicit.")
s["countAmplificationNote"] = {
    "statement": "A count of a class that the recording process itself adds to necessarily grows; state the decision rule and the moment so that differences across observers and runs read as explainable growth rather than as disagreement.",
    "structuredInstance": "this ledger: entry[59] and entry[64] are ticks that correct statistics; each correction increments the tick count",
    "proseInstances": ["an intersection count 0 -> 1 -> 3", "a phrase count 1 -> 2", "a value count 12 -> 13 -> 15"],
    "raisedBy": "test-strategy-architect observed the structured-data instance; rule-reviewer requested the correction-entry clarification",
}
lg["schema"] = s

def canon(e):
    return hashlib.sha256(json.dumps(e, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()

entry = {"snapshotIndex": len(lg["entries"]) + 1, "takenAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "kind": "tick",
         "reason": "one write closing two pending clarifications: correction entries are ticks, and count self-amplification (with its structured-data instance)",
         "artifactsAbsent": True,
         "artifactsAbsentReason": "no artefact value set is recorded here; this entry corrects the semantics of this ledger's own schema block",
         "selfAnchor": {"ledgerSizeBytesBeforeThisWrite": len(pre), "ledgerSha256BeforeThisWrite": hashlib.sha256(pre).hexdigest(), "entriesBeforeThisWrite": len(lg["entries"])},
         "prevEntryCanonicalSha256": canon(lg["entries"][-1]),
         "pendingItemsClosed": ["rule-reviewer: correction-type entries are ticks, so the tick count grows with corrections",
                                "test-strategy-architect: the first STRUCTURED-DATA instance of count self-amplification, and why a declared rule plus a declared moment is what makes such growth explainable"],
         "distributionBeforeThisWrite": before,
         "note": "this entry is itself a tick (no value set), so it too increments the tick count - the effect it documents",
         }
entry["ledgerSelfProof"] = {"rule": "chain + self anchors", "entryCanonicalSha256": canon(entry)}
lg["entries"].append(entry)
json.dump(lg, open(LOG, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
post = open(LOG, "rb").read()
after = dist(json.loads(post.decode("utf-8"))["entries"])
print("distribution after this write:", after)
print("ledger:", len(json.loads(post.decode('utf-8'))["entries"]), "entries |", len(post), "B /", hashlib.sha256(post).hexdigest())
