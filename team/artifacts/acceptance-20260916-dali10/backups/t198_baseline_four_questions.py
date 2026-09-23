# -*- coding: utf-8 -*-
"""Verify the diagnostician's four-question refinement and correct my own baselineTriad wording."""
import json, hashlib, os, datetime, re

A = r"team/artifacts/acceptance-20260916-dali10"
C = os.path.join(A, "setup-contract.json")
raw = open(C, "rb").read()
d = json.loads(raw.decode("utf-8"))

# 1) is the contract's gate-read field neutral today, and was it wrong historically?
closed = d["aliasResolution"][1]["resolution"]["closedRelayNumbers"]
print("gate-read field now:", closed)
hist = []
def walk(node, path):
    if isinstance(node, dict):
        for k, v in node.items():
            walk(v, path + [str(k)])
    elif isinstance(node, list):
        for i, v in enumerate(node):
            walk(v, path + ["[%d]" % i])
    elif isinstance(node, str):
        if re.search(r"\b110\b", node) and re.search(r"superseded|withdrawn|contested|old|previous|prefer", node, re.I):
            hist.append((".".join(path), node[:190]))
walk(d, [])
print("\nplaces inside the contract that record 110 as contested/superseded:")
for p, s in hist[:6]:
    print("  -", p, "=>", s)

# 2) the four questions, evaluated on the three artifacts
MATRIX = {
    "questions": [
        "1 authoritative - is it consumed by the gate by construction?",
        "2 ownership-neutral - does it belong to no single party?",
        "3 independent of me - is it produced by a different member?",
        "4 content independently recomputed - has a third party verified its content?",
    ],
    "contract": {"1": True, "2": True, "3": True, "4": False,
                 "note": "the contract is an AUTHORED artifact: it is authoritative and ownership-neutral, but its gate-read field was wrong during rev 24-28 ([110,61]) before being narrowed to [48,60,61,76]. Ownership-neutral is therefore NOT a synonym for content-verified."},
    "peerReport": {"1": False, "2": False, "3": True, "4": False, "note": "produced by the owning member; independent of me, not of its author"},
    "myAnchors": {"1": False, "2": False, "3": True, "4": False, "note": "my own ledger; for a reviewer it is neither independent nor neutral - which is why rule-reviewer refused it as a baseline"},
    "conclusion": ("baseline = the contract as an AUTHORITATIVE, OWNERSHIP-NEUTRAL INPUT, cited by revision (recomputed sha256) with key fields cross-checked at the same evidence level. It is not an independent baseline."),
    "raisedBy": "compile-diagnostician (refining my earlier three-property summary)",
    "whyItMatters": "conflating 'ownership-neutral' with 'content-verified' would turn 'a value someone wrote' into 'an independent fact' - the same failure family as size/identity, revision/content and preservedPeerKeys/entries",
}

LOG = os.path.join(A, "gate-logs-t28", "setupArchitect-freeze-snapshots.json")
pre = open(LOG, "rb").read(); lg = json.loads(pre.decode("utf-8"))
def canon(e):
    return hashlib.sha256(json.dumps(e, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()
entry = {"snapshotIndex": len(lg["entries"]) + 1, "takenAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "kind": "full",
         "reason": "adopted the peer's four-question refinement of the baseline triad and corrected my own 'authoritative and neutral' summary",
         "contractRevision": d.get("revision"),
         "gateReadField": {"where": "aliasResolution[bst2sw].resolution.closedRelayNumbers", "value": closed, "expectedForTM600": [48, 60, 61, 76, 83]},
         "selfAnchor": {"ledgerSizeBytesBeforeThisWrite": len(pre), "ledgerSha256BeforeThisWrite": hashlib.sha256(pre).hexdigest(), "entriesBeforeThisWrite": len(lg["entries"])},
         "prevEntryCanonicalSha256": canon(lg["entries"][-1]),
         "baselineFourQuestions": MATRIX,
         "correctionOfMyOwnWording": ("I summarised the triad as 'the contract is authoritative and neutral'. The peer's refinement shows this collapses two questions and omits two more: the contract satisfies authority (1) and ownership-neutrality (2), but not independent recomputation (4) - it is an AUTHORED artifact whose gate-read field was "
                                      "wrong during rev 24-28. My summary is therefore superseded by the four-question form."),
         "artifacts": {"setup-contract.json": {"path": C.replace("\\", "/"), "sizeBytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}}}
entry["ledgerSelfProof"] = {"rule": "chain + self anchors", "entryCanonicalSha256": canon(entry)}
lg["entries"].append(entry)
json.dump(lg, open(LOG, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
nb = open(LOG, "rb").read()
print("\nledger:", len(lg["entries"]), "entries |", len(nb), "B /", hashlib.sha256(nb).hexdigest())

ap = os.path.join(A, "gate-logs-t28", "setupArchitect-anchors.json")
doc = json.load(open(ap, encoding="utf-8"))
doc["baselineFourQuestions"] = MATRIX
doc["baselineTriadSuperseded"] = ("the earlier three-property summary ('authoritative / independent / neutral') is superseded by baselineFourQuestions: authority and ownership-neutrality are separate questions, and 'content independently recomputed' is a fourth that the contract does NOT satisfy")
doc["generatedAt"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
json.dump(doc, open(ap, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
ab = open(ap, "rb").read()
print("anchors:", len(ab), "B /", hashlib.sha256(ab).hexdigest())
