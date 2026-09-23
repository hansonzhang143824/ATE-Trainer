# probe_api_generation.py — Captain 只读探针：核实 RDSON 黄金案例与当前 API 代际差异
# 用途：回答 t5 升级的三个问题中的 #1（compliance/SetClamp 在本代是否可用）
# 运行：python team/artifacts/acceptance-20260916-dali10/probe_api_generation.py
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
SRC = "D:/PROJECT6-DALI/ForCodexDebug/source"
FILES = ["test.cpp", "sub.cpp", "StdAfx.h", "Test_Method.h", "Test_Method.cpp", "mylib.h", "treg.h"]


def load(name):
    try:
        return open(f"{SRC}/{name}", encoding="utf-8-sig", errors="replace").read()
    except OSError:
        return ""


texts = {f: load(f) for f in FILES}
blob = "\n".join(texts.values())
print("loaded:", {k: len(v.splitlines()) for k, v in texts.items() if v})

LEGACY = ["SetClamp", "K31_VBUSL_PMID", "K17_BUSH_SW", "K18_BST_SW_Cap", "K30_VBAT_Cap",
          "K28_VDRV_Cap", "K32_PMID_Cap", "BTST_ACM", "PMID_FOVI", "VBAT_ACM",
          "VDRV_AMP_ACM", "FOVIe_40V", "FOVIe_100MA", "FPVI_RELAY_ON", "FPVIe_1V", "FPVIe_2A"]
print("\n--- legacy golden API/relay names in CURRENT debug copy ---")
for n in LEGACY:
    print("  %-18s hits=%d" % (n, blob.count(n)))

CURRENT = ["MeasureVI", "GetMeasResult", "MVRET", "MIRET", "FPVIe_", "FXVIe_", "SetClamp",
           "Compliance", "CPLimit", "ILimit", "VLimit", "SetRange", "SetCurrentRange"]
print("\n--- current-generation instrument API ---")
for n in CURRENT:
    print("  %-18s hits=%d" % (n, blob.count(n)))

print("\n--- compliance/limit candidates (unique method-ish names on instrument objects) ---")
methods = sorted(set(re.findall(r"\.\s*([A-Z][A-Za-z0-9_]{2,})\s*\(", blob)))
print("  all dotted method names:", methods[:60])

for kw in ["Clamp", "Compliance", "CPLimit", "LIMIT"]:
    hits = [(f, i, l.strip()[:150]) for f, t in texts.items()
            for i, l in enumerate(t.splitlines(), 1) if kw in l]
    if hits:
        print(f"\n--- lines containing {kw!r} (first 8) ---")
        for f, i, l in hits[:8]:
            print("  %s:%d %s" % (f, i, l))
