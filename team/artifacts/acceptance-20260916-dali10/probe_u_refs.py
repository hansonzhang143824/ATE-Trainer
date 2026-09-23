# probe_u_refs.py — 列出契约中所有 U10/U11 引用及其语境，检查跨引用一致性
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
D = os.path.join(os.path.dirname(os.path.abspath(__file__))) + os.sep
c = json.load(open(D + "setup-contract.json", encoding="utf-8"))
c_txt = json.dumps(c, ensure_ascii=False)

print("U10 count:", c_txt.count("U10"), "| U11 count:", c_txt.count("U11"))


def walk(node, path=""):
    if isinstance(node, dict):
        for k, v in node.items():
            yield from walk(v, path + "/" + str(k))
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from walk(v, path + "[%d]" % i)
    else:
        if isinstance(node, str) and ("U10" in node or "U11" in node):
            yield path, node


print("\n--- 所有含 U10/U11 的字段 ---")
for p, s in walk(c):
    for m in re.finditer(r"U1[01]", s):
        seg = s[max(0, m.start() - 70): m.start() + 90].replace("\n", " ")
        print("  %-58s %s ...%s..." % (p[:58], m.group(0), seg))

print("\n--- 一致性判定 ---")
# 期望口径（canonical，用户指令）：U10 = QVM ch0 concurrency；U11 = SIGN-CONVENTION
# 注意：topic 文本可能带 "(verbatim captain text)" 等后缀，故用**关键词**而非全串匹配。
qvm_keys = ("QVM", "concurren")
sign_keys = ("SIGN-CONVENTION", "command-sign", "command sign")
bad = []
for i in c.get("openItems", []):
    if isinstance(i, dict):
        blob = (str(i.get("topic", "")) + " " + str(i.get("detail", ""))[:200])
        if i.get("id") == "U10" and not all(k in blob for k in ("QVM", "concurren")):
            bad.append("U10 不是 QVM 并发性: " + str(i.get("topic")))
        if i.get("id") == "U11" and not any(k in blob for k in sign_keys):
            bad.append("U11 不是 SIGN-CONVENTION: " + str(i.get("topic")))
# 交叉引用：U11 的语境不应是 QVM 并发性；U10 的语境不应是 SIGN-CONVENTION
for p, s in walk(c):
    if "U11" in s and all(k in s for k in qvm_keys) and not any(k in s for k in sign_keys):
        bad.append("引用了 U11 但同时描述 QVM 并发性 @ %s" % p)
    if "U10" in s and any(k in s for k in sign_keys) and not all(k in s for k in qvm_keys):
        bad.append("引用了 U10 但同时描述 SIGN-CONVENTION @ %s" % p)
print("  canonical: U10 = QVM ch0 concurrency | U11 = SIGN-CONVENTION")
print("  problems:", bad if bad else "NONE")
