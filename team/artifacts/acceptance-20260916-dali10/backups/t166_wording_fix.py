# -*- coding: utf-8 -*-
"""Correction: my own scan paragraph overstated the evidence; state it precisely."""
import json, hashlib, os, datetime

A = r"team/artifacts/acceptance-20260916-dali10"
ACCURATE = ("class 2. Evidence, stated precisely: no runner references it - a search of every .ps1 in the tree returns nothing, and no manifest or runner lists the script. The four files that DO contain its name are my own documentation artefacts "
            "(two of my rule/registry scripts, my anchors file and my ledger), which cite it as a subject rather than execute it. The misspelled token appears in a narrative sentence, not as an operand constant, so the exception "
            "('still executed and its search depends on the misspelling') does not apply. Hence: keep the historical string plus the explanatory comment; the reviewer's explicit answer is do not change it.")

LOG = os.path.join(A, "gate-logs-t28", "setupArchitect-freeze-snapshots.json")
pre = open(LOG, "rb").read(); lg = json.loads(pre.decode("utf-8"))
def canon(e):
    return hashlib.sha256(json.dumps(e, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()

# fix the anchors copy of the taxonomy (my own file)
ap = os.path.join(A, "gate-logs-t28", "setupArchitect-anchors.json")
doc = json.load(open(ap, encoding="utf-8"))
doc["wrongStringTaxonomy"]["classificationOfT86"] = ACCURATE
doc["wrongStringTaxonomy"]["evidenceWordingCorrected"] = ("an earlier wording of this field said 'no runner, script or manifest references it'; that was too broad - my own documentation artefacts do contain the name as a citation. The classification (class 2) is unchanged.",
                                                          )
doc["generatedAt"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
json.dump(doc, open(ap, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
ab = open(ap, "rb").read()

entry = {"snapshotIndex": len(lg["entries"]) + 1, "takenAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "kind": "full",
         "reason": "corrected my own overstated evidence sentence about the draft script (my documentation cites its name; no runner executes it) - classification unchanged",
         "contractRevision": 39,
         "gateReadField": {"where": "aliasResolution[bst2sw].resolution.closedRelayNumbers", "value": [48, 60, 61, 76], "expectedForTM600": [48, 60, 61, 76, 83]},
         "selfAnchor": {"ledgerSizeBytesBeforeThisWrite": len(pre), "ledgerSha256BeforeThisWrite": hashlib.sha256(pre).hexdigest(), "entriesBeforeThisWrite": len(lg["entries"])},
         "prevEntryCanonicalSha256": canon(lg["entries"][-1]),
         "correctionOfMyOwnWording": {"whatISaid": "no runner, script or manifest references t86_attribution_and_path.py",
                                      "whyTooBroad": "my own anchors file, ledger and two rule scripts contain the name as a citation, so 'no script references it' was imprecise",
                                      "accurateNow": ACCURATE,
                                      "lesson": "same family as the scope rule: quantify the claim to the class being scanned (runners versus documentation), and re-measure before asserting absence"},
         "artifacts": {"gate-logs-t28/setupArchitect-anchors.json": {"path": ap.replace("\\", "/"), "sizeBytes": len(ab), "sha256": hashlib.sha256(ab).hexdigest()},
                       "acceptance-report.json": {"path": os.path.join(A, "acceptance-report.json").replace("\\", "/"),
                                                  "sizeBytes": os.path.getsize(os.path.join(A, "acceptance-report.json")),
                                                  "sha256": hashlib.sha256(open(os.path.join(A, "acceptance-report.json"), "rb").read()).hexdigest()}}}
entry["ledgerSelfProof"] = {"rule": "chain + self anchors", "entryCanonicalSha256": canon(entry)}
lg["entries"].append(entry)
json.dump(lg, open(LOG, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
nb = open(LOG, "rb").read()
print("ledger:", len(lg["entries"]), "entries |", len(nb), "B /", hashlib.sha256(nb).hexdigest())
print("anchors:", len(ab), "B /", hashlib.sha256(ab).hexdigest())
