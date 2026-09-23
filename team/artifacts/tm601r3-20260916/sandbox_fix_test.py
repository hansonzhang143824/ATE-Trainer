# -*- coding: utf-8 -*-
"""Round-10 sandbox test: does landing the proposed K48/K76 closure make the
bst-sw contract-closure assertion pass?

Creates a COPY of the deployed test.cpp under this run's sandbox/ directory,
applies ONLY the proposed one-line edit to TM600's SetOn, and reports:
  - Gate A: fresh copy, unedited            -> expect TM600 missing [48,76]
  - Gate B: copy + K48/K76 added to SetOn   -> expect TM600 missing []
The target tree and devel are never touched.

Run: python .\\sandbox_fix_test.py
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


a = os.path.join(SANDBOX, "test.cpp.copy")
b = os.path.join(SANDBOX, "test.cpp.k48k76")

raw = open(SRC, "rb").read()
open(a, "wb").write(raw)

text = raw.decode("utf-8")
old = ("cbite.SetOn(K83_BUSH0_PMID, K60_BUSL0_VCP, K61_ACM8_SW, K13_VBAT_Cap, "
       "K85_CAP_PMID, K57_CAP_BST_SW, K126_V1P5_CAP, -1);")
new = ("cbite.SetOn(K83_BUSH0_PMID, K60_BUSL0_VCP, K61_ACM8_SW, K13_VBAT_Cap, "
       "K85_CAP_PMID, K57_CAP_BST_SW, K126_V1P5_CAP, K48_ACM5_AMP_REF, K76_ACM_BST, -1);")
n = text.count(old)
print("anchor occurrences:", n)
assert n == 1, "expected exactly one anchor"
open(b, "wb").write(text.replace(old, new).encode("utf-8"))


def gate(path):
    cmd = ["python", os.path.join(WS, "scripts", "verify_bst_sw_sequence.py"),
           "--src", path, "--contract", CONTRACT]
    p = subprocess.run(cmd, cwd=WS, capture_output=True, text=True, encoding="utf-8", errors="replace")
    out = (p.stdout or "") + (p.stderr or "")
    keep = [l for l in out.splitlines() if "[t30]" in l or "[scan]" in l or "FAIL" in l or "PASS" in l]
    return p.returncode, keep


result = {}
for tag, path in (("A_unedited_copy", a), ("B_k48_k76_added", b)):
    rc, lines = gate(path)
    result[tag] = {"path": path, "size": sig(path)[0], "sha256": sig(path)[1],
                   "exit": rc, "lines": lines}
    print("\n=====", tag, "size", result[tag]["size"], "sha256", result[tag]["sha256"][:16], "exit", rc)
    for l in lines:
        print("   ", l[:200])

json.dump(result, open(os.path.join(SANDBOX, "fix-test-result.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=2)
print("\ntarget tree untouched:", sig(SRC))
print("devel:", sig(r"D:\PROJECT6-DALI\devel\source\test.cpp"))
