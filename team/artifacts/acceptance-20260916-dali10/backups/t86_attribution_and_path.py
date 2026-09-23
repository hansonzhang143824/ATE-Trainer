# NOTE (record-preserving annotation, added after schematic-expert's scan): this draft script contains a historical misspelling of a function name.
# The misspelled token in the lookup list below is intended to be TM643_VBAT_LOOP_INDICTOR (source truth: test.cpp L7717).
# The line is left as written for record fidelity; the occurrence is explained here so a future grep does not mis-read it.
# -*- coding: utf-8 -*-
"""Verify which function encloses the four BST-supply sites and what the deployed TM600 block actually does; then patch t34 and add a markdown carrier pointer."""
import json, hashlib, os, datetime, re

DEP = r"D:/PROJECT6-DALI/ForCodexDebug/source/test.cpp"
A = r"team/artifacts/acceptance-20260916-dali10"
L = open(DEP, encoding="utf-8", errors="replace").read().splitlines()

def enclosing_function(lineno):
    for i in range(lineno - 1, 0, -1):
        m = re.search(r"DUT_API\s+int\s+(\w+)", L[i - 1])
        if m:
            return i, m.group(1)
    return None, None

print("--- enclosing function for the four BST-supply sites ---")
for n in (7000, 7087, 7170, 7513, 7623, 7734, 9081):
    ln, fn = enclosing_function(n)
    print("L%-6d -> %-26s (function starts at L%s)" % (n, fn, ln))

print("\n--- deployed TM600_HS_RDSON block ---")
start = end = None
for i, l in enumerate(L, 1):
    if "DUT_API int TM600_HS_RDSON" in l:
        start = i
    elif start and "DUT_API int" in l and i > start:
        end = i; break
print("block = L%s-%s" % (start, end - 1))
blk = "\n".join(L[start - 1:end - 1])
print("  SW12_U1REF_BST_ACM refs:", blk.count("SW12_U1REF_BST_ACM"), "| .Set calls:", len(re.findall(r"SW12_U1REF_BST_ACM\.Set\(", blk)))
print("  K48/K76/K109/K110 in block:", blk.count("K48_"), blk.count("K76_"), blk.count("K109_"), blk.count("K110_"))
calls = [(start - 1 + i + 1, L[start - 1 + i].strip()[:120]) for i, l in enumerate(blk.splitlines()) if "cbite.SetOn" in l]
print("  SetOn calls in the TM600 block:", calls if calls else "NONE")
print("  ACM calls:", [l.strip()[:120] for l in blk.splitlines() if "SW12_U1REF_BST_ACM" in l][:4])

# patch t34
f34 = os.path.join(A, "acceptance-report.json")
d = json.load(open(f34, encoding="utf-8"))
L44 = ("L44 (OWNER-ATTRIBUTION CORRECTION, accepted from the reviewer's t56 - recorded so the two facts are never merged): the four BST-supply sites at test.cpp:6997/7000, 7085/7087, 7169/7170 and 7512/7513 belong to OTHER items "
       "(the reviewer's t56 names TM607/TM608/TM609/TM640, with L7623 -> TM641_BST_UV and L7734 -> TM643_VAT_LOOP_INDICTOR closing legs through composite macros) - they are NOT the deployed TM600 behaviour. "
       "The DEPLOYED TM600_HS_RDSON block is L9057-9216 and its ONLY cbite.SetOn call point is L9081, which does not close K48/K76 (and correctly closes no K109/K110). Any statement of the form 'the deployed TM600 does not close K48/K76' must therefore be pinned to L9081; it must NOT be generalised to "
       "'the deployed TM600's four call sites are all unclosed' and the four sites above must not be presented as TM600's behaviour. This report's own T32-F1 wording (L1/L20) already pins the missing closure to :9081; this entry removes any ambiguity.")
if L44 not in d["limitations"]:
    d["limitations"].append(L44)
json.dump(d, open(f34, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
b = open(f34, "rb").read()
print("\nt34:", len(b), "B /", hashlib.sha256(b).hexdigest(), "@", datetime.datetime.fromtimestamp(os.stat(f34).st_mtime).strftime("%Y-%m-%d %H:%M:%S"), "| limitations:", len(d["limitations"]))

# markdown carrier pointer with ABSOLUTE path
abs_carrier = os.path.abspath(f34).replace("\\", "/")
md = ("# t34 carrier path (unambiguous)\n\n"
      "`t34` is a TASK LABEL and appears in no filename.\n\n"
      "* carrier (absolute): `%s`\n"
      "* carrier (workspace-relative): `team/artifacts/acceptance-20260916-dali10/acceptance-report.json`\n"
      "* current bytes: %d B / `%s` @ %s\n"
      "* the t34 entries are `limitations[]` in that JSON (L1..L44)\n"
      "* the only other `*t34*` name in the tree is a script: `team/artifacts/acceptance-20260916-dali10/backups/superseded-scratch/t60_apply_captain_t34_t35_t41.py`\n") % (
      abs_carrier, len(b), hashlib.sha256(b).hexdigest(), datetime.datetime.fromtimestamp(os.stat(f34).st_mtime).strftime("%Y-%m-%d %H:%M:%S"))
out = os.path.join(A, "t34-CARRIER-PATH.md")
open(out, "w", encoding="utf-8").write(md)
mb = open(out, "rb").read()
print("markdown pointer:", out, len(mb), "B /", hashlib.sha256(mb).hexdigest())
print("absolute carrier:", abs_carrier)
