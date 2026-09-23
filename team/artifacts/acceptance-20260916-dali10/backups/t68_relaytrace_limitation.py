# -*- coding: utf-8 -*-
"""t34: add the relay-trace parse_defines truncation limitation (verification limitation + discipline class 5); align channelsInScope.BST wording to 'closed by t53'; drop the relays.md contradiction item."""
import json, hashlib, os, datetime, re

A = r"team/artifacts/acceptance-20260916-dali10"

# ---- independent check of the claimed regex/truncation ----
rt = "scripts/verify_relay_trace.py"
src = open(rt, encoding="utf-8").read().splitlines()
print("--- verify_relay_trace.py lines 35-50 ---")
for i in range(35, 51):
    if i <= len(src):
        print("%4d| %s" % (i, src[i - 1].rstrip()[:150]))
pat = re.search(r"r'#define\\s\+\(K\\d\*_\\w\+\)\\s\+\(\\d\+\)'", "\n".join(src))
print("regex found in file:", bool(pat))
std = open(r"D:/PROJECT6-DALI/ForCodexDebug/source/StdAfx.h", encoding="utf-8", errors="replace").read().splitlines()
multi = [l.strip() for l in std if re.match(r"#define\s+K\d*_\w+\s+\d+\s*,", l)]
print("multi-value K macros in StdAfx.h:", len(multi))
for l in multi[:5]:
    print("   ", l[:120])

# ---- t34: locate wording to update ----
f34 = os.path.join(A, "acceptance-report.json")
d = json.load(open(f34, encoding="utf-8"))
for i, x in enumerate(d["limitations"]):
    if "channelsInScope" in x or "relays.md" in x.lower() or "自相矛盾" in x or "L21-27" in x or "L29/L31" in x:
        print("\n[%d] %s" % (i, x[:200].replace("\n", " ")))

# ---- apply ----
L37 = ("L37 (VERIFICATION LIMITATION - silent truncation in a helper; registered discipline class 5 'helper != semantics'): scripts/verify_relay_trace.py:39-44 parse_defines() uses the regex "
       "r'#define\\s+(K\\d*_\\w+)\\s+(\\d+)', which captures only the FIRST number of a macro, so every multi-value macro in StdAfx.h is silently truncated - measured: "
       + str(len(multi)) + " such macros, e.g. K_FPVIH_TO_BST_A -> 46 (true 46,48,76), K_FPVIL_TO_SW_A -> 60 (true 60,61), K_BST_ACM -> 48 (true 48,76). Scope measured: the function is referenced only by verify_relay_trace.py "
       "(verify_bst_sw_sequence.py contains zero references), so the bst-sw expectation is NOT affected; but wherever defines[name] is used as 'which relays does this name close', macro routes are under-counted - a bias toward FALSE MISSING, never a false pass. "
       "Consequently: (i) a relay-trace PASS must NOT be presented as evidence about multi-value macro routes; (ii) whether relay-trace itself consumes the truncated value as a criterion is UNKNOWN (load/consumption points were traced but not exhaustively enumerated); "
       "(iii) the remedy (fix the regex / add an assertion / record the limitation in writing) is an OWNER DECISION and must not be improvised by editing a gate script inside this task. Mitigation discipline: smoke-assert an expander with a KNOWN multi-value macro before trusting its output.")
if L37 not in d["limitations"]:
    d["limitations"].append(L37)

changed = []
for i, x in enumerate(d["limitations"]):
    y = x
    if "channelsInScope.BST" in y and ("rev 30" in y or "still" in y or "残留" in y or "pending" in y):
        y = y + (" CORRECTION (captain): this residue is CLOSED by t53 - the live contract has channelsInScope.BST in the channel-5 form with the original string preserved as BST_original_t49. "
                 "Only the 'ACM200 row split per channel' item remains listed as a rev-30 follow-up.")
    if ("L21-27" in y or "L29/L31" in y or "自相矛盾" in y) and "撤回" not in y:
        y = y + (" CORRECTION (reviewer retraction, accepted): the 'relays.md table contradicts its mnemonic' item is WITHDRAWN - the reviewer confirmed that the L18 column is a STATE column (not a contact-type column) and that the table, the L29 mnemonic and the L31 warning agree. "
                 "What remains: (i) terminology standardisation to un-actuated/actuated, and (ii) the negative-list rule 'default-conducting relays must not be added to required-on and must not be actuated'. "
                 "Also retained: un-actuated lands on PB0 only for the channel-18 leg; for channel 5 the un-actuated path goes K48(NC) -> K49(NC) -> SW1_F (K49 actuated -> SW2_F).")
    if y != x:
        d["limitations"][i] = y; changed.append(i)
print("\nupdated entries:", changed)
json.dump(d, open(f34, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
b = open(f34, "rb").read()
print("t34:", len(b), "B /", hashlib.sha256(b).hexdigest(), "@", datetime.datetime.fromtimestamp(os.stat(f34).st_mtime).strftime("%Y-%m-%d %H:%M:%S"), "| limitations:", len(d["limitations"]))

ap = os.path.join(A, "gate-logs-t28", "setupArchitect-anchors.json")
doc = json.load(open(ap, encoding="utf-8"))
doc["anchors"]["acceptance-report.json"] = {"path": "team/artifacts/acceptance-20260916-dali10/acceptance-report.json", "sizeBytes": len(b),
                                            "sha256": hashlib.sha256(b).hexdigest(),
                                            "measuredAt": datetime.datetime.fromtimestamp(os.stat(f34).st_mtime).strftime("%Y-%m-%d %H:%M:%S")}
json.dump(doc, open(ap, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("anchors:", os.path.getsize(ap), "B")
