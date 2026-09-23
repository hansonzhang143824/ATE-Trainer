#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Systematic three-artifact consistency test for the TM108 audit (t3).

Compares, per relay, the three state facts:
  A) SCH-Connect-Map.txt  ->  every "K<n>(Relay-ON|Relay-NC)" row token
  B) schematic-ir.json    ->  relays[].state plus every
                              paths[].relayChainUnion entry [instanceName, state]
  C) Component-Statistic.txt -> the three relay bucket lists
                              ("需闭合=默认ON" / 默认NC / 默认导通)
and reports a per-relay matrix plus the disagreement counts.

Read-only on project/DALI. Writes tm108-consistency-check.txt / .json.
"""
import json
import pathlib
import re

OUT = pathlib.Path(__file__).parent
PROJ = pathlib.Path("project/DALI")


def read_lines(name):
    with open(PROJ / name, "r", encoding="utf-8", errors="replace", newline="") as fh:
        return fh.read().splitlines()


cm = read_lines("SCH-Connect-Map.txt")
cs = read_lines("Component-Statistic.txt")
ir = json.loads((PROJ / "schematic-ir.json").read_text(encoding="utf-8"))

# ---------- A) connect map per-row tokens ----------
map_rows = []           # (line, knum, inst_token, state)
for i, l in enumerate(cm, 1):
    for m in re.finditer(r"K(\d+)\(Relay-(ON|NC)\)", l):
        map_rows.append({"line": i, "knum": int(m.group(1)), "token": m.group(0), "state": m.group(2)})

map_header = {}         # knum -> set of "需闭合: K.." header lines
for i, l in enumerate(cm, 1):
    if "需闭合" in l:
        for m in re.finditer(r"K(\d+)", l):
            map_header.setdefault(int(m.group(1)), []).append(i)

# ---------- B) IR ----------
ir_relay_state = {}     # name -> state ; number -> set(states)
for r in ir["relays"]:
    ir_relay_state[r["name"]] = r["state"]
ir_num_states = {}
for r in ir["relays"]:
    ir_num_states.setdefault(int(r["number"]), set()).add(r["state"])
ir_chain = {}           # name -> set of states over all path chains
for p in ir["paths"]:
    for name, st in p.get("relayChainUnion", []):
        ir_chain.setdefault(name, set()).add(st)

# ---------- C) component statistic buckets ----------
def bucket_after(label, lines):
    names = set()
    for i, l in enumerate(lines, 1):
        if label in l:
            for m in re.finditer(r"\b(K\d+_[A-Za-z0-9_]+)", l):
                names.add(m.group(1))
            # continuation lines that are pure lists
            j = i
            while j < len(lines) and lines[j].strip().startswith("K"):
                for m in re.finditer(r"\b(K\d+_[A-Za-z0-9_]+)", lines[j]):
                    names.add(m.group(1))
                j += 1
            depth = 0
    return names

cs_on = bucket_after("\u9ed8\u8ba4ON", cs)          # 默认ON
cs_nc = bucket_after("\u9ed8\u8ba4NC", cs)          # 默认NC
cs_dflt = bucket_after("\u9ed8\u8ba4\u5bfc\u901a", cs)  # 默认导通

# ---------- matrix ----------
nums = sorted(set(list(map_header.keys()) + [x["knum"] for x in map_rows] + list(ir_num_states.keys())))
rows = []
for n in nums:
    prefixes = [x["token"] for x in map_rows if x["knum"] == n]
    map_states = sorted({x["state"] for x in map_rows if x["knum"] == n})
    ir_states = sorted(ir_num_states.get(n, []))
    names = [nm for nm in ir_relay_state if re.match(r"K%d\b" % n, nm)]
    ir_chain_states = {}
    for nm in ir_relay_state:
        if re.match(r"K%d\b" % n, nm) and nm in ir_chain:
            ir_chain_states[nm] = sorted(ir_chain[nm])
    cs_bucket = None
    for nm in list(cs_on) + list(cs_nc) + list(cs_dflt):
        pass
    cs_names_on = [nm for nm in cs_on if re.match(r"K%d_" % n, nm)]
    cs_names_nc = [nm for nm in cs_nc if re.match(r"K%d_" % n, nm)]
    cs_names_dflt = [nm for nm in cs_dflt if re.match(r"K%d_" % n, nm)]
    rows.append({
        "knum": n,
        "map_row_tokens": prefixes,
        "map_row_states": map_states,
        "map_header_lines": map_header.get(n, []),
        "ir_relay_names": names,
        "ir_relay_states": ir_states,
        "ir_chain_states": ir_chain_states,
        "cs_in_ON_bucket": cs_names_on,
        "cs_in_NC_bucket": cs_names_nc,
        "cs_in_default_on_bucket": cs_names_dflt,
    })

# disagreement summary
disagree = []
for r in rows:
    ms = set(r["map_row_states"])
    iss = set(r["ir_relay_states"])
    if ms and iss and ms != iss:
        disagree.append(r)

# bucket size sanity
res = {
    "counts": {
        "map_rows_with_tokens": len(map_rows),
        "map_header_k_numbers": len(map_header),
        "ir_relays": len(ir["relays"]),
        "cs_bucket_ON": len(cs_on),
        "cs_bucket_NC": len(cs_nc),
        "cs_bucket_default_on": len(cs_dflt),
    },
    "map_row_state_value_counts": {},
    "map_rows_of_K_on_the_TM108_pin_paths": {
        str(n): [x for x in map_rows if x["knum"] == n]
        for n in [7, 8, 13, 17, 18, 19, 20, 21, 62, 64, 65, 66, 70, 82, 86, 87,
                  88, 89, 90, 130, 136, 137, 138, 139, 140, 141, 142, 143, 144,
                  145, 146, 154, 155]
    },
    "ir_state_by_instance": ir_relay_state,
    "ir_chain_states_by_instance": {k: sorted(v) for k, v in sorted(ir_chain.items())},
    "cs_buckets": {
        "default_ON": sorted(cs_on),
        "default_NC": sorted(cs_nc),
        "default_conducting": sorted(cs_dflt),
    },
    "per_relay": rows,
    "disagreements_map_vs_ir": disagree,
}
for r in map_rows:
    res["map_row_state_value_counts"][r["state"]] = res["map_row_state_value_counts"].get(r["state"], 0) + 1

(OUT / "tm108-consistency-check.json").write_text(
    json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")

txt = []
txt.append("### counts")
txt.append(json.dumps(res["counts"], ensure_ascii=False, indent=1))
txt.append("### map row token states: %s" % res["map_row_state_value_counts"])
txt.append("### CS buckets")
txt.append(json.dumps(res["cs_buckets"], ensure_ascii=False, indent=1))
txt.append("### IR chain states per instance (state per instance as used in path chains)")
for k, v in res["ir_chain_states_by_instance"].items():
    txt.append("%-24s %s" % (k, v))
txt.append("### IR relays[].state per instance")
for k, v in ir_relay_state.items():
    txt.append("%-24s %s" % (k, v))
txt.append("### per-relay matrix (TM108-relevant K numbers)")
for r in rows:
    if r["knum"] in [7, 8, 13, 17, 18, 19, 20, 21, 62, 64, 65, 66, 70, 82, 86, 87, 88, 89, 90,
                     130, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 154, 155]:
        txt.append(json.dumps(r, ensure_ascii=False))
txt.append("### DISAGREEMENTS (map row states vs IR relay states) count=%d" % len(disagree))
for r in disagree:
    txt.append(json.dumps({k: r[k] for k in ["knum", "map_row_states", "map_row_tokens",
                                             "ir_relay_names", "ir_relay_states",
                                             "cs_in_ON_bucket", "cs_in_NC_bucket",
                                             "cs_in_default_on_bucket"]}, ensure_ascii=False))
(OUT / "tm108-consistency-check.txt").write_text("\n".join(txt) + "\n", encoding="utf-8")
print("WROTE tm108-consistency-check.json/.txt")
print("counts:", json.dumps(res["counts"]))
print("disagreements map-vs-IR:", len(disagree))
print("cs buckets:", {k: len(v) for k, v in res["cs_buckets"].items()})
