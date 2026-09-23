# -*- coding: utf-8 -*-
"""Deep field search: exact JSON paths for the fields rule-reviewer could not find, and check for a naming mismatch between my two carriers."""
import json, hashlib, os

A = r"team/artifacts/acceptance-20260916-dali10"
TARGETS = ["knownSpecsRegister", "specRegister", "identityAddendum", "prohibitedInferenceConvention"]

def paths(node, path, acc, targets):
    if isinstance(node, dict):
        for k, v in node.items():
            if k in targets:
                acc.append(".".join(path + [k]))
            paths(v, path + [k], acc, targets)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            paths(v, path + ["[%d]" % i], acc, targets)

for rel in ("gate-logs-t28/setupArchitect-anchors.json", "gate-logs-t28/setupArchitect-freeze-snapshots.json"):
    p = os.path.join(A, rel)
    doc = json.load(open(p, encoding="utf-8"))
    acc = []
    paths(doc, [], acc, set(TARGETS))
    print("==", rel, "==")
    for a in acc:
        print("   ", a)
    if not acc:
        print("    (none)")
