#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Per-source-end comparison: SCH-Connect-Map rows vs schematic-ir.json chain.

For each TM108-relevant DUT terminal (F and S) the connect map has rows
"<src> -> K..(Relay-..) -> .. -> <terminal>". The IR has paths PIN_<terminal> with
a relayChainUnion (union over all accepted proofs of that terminal).

This script prints, per terminal:
  - every map row that ends at that terminal (with relay tokens in order)
  - the IR chain entries (name, state)
  - set difference: IR-not-in-map and map-not-in-IR for the relays referenced
Read-only; writes tm108-perpath-compare.txt.
"""
import json
import pathlib
import re

OUT = pathlib.Path(__file__).parent
PROJ = pathlib.Path("project/DALI")


def read_lines(p):
    with open(p, "r", encoding="utf-8", errors="replace", newline="") as fh:
        return fh.read().splitlines()


cm = read_lines(PROJ / "SCH-Connect-Map.txt")
ir = json.loads((PROJ / "schematic-ir.json").read_text(encoding="utf-8"))

TERMINALS = ["VBAT_F", "VBAT_S", "VAC1_F", "VAC1_S", "nQON_F", "nQON_S",
             "AGND_F", "AGND_S", "AMUX_F", "AMUX_S"]
PINID = {"VBAT": "VBAT", "VAC1": "VAC1", "nQON": "nQON", "AGND": "AGND", "AMUX": "AMUX"}

rows_by_terminal = {}
for i, l in enumerate(cm, 1):
    m = re.search(r"->\s*([A-Za-z0-9_]+)\s*$", l)
    if "->" in l and m:
        tok = m.group(1)
        if tok in TERMINALS:
            knums = [int(x) for x in re.findall(r"K(\d+)\(Relay-(?:ON|NC)\)", l)]
            rows_by_terminal.setdefault(tok, []).append({"line": i, "text": l.strip(), "knums": knums})

ir_chain_by_pinid = {}
for p in ir["paths"]:
    if p["id"].startswith("PIN_"):
        ir_chain_by_pinid[p["id"][4:]] = p

buf = []
w = buf.append
for term in TERMINALS:
    pinid = "_".join([term.rsplit("_", 1)[0], term.rsplit("_", 1)[1], "S1"])
    pin_rec = next((p for p in ir["pins"] if p["pin"] == pinid), None)
    path_rec = ir_chain_by_pinid.get(pinid)
    w("==== %s (IR pin %s) ====" % (term, pinid))
    rows = rows_by_terminal.get(term, [])
    w("-- SCH-Connect-Map.txt rows ending at %s: %d" % (term, len(rows)))
    for r in rows:
        w("   %5d| %s   [K=%s]" % (r["line"], r["text"], r["knums"]))
    if path_rec:
        w("-- IR path %s from=%s" % (path_rec["id"], path_rec["from"]))
        for c in path_rec.get("relayChainUnion", []):
            w("   chain %-26s %s" % (c[0], c[1]))
    else:
        w("-- IR path %s: ABSENT" % pinid)
    if pin_rec:
        w("-- IR pin record sources=%s" % pin_rec["sources"])
        w("   requiredRelays=%s nets=%s proofs=%s rejected=%s"
          % (pin_rec["requiredRelays"], pin_rec["nets"], pin_rec["proofCount"], pin_rec["rejectedCount"]))
    # membership comparison
    map_k = set()
    for r in rows:
        map_k.update(r["knums"])
    ir_k = set()
    if path_rec:
        for c in path_rec.get("relayChainUnion", []):
            m = re.match(r"K(\d+)_", c[0])
            if m:
                ir_k.add(int(m.group(1)))
    w("-- K numbers only in IR chain (not on any map row ending at %s): %s" % (term, sorted(ir_k - map_k)))
    w("-- K numbers only on map rows ending at %s (not in IR chain): %s" % (term, sorted(map_k - ir_k)))
    w("")

(OUT / "tm108-perpath-compare.txt").write_text("\n".join(buf) + "\n", encoding="utf-8")
print("WROTE", OUT / "tm108-perpath-compare.txt")
