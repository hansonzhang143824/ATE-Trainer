# probe_u_numbering.py — 查清 U10/U11 的真实归属（契约 + 计划）
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
D = os.path.join(os.path.dirname(os.path.abspath(__file__))) + os.sep


def topics(path, label):
    c = json.load(open(D + path, encoding="utf-8"))
    print("=== %s ===" % label)
    seen = []
    for key in ("openItems", "limitations"):
        for it in (c.get(key) or []):
            s = it if isinstance(it, str) else json.dumps(it, ensure_ascii=False)
            if "U10" in s or "U11" in s:
                seen.append((key, s[:230]))
    for k, s in seen[:14]:
        print("  [%s] %s" % (k, s))
    return seen


topics("setup-contract.json", "setup-contract.json (live 326363 B)")
print()
topics("test-plan.json", "test-plan.json (frozen v12 148150 B)")
