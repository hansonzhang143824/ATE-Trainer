#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Per-proof relay chains for the TM108 terminals (t3).

Reads project/DALI/path_proofs.json.txt (the engine's per-proof evidence file
cited by schematic-ir.json) and prints, for every accepted proof whose
dut_pin is one of the TM108-relevant terminals, the full relay chain with
relay number, instance, state, contact pins and net-to-net transition.

Read-only. Writes tm108-paths-proofs.txt / .json.
"""
import json
import pathlib

OUT = pathlib.Path(__file__).parent
PINS = ["VAC1_F_S1", "VAC1_S_S1", "VBAT_F_S1", "VBAT_S_S1",
        "nQON_F_S1", "nQON_S_S1", "AGND_F_S1", "AGND_S_S1"]


def main():
    d = json.loads(pathlib.Path("project/DALI/path_proofs.json.txt").read_text(encoding="utf-8"))
    ap = d["accepted_path_proofs"]
    rp = d["rejected_paths"]
    res = {"counts": d["counts"], "status": d["status"], "proofs": {}, "rejected": {}}
    lines = []
    w = lines.append
    w("# per-proof relay chains, source = project/DALI/path_proofs.json.txt")
    w("# engine=%s status=%s counts=%s" % (d.get("engine"), d.get("status"), json.dumps(d["counts"])))
    for pin in PINS:
        ps = [p for p in ap if p["dut_pin"] == pin]
        res["proofs"][pin] = ps
        w("")
        w("==== %s : %d accepted proofs ====" % (pin, len(ps)))
        for p in ps:
            sm = p.get("source_meta", {})
            w("-- source_port=%s type=%s role=%s side=%s ch=%s domain=%s pair=%s"
              % (p["source_port"], sm.get("type"), sm.get("role"), sm.get("side"),
                 sm.get("channel"), sm.get("domain"), sm.get("pair_key")))
            w("   dut_net=%s required_on=%s terminal_stop=%s cbit=%s"
              % (p["dut_net"], p["required_on"], p.get("terminal_stop"),
                 json.dumps(p.get("cbit"), ensure_ascii=False)))
            w("   validation=%s" % json.dumps(p.get("validation"), ensure_ascii=False))
            if not p.get("path"):
                w("   path = []  (EMPTY: no relay transition recorded; port net == dut net group)")
            for s in p.get("path") or []:
                w("   %-22s #%-4s state=%-3s pin%s->pin%s  %s -> %s"
                  % (s["relay"], s["relay_number"], s["state"], s["from_pin"],
                     s["to_pin"], s["from_net"], s["to_net"]))
        rps = [p for p in rp if p["dut_pin"] == pin]
        res["rejected"][pin] = [{"source_port": p["source_port"], "dut_net": p["dut_net"],
                                 "reason": p.get("validation") or p.get("reject_reason")}
                                for p in rps]
        if rps:
            w("-- rejected proofs for %s: %d" % (pin, len(rps)))
            for x in res["rejected"][pin][:12]:
                w("   src=%-22s net=%-28s reason=%s"
                  % (x["source_port"], x["dut_net"], json.dumps(x["reason"], ensure_ascii=False)[:200]))
    (OUT / "tm108-paths-proofs.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (OUT / "tm108-paths-proofs.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    print("WROTE tm108-paths-proofs.txt/.json")
    print("accepted", len(ap), "rejected", len(rp), "status", d["status"],
          "issues", len(d.get("issues", [])), "warnings", d.get("warnings"))


if __name__ == "__main__":
    main()
