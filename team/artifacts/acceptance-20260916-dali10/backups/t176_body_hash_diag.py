# -*- coding: utf-8 -*-
"""Diagnose why the peer's reproducibleBodySha256 cannot be reproduced: scan for nested timestamp fields."""
import json, hashlib, os, re, datetime

A = r"team/artifacts/acceptance-20260916-dali10"
br_p = os.path.join(A, "build-report.json")
raw = open(br_p, "rb").read().decode("utf-8")
d = json.loads(raw)

ISO = re.compile(r"\b(20\d\d-\d\d-\d\d[T ]\d\d:\d\d(?::\d\d)?)")
time_keys = []
def walk(node, path):
    if isinstance(node, dict):
        for k, v in node.items():
            if isinstance(v, str) and ISO.search(v):
                time_keys.append(((".".join(path + [str(k)])) if path else str(k), v[:24]))
            walk(v, path + [str(k)])
    elif isinstance(node, list):
        for i, v in enumerate(node):
            walk(v, path + ["[%d]" % i])
walk(d, [])
print("string fields containing a timestamp-like value: %d" % len(time_keys))
for p, v in time_keys[:20]:
    print("   ", p, "=", v)
print("   ..." if len(time_keys) > 20 else "")

present_at = [p for p, v in time_keys if v.startswith("2026-09-17")]
print("\nfields whose timestamp is 2026-09-17 (i.e. generation-time):", len(present_at))

# how many distinct conventions produce distinct hashes?
stripped = {k: v for k, v in d.items() if k != "generatedAt"}
cands = {
    "canonical json, generatedAt removed (sorted keys)": hashlib.sha256(json.dumps(stripped, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest(),
    "canonical json, generatedAt removed (insertion order)": hashlib.sha256(json.dumps(stripped, ensure_ascii=False).encode("utf-8")).hexdigest(),
    "canonical json, ALL timestamp-valued string fields blanked (sorted)": None,
}
import copy
def blank(node):
    if isinstance(node, dict):
        return {k: ("<TS>" if isinstance(v, str) and ISO.search(v) else blank(v)) for k, v in node.items()}
    if isinstance(node, list):
        return [blank(v) for v in node]
    return node
blanked = blank(d)
cands["canonical json, ALL timestamp-valued string fields blanked (sorted)"] = hashlib.sha256(json.dumps(blanked, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()
for k, v in cands.items():
    print("  %-64s %s" % (k, v))

rc = json.load(open(os.path.join(A, "gate-logs-t54", "build-report.receipt.json"), encoding="utf-8"))
print("\ntheir recorded reproducibleBodySha256:", rc.get("reproducibleBodySha256"))
print("their receipt keys:", sorted(rc.keys()))
print("their reproducibleNote:", str(rc.get("reproducibleNote"))[:200])
print("\n=> reproduced? ", any(v == rc.get("reproducibleBodySha256") for v in cands.values() if v))
print("file size now:", os.path.getsize(br_p), "B (their message cited 31,821 B, so the file has moved since)")
