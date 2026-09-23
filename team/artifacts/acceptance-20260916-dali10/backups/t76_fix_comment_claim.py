# -*- coding: utf-8 -*-
"""Verify the four comment lines in the deployed tree and correct the wording in t34 (t34 = acceptance-report.json)."""
import json, hashlib, os, datetime, re

DEP = r"D:/PROJECT6-DALI/ForCodexDebug/source/test.cpp"
A = r"team/artifacts/acceptance-20260916-dali10"
L = open(DEP, encoding="utf-8", errors="replace").read().splitlines()
for n in (6997, 6998, 7000, 7085, 7086, 7087, 7169, 7170, 7512, 7513):
    if n <= len(L):
        print("%5d| %s" % (n, L[n - 1].rstrip()[:170]))

# which of them contain the (FH5->BST) marker vs the alternative wording
mark_fh5 = [n for n in (6997, 7085, 7169, 7512) if n <= len(L) and "FH5" in L[n - 1] and "BST" in L[n - 1]]
mark_alt = [n for n in (6997, 7085, 7169, 7512) if n <= len(L) and "供电" in L[n - 1]]
print("\nlines containing an FH5->BST style marker:", mark_fh5)
print("lines using the 'BST 供电 ... (K48+K76)' wording:", mark_alt)

f = os.path.join(A, "acceptance-report.json")
d = json.load(open(f, encoding="utf-8"))
pat = re.compile(r"[^\n]*6997[^\n]*")
hits = 0
for i, x in enumerate(d["limitations"]):
    if "6997" in x and ("FH5" in x or "7169" in x):
        print("\n[%d] BEFORE: %s" % (i, x[:400]))
        new = x.replace(
            "comments :6997/:7085/:7169/:7512 name the pin and instrument in one sentence",
            "comments state the same fact in TWO forms: test.cpp:6997 and :7085 read \"BST <- SW12_U1REF_BST_ACM: K48_ACM5_AMP_REF + K76_ACM_BST (FH5->BST)\", while :7169 and :7512 read \"BST supply SW12_U1REF_BST_ACM (K48+K76)\" - the four comment lines are NOT one identical string; the corresponding CALL lines are the next line in each case (:7000/:7087/:7170/:7513)")
        new = new.replace("comments :6997/:7085 name the pin and instrument in one sentence",
                          "comments :6997/:7085 state the pin, the instrument and K48/K76 in one sentence, in the form \"(FH5->BST)\"; the other two sites (:7169/:7512) state the same fact in the \"BST supply ... (K48+K76)\" form - not one identical string")
        if new != x:
            d["limitations"][i] = new
            hits += 1
            print("[%d] AFTER : %s" % (i, new[:400]))
print("\nentries rewritten:", hits)
j = json.dumps(d, ensure_ascii=False)
print("residual '(FH5.BST)'-style claim occurrences:", j.count("(FH5.BST)"))
json.dump(d, open(f, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
b = open(f, "rb").read()
print("t34 (acceptance-report.json):", len(b), "B /", hashlib.sha256(b).hexdigest(), "@", datetime.datetime.fromtimestamp(os.stat(f).st_mtime).strftime("%Y-%m-%d %H:%M:%S"), "| limitations:", len(d["limitations"]))

ap = os.path.join(A, "gate-logs-t28", "setupArchitect-anchors.json")
doc = json.load(open(ap, encoding="utf-8"))
doc["anchors"]["acceptance-report.json"] = {"path": "team/artifacts/acceptance-20260916-dali10/acceptance-report.json", "sizeBytes": len(b),
                                            "sha256": hashlib.sha256(b).hexdigest(),
                                            "measuredAt": datetime.datetime.fromtimestamp(os.stat(f).st_mtime).strftime("%Y-%m-%d %H:%M:%S")}
json.dump(doc, open(ap, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("anchors refreshed")
