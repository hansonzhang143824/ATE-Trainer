# -*- coding: utf-8 -*-
"""Round-11 sandbox test: TM601 BST-leg fix + novelty check.

1) Applies ONLY the TM601 change to a fresh sandbox copy:
   add K48_ACM5_AMP_REF + K76_ACM_BST to TM601's single SetOn.
2) Runs the bst-sw contract-closure gate on it (expect exit 0).
3) NOVELTY CHECK: scans every deployed function for a single cbite.SetOn whose
   token list contains all of {K154|K155, K60, K61, K48, K76} - i.e. the exact
   combination the TM601 fix would create. If no deployed function has that
   combination, the fix is electrically UNPRECEDENTED and must be reviewed
   electrically, not merely by the text-set gate.

Target tree and devel are never modified.
"""
import hashlib
import json
import os
import re
import subprocess

RUN = os.path.dirname(os.path.abspath(__file__))
WS = r"D:\Newtest\DSH\ATE-Coding-Plat"
SRC = r"D:\PROJECT6-DALI\ForCodexDebug\source\test.cpp"
CONTRACT = os.path.join(RUN, "snapshot", "setup_contract.json")
SANDBOX = os.path.join(RUN, "sandbox")
os.makedirs(SANDBOX, exist_ok=True)


def sig(p):
    with open(p, "rb") as f:
        b = f.read()
    return len(b), hashlib.sha256(b).hexdigest()


text = open(SRC, "rb").read().decode("utf-8")
lines = text.splitlines()

# ---------- 1) build the TM601-fixed copy ----------
anchor_old = ("cbite.SetOn(K154_BUSH0_AMUX, K155_FOVI3_PGND, K60_BUSL0_VCP, K61_ACM8_SW, "
              "K13_VBAT_Cap, K85_CAP_PMID, K57_CAP_BST_SW, K126_V1P5_CAP, -1);")
anchor_new = ("cbite.SetOn(K154_BUSH0_AMUX, K155_FOVI3_PGND, K60_BUSL0_VCP, K61_ACM8_SW, "
              "K13_VBAT_Cap, K85_CAP_PMID, K57_CAP_BST_SW, K126_V1P5_CAP, "
              "K48_ACM5_AMP_REF, K76_ACM_BST, -1);")
n = text.count(anchor_old)
print("TM601 anchor occurrences:", n)
assert n == 1, "expected exactly one TM601 anchor"
fixed = os.path.join(SANDBOX, "test.cpp.tm601_bstleg")
open(fixed, "wb").write(text.replace(anchor_old, anchor_new).encode("utf-8"))
print("fixed:", sig(fixed))

# ---------- 2) gate ----------
cmd = ["python", os.path.join(WS, "scripts", "verify_bst_sw_sequence.py"),
       "--src", fixed, "--contract", CONTRACT]
p = subprocess.run(cmd, cwd=WS, capture_output=True, text=True, encoding="utf-8", errors="replace")
out = (p.stdout or "") + (p.stderr or "")
print("gate exit:", p.returncode)
for l in out.splitlines():
    if "[t30]" in l or "[scan]" in l or "FAIL" in l or "PASS" in l:
        print("   ", l[:190])

# ---------- 3) novelty check over the DEPLOYED tree ----------
funcs = [(i + 1, m.group(1)) for i, l in enumerate(lines)
         for m in [re.search(r"DUT_API\s+int\s+(\w+)\s*\(short\s+funcindex", l)] if m]
combo = []
for idx, (ln, name) in enumerate(funcs):
    end = funcs[idx + 1][0] - 1 if idx + 1 < len(funcs) else len(lines)
    block = "\n".join(lines[ln - 1:end])
    for m in re.finditer(r"cbite\.SetOn\((.*?)\);", block, re.DOTALL):
        toks = m.group(1)
        has = lambda t: re.search(r"\b" + t + r"\b", toks) is not None
        if (has("K154_BUSH0_AMUX") or has("K155_FOVI3_PGND")) and has("K60_BUSL0_VCP") \
           and has("K61_ACM8_SW") and has("K48_ACM5_AMP_REF") and has("K76_ACM_BST"):
            combo.append(name)
print("\nfunctions whose SetOn contains {K154|K155 + K60 + K61 + K48 + K76}:", combo or "NONE")

# also: does any function close K48/K76 AND K60/K61 AND K83 (the TM600 fix shape)?
shape600 = []
for idx, (ln, name) in enumerate(funcs):
    end = funcs[idx + 1][0] - 1 if idx + 1 < len(funcs) else len(lines)
    block = "\n".join(lines[ln - 1:end])
    for m in re.finditer(r"cbite\.SetOn\((.*?)\);", block, re.DOTALL):
        toks = m.group(1)
        has = lambda t: re.search(r"\b" + t + r"\b", toks) is not None
        if has("K48_ACM5_AMP_REF") and has("K76_ACM_BST") and has("K60_BUSL0_VCP") \
           and has("K61_ACM8_SW") and has("K83_BUSH0_PMID"):
            shape600.append(name)
print("functions whose SetOn contains {K48 + K76 + K60 + K61 + K83} (TM600 fix shape):", shape600 or "NONE")

json.dump({
    "tm601_fixed": {"path": fixed, "size": sig(fixed)[0], "sha256": sig(fixed)[1]},
    "gate_exit": p.returncode,
    "t30_lines": [l for l in out.splitlines() if "[t30]" in l],
    "novelty_tm601_combo": combo,
    "novelty_tm600_shape": shape600,
}, open(os.path.join(SANDBOX, "tm601-fix-test-result.json"), "w", encoding="utf-8"),
    ensure_ascii=False, indent=2)
print("\ntarget:", sig(SRC), "devel:", sig(r"D:\PROJECT6-DALI\devel\source\test.cpp"))
