# -*- coding: utf-8 -*-
"""Independent verification: (1) the owner's mirroredContentSha256 names a real revision of my ledger; (2) their CRLF chain definition holds."""
import json, hashlib, os, datetime

A = r"team/artifacts/acceptance-20260916-dali10"
LOG = os.path.join(A, "gate-logs-t28", "setupArchitect-freeze-snapshots.json")
raw = open(LOG, "rb").read()
rec = "acee857ed8501427357579a0bb03def2"
print("my ledger NOW:", len(raw), "B /", hashlib.sha256(raw).hexdigest()[:24])

lg = json.loads(raw.decode("utf-8"))
hits = []
def walk(node, path):
    if isinstance(node, dict):
        for k, v in node.items():
            walk(v, path + [k])
    elif isinstance(node, list):
        for i, v in enumerate(node):
            walk(v, path + ["[%d]" % i])
    elif isinstance(node, str) and node.startswith(rec):
        hits.append(".".join(path))
walk(lg, [])
print("occurrences of the recorded mirror hash inside my ledger:", len(hits))
for h in hits[:8]:
    print("   ", h)

rows = [l for l in open(os.path.join(A, "gate-logs-t54", "build-report.receipts.jsonl"), "rb").read().splitlines() if l.strip()]
print("\nreceipts.jsonl rows:", len(rows), "| CRLF line endings:", all(r.endswith(b"\r") for r in rows))
def chain(strip):
    bad = 0
    prev = None
    for r in rows:
        try:
            o = json.loads(r.decode("utf-8"))
        except Exception:
            bad += 1
            continue
        pl = o.get("prevLineSha256")
        if prev is not None and pl is not None and pl != hashlib.sha256(prev.rstrip(strip)).hexdigest():
            bad += 1
        prev = r
    return bad
print("mismatches with rstrip(b'\\r\\n') [their definition]:", chain(b"\r\n"), "/", len(rows))
print("mismatches with rstrip(b'\\n')   [the wrong way]      :", chain(b"\n"), "/", len(rows))
