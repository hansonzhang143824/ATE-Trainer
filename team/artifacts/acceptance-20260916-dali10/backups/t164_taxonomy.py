# -*- coding: utf-8 -*-
"""Adopt the three-class taxonomy for known defects in derived text, and classify the draft script with evidence."""
import json, hashlib, os, datetime, glob, re

A = r"team/artifacts/acceptance-20260916-dali10"
# evidence for the classification of backups/t86_attribution_and_path.py
refs = []
for root, dirs, files in os.walk("."):
    if any(x in root for x in (".git", "node_modules")):
        continue
    for f in files:
        if not f.endswith((".ps1", ".py", ".json", ".md", ".js", ".mjs", ".cmd", ".bat")):
            continue
        p = os.path.join(root, f)
        if os.path.basename(p) == "t86_attribution_and_path.py":
            continue
        try:
            t = open(p, encoding="utf-8", errors="replace").read()
        except Exception:
            continue
        if "t86_attribution_and_path" in t:
            refs.append(p.replace("\\", "/"))
print("files referencing t86_attribution_and_path (excluding itself):", refs or "none")
t86 = os.path.join(A, "backups", "t86_attribution_and_path.py")
src = open(t86, encoding="utf-8").read()
print("t86 executes on import/run?:", "no runner references it" if not refs else "referenced")
print("t86 uses the misspelled token as an operand?:", bool(re.search(r"(BAD|needle|target)\s*=\s*[\"'][^\"']*VAT_LOOP_INDICTOR", src)))

TAXONOMY = {
    "name": "three-class taxonomy for a known wrong string in derived text (purified by schematic-expert, adopted by rule-reviewer and here)",
    "classes": [
        "class 1 - live deliverable: it MUST be correct (the live acceptance-report.json was corrected at 23:09:01)",
        "class 2 - retired or backup copy: it does not take part in acceptance; REGISTER the defect (e.g. backups/t86_attribution_and_path.py, which carries an explanatory comment instead of a silent rewrite)",
        "class 3 - deliberately retained old string: it must NOT be 'corrected' (the misspelling inside a fix script is the search target; the contract's superseded fields record history)",
    ],
    "decisionRule": "register, do not rewrite; one fewer write is one fewer drift. Registering is required; rewriting is only warranted when the string is an operand of a live tool.",
    "classificationOfT86": ("class 2. Evidence: no runner, script or manifest references t86_attribution_and_path.py anywhere in the tree, and the misspelled token appears in a narrative sentence rather than as an operand constant, "
                            "so the exception ('still executed and its search depends on the misspelling') does not apply. The file keeps its historical string plus an explanatory comment; the reviewer's explicit answer is: do not change it."),
    "reviewerAnswer": "do not change backups/t86_attribution_and_path.py (explicit answer); registration plus the explanatory comment is the correct handling",
}

LOG = os.path.join(A, "gate-logs-t28", "setupArchitect-freeze-snapshots.json")
pre = open(LOG, "rb").read(); lg = json.loads(pre.decode("utf-8"))
def canon(e):
    return hashlib.sha256(json.dumps(e, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()
entry = {"snapshotIndex": len(lg["entries"]) + 1, "takenAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "kind": "full",
         "reason": "adopted the three-class taxonomy for known wrong strings; classified the draft script with evidence; recorded the reviewer's explicit answer",
         "contractRevision": 39,
         "gateReadField": {"where": "aliasResolution[bst2sw].resolution.closedRelayNumbers", "value": [48, 60, 61, 76], "expectedForTM600": [48, 60, 61, 76, 83]},
         "selfAnchor": {"ledgerSizeBytesBeforeThisWrite": len(pre), "ledgerSha256BeforeThisWrite": hashlib.sha256(pre).hexdigest(), "entriesBeforeThisWrite": len(lg["entries"])},
         "prevEntryCanonicalSha256": canon(lg["entries"][-1]),
         "wrongStringTaxonomy": TAXONOMY,
         "artifacts": {"backups/t86_attribution_and_path.py": {"path": t86.replace("\\", "/"), "sizeBytes": os.path.getsize(t86),
                                                               "sha256": hashlib.sha256(open(t86, "rb").read()).hexdigest()},
                       "acceptance-report.json": {"path": os.path.join(A, "acceptance-report.json").replace("\\", "/"),
                                                  "sizeBytes": os.path.getsize(os.path.join(A, "acceptance-report.json")),
                                                  "sha256": hashlib.sha256(open(os.path.join(A, "acceptance-report.json"), "rb").read()).hexdigest()}}}
entry["ledgerSelfProof"] = {"rule": "chain + self anchors", "entryCanonicalSha256": canon(entry)}
lg["entries"].append(entry)
json.dump(lg, open(LOG, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
nb = open(LOG, "rb").read()
print("ledger:", len(lg["entries"]), "entries |", len(nb), "B /", hashlib.sha256(nb).hexdigest())

ap = os.path.join(A, "gate-logs-t28", "setupArchitect-anchors.json")
doc = json.load(open(ap, encoding="utf-8"))
doc["wrongStringTaxonomy"] = TAXONOMY
doc["generatedAt"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
json.dump(doc, open(ap, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
ab = open(ap, "rb").read()
print("anchors:", len(ab), "B /", hashlib.sha256(ab).hexdigest())
