# probe_f5_and_ranges.py — 核验 F5 阻值/零流处理 与 全部 FXVIe/ACM 量程配对
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
P = "team/artifacts/acceptance-20260916-dali10/implementation-payload-TM600-TM601.cpp"
src = open(P, "rb").read().decode("utf-8-sig")
lines = src.splitlines()

print("=== A. F5 阻值计算 / 零流门限 / 符号注释 ===")
for i, ln in enumerate(lines, 1):
    if re.search(r"MVRET|MIRET|v_meas|i_meas|0\.1|RDSON|rdson|polarity|negative|fabs", ln):
        s = ln.strip()
        if len(s) > 4:
            print("  L%-4d %s" % (i, s[:200]))

print("\n=== B. 全部 Set(FV, <value>, <range>) 配对（量程 ≥2× 判定）===")
pat = re.compile(r"(\w+)\.Set\(\s*FV\s*,\s*(-?[\d.]+)\s*,\s*(\w+)\s*,\s*(\w+)")
for i, ln in enumerate(lines, 1):
    m = pat.search(ln)
    if m:
        pin, val, rng, irng = m.group(1), float(m.group(2)), m.group(3), m.group(4)
        if rng.startswith("FXVIe_PLUS_"):
            rv = {"FXVIe_PLUS_3p6V": 3.6, "FXVIe_PLUS_10V": 10, "FXVIe_PLUS_20V": 20,
                  "FXVIe_PLUS_30V": 30, "FXVIe_PLUS_40V": 40}.get(rng, 0)
        elif rng.startswith("ACM200_"):
            rv = {"ACM200_3p6V": 3.6, "ACM200_10V": 10, "ACM200_20V": 20, "ACM200_40V": 40}.get(rng, 0)
        elif rng.startswith("FPVIe_"):
            rv = {"FPVIe_1V": 1, "FPVIe_2V": 2, "FPVIe_5V": 5, "FPVIe_10V": 10,
                  "FPVIe_20V": 20, "FPVIe_40V": 40, "FPVIe_100V": 100}.get(rng, 0)
        else:
            rv = 0
        ok = (val == 0) or (rv >= 2 * val)
        print("  L%-4d %-22s set=%-6s range=%-18s (%sV)  >=2x: %s" % (i, pin, val, rng, rv, "OK" if ok else "VIOLATION"))

print("\n=== C. 注释中与 -1 A / negative 相关的行（TM600 vs TM601 段落定位）===")
cur = ""
for i, ln in enumerate(lines, 1):
    if "DUT_API" in ln and "TM6" in ln:
        cur = ln.strip()[:80]
    if re.search(r"-1 A|negative|magnitude", ln):
        print("  L%-4d [%s] %s" % (i, cur[:40], ln.strip()[:170]))
