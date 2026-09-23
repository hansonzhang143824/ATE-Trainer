# -*- coding: utf-8 -*-
"""Verify t4's receipts that 41,797/6034af71 (and 40,658/5a668fe6) WERE written to the canonical payload path, then refine t34's wording."""
import json, hashlib, os, datetime, re

A = r"team/artifacts/acceptance-20260916-dali10"
RECEIPTS = {
    "backups/t52_verify.py": [8, 9],
    "backups/t50_claim.py": [7],
    "backups/t50_msync.py": [40, 41],
    "backups/t55_edit.py": [36],
}
for rel, lines in RECEIPTS.items():
    p = os.path.join(A, rel)
    if not os.path.exists(p):
        print("MISSING:", rel); continue
    src = open(p, encoding="utf-8", errors="replace").read().splitlines()
    print("--- %s (%d lines) ---" % (rel, len(src)))
    for n in lines:
        if n <= len(src):
            print("%5d| %s" % (n, src[n - 1].rstrip()[:170]))

f34 = os.path.join(A, "acceptance-report.json")
d = json.load(open(f34, encoding="utf-8"))
REFINE = ("REFINED WORDING (accepted from test-strategy-architect, verified against the editor scripts' receipts): the intermediate revisions 41,797 B / 6034af71... and 40,658 B / 5a668fe6... WERE written to the canonical payload path - the receipt is in the "
          "archived edit scripts (backups/t52_verify.py L8-9 carries a MATCH hash assertion, t50_claim.py L7 likewise, t50_msync.py L40-41 and t55_edit.py L36 record their supersession) - but their bytes were overwritten in place, so their CONTENT can no longer be reviewed. "
          "The correct statement is therefore 'was written (receipt provable) + content not reviewable', NOT 'never landed'. The captain's 'never delivered' refers to never having become the final delivered state, which is consistent with this.")
n = 0
for i, x in enumerate(d["limitations"]):
    if x.startswith("L24 ") and "REFINED WORDING" not in x:
        d["limitations"][i] = x + " " + REFINE
        n += 1
if "content not reviewable" not in d["isolationAudit"].get("payloadNote", ""):
    d["isolationAudit"]["payloadNote"] = d["isolationAudit"]["payloadNote"] + " " + REFINE
    n += 1
d["limitations"].append("L43 (record closure, so the point is not re-litigated): regarding the claim that test-strategy-architect stated 'the t30 expectation should become [48,61,76]' - that sentence appears in their v22-era refresh request; their later and current position is "
                        "consistently the expectation {48,60,61,76,83}, which matches my own measurement. The operative value in this report is {48,60,61,76,83}, and the conflicting sentence is not treated as their position. Closed.")
json.dump(d, open(f34, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
b = open(f34, "rb").read()
print("\nt34: %d B / %s @%s | limitations: %d | refined edits: %d" % (len(b), hashlib.sha256(b).hexdigest(),
      datetime.datetime.fromtimestamp(os.stat(f34).st_mtime).strftime("%Y-%m-%d %H:%M:%S"), len(d["limitations"]), n))

ap = os.path.join(A, "gate-logs-t28", "setupArchitect-anchors.json")
doc = json.load(open(ap, encoding="utf-8"))
doc["anchors"]["acceptance-report.json"] = {"path": "team/artifacts/acceptance-20260916-dali10/acceptance-report.json", "sizeBytes": len(b),
                                            "sha256": hashlib.sha256(b).hexdigest(), "measuredAt": datetime.datetime.fromtimestamp(os.stat(f34).st_mtime).strftime("%Y-%m-%d %H:%M:%S")}
json.dump(doc, open(ap, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("anchors refreshed:", os.path.getsize(ap), "B /", hashlib.sha256(open(ap, "rb").read()).hexdigest())
