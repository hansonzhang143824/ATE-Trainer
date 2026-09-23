# -*- coding: utf-8 -*-
"""Adopt schematic-expert's two-root split for the defect family (relocating example (1) to 'label != liveness', danger object = reader) and record their explicit ruling on the draft script."""
import json, hashlib, os, datetime

A = r"team/artifacts/acceptance-20260916-dali10"
ROOTS = {
    "rootA_mechanismCannotSee": {
        "name": "mechanism cannot see it",
        "examples": [
            "(2) the closure written as [48,61,76], omitting SW-side K60 - a subset-checking gate cannot see an expectation set that is missing a member (t34 L32/L32b)",
            "(3) parse_defines silently truncating multi-value macros (t34 L37)",
            "(4) a misspelled function name breaking search and cross-reference (fixed in the carrier at 23:09:01)",
        ],
        "remedy": "writing/review layer: enumerate every form of a claim, smoke-test expanders before trusting them, locators must carry owner and scope",
        "dangerObject": "the mechanism (it reports PASS while the artefact is wrong)",
    },
    "rootB_labelVsLiveness": {
        "name": "label is inconsistent with structural liveness",
        "examples": [
            "(1) the union disposition surviving as child keys inside a parent already marked SUPERSEDED (t34 L47): three children - ruling, disposition, union_form",
            "(1b) _t30ExpectationNote states things in an adjudicative tone while no script reads it",
        ],
        "remedy": "label discipline: the authority of a field is set by its consumers, not by its wording",
        "dangerObject": "the READER - and for (1) the gate does read closedRelayNumbers, so the hazard is not invisibility to the mechanism but misinterpretation by a human",
        "note": "raised by schematic-expert: grouping (1) under 'mechanism invisible' would merge two families whose remedies differ",
    },
}

LOG = os.path.join(A, "gate-logs-t28", "setupArchitect-freeze-snapshots.json")
pre = open(LOG, "rb").read(); lg = json.loads(pre.decode("utf-8"))
def canon(e):
    return hashlib.sha256(json.dumps(e, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()

entry = {
    "snapshotIndex": len(lg["entries"]) + 1, "takenAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "kind": "full",
    "reason": "adopted schematic-expert's two-root split of the defect family (example 1 relocated to 'label != liveness', danger object = reader) and recorded their explicit ruling that the draft script stays as written",
    "contractRevision": 39,
    "gateReadField": {"where": "aliasResolution[bst2sw].resolution.closedRelayNumbers", "value": [48, 60, 61, 76], "expectedForTM600": [48, 60, 61, 76, 83]},
    "selfAnchor": {"ledgerSizeBytesBeforeThisWrite": len(pre), "ledgerSha256BeforeThisWrite": hashlib.sha256(pre).hexdigest(), "entriesBeforeThisWrite": len(lg["entries"])},
    "prevEntryCanonicalSha256": canon(lg["entries"][-1]),
    "defectFamilyRoots": ROOTS,
    "draftScriptRuling": {
        "question": "should backups/t86_attribution_and_path.py be corrected to the right spelling?",
        "answer": "NO - keep it as written (schematic-expert's explicit answer). The occurrence there is a narrative reference, not an executable lookup, and rewriting it would erase the trace that the mistake was made and flagged.",
        "conditionThatWouldFlipIt": "if that script became a live tool in which the string is the OPERAND (like the BAD constant in backups/t102_fix_typo.py), then keeping the wrong spelling would be a latent bug and it must be corrected",
        "currentClassification": "the remaining occurrences of the wrong spelling are: an anchor-file note recording the correction, two ledger blocks recording it, the fix script's BAD/GOOD constants (by design), and the draft script's narrative reference",
    },
    "artifacts": {"acceptance-report.json": {"path": os.path.join(A, "acceptance-report.json").replace("\\", "/"),
                                             "sizeBytes": os.path.getsize(os.path.join(A, "acceptance-report.json")),
                                             "sha256": hashlib.sha256(open(os.path.join(A, "acceptance-report.json"), "rb").read()).hexdigest()},
                  "scripts/gate_baseline.json": {"path": "scripts/gate_baseline.json", "sizeBytes": os.path.getsize("scripts/gate_baseline.json"),
                                                  "sha256": hashlib.sha256(open("scripts/gate_baseline.json", "rb").read()).hexdigest()}},
}
entry["ledgerSelfProof"] = {"rule": "chain + self anchors", "entryCanonicalSha256": canon(entry)}
lg["entries"].append(entry)
json.dump(lg, open(LOG, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
nb = open(LOG, "rb").read()
print("ledger:", len(lg["entries"]), "entries |", len(nb), "B /", hashlib.sha256(nb).hexdigest())

ap = os.path.join(A, "gate-logs-t28", "setupArchitect-anchors.json")
doc = json.load(open(ap, encoding="utf-8"))
doc["defectFamilyRoots"] = {"rootA": ROOTS["rootA_mechanismCannotSee"]["name"] + " -> remedy: writing/review layer; danger object: the mechanism",
                            "rootB": ROOTS["rootB_labelVsLiveness"]["name"] + " -> remedy: label discipline (a field's authority is set by its consumers, not its wording); danger object: the reader",
                            "attribution": "the two-root split was proposed by schematic-expert; example (1) moved from root A to root B accordingly"}
doc["draftScriptRuling"] = "backups/t86_attribution_and_path.py stays as written (narrative reference); it would only need correcting if the string became an operand of a live tool"
doc["generatedAt"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
json.dump(doc, open(ap, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
ab = open(ap, "rb").read()
print("anchors:", len(ab), "B /", hashlib.sha256(ab).hexdigest())
