#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TM108 schematic fact extractor (evidence helper for t3).

Reads the three project schematic artifacts, extracts TM108-relevant physical
facts and writes them as UTF-8 JSON + readable TXT for inspection/citation.

Artifacts (project/DALI/):
  SCH-Connect-Map.txt     plain text  (PowerShell-readable)
  Component-Statistic.txt plain text  (PowerShell-readable)
  schematic-ir.json       DLP/TSZ transparent-encryption file: on-disk bytes are
                          ciphertext starting with b'TSZ#'; only a DLP-authorized
                          process (python) sees the plaintext JSON. Hash policy:
                          on-disk ciphertext hash (Get-FileHash) differs from the
                          python-read sha256 -> both are recorded.

Read-only: this script never writes into project/DALI.
"""

import hashlib
import json
import os
import pathlib
import re
import sys

PROJ = pathlib.Path("project/DALI")
OUT = pathlib.Path("team/artifacts/tm108-v2-trial/schematic")
RUNID = "tm108-v2-trial"

ARTIFACTS = ["SCH-Connect-Map.txt", "Component-Statistic.txt", "schematic-ir.json"]

# TM108-relevant DUT terminals (from the DFT-declared check pin + the plain-text
# DFT dump / test-code block facts supplied by the captain pre-check):
#   VBAT  : static supply for the item
#   VAC1  : ramped input (threshold search)
#   nQON  : observation terminal carrying the digital DTEST0 level
#   AGND  : reference return
TM_PINS = {
    "VBAT": ["VBAT_F_S1", "VBAT_S_S1"],
    "VAC1": ["VAC1_F_S1", "VAC1_S_S1", "VAC_WL_F_S1", "VAC_WL_S_S1"],
    "nQON": ["nQON_F_S1", "nQON_S_S1"],
    "AGND": ["AGND_F_S1", "AGND_S_S1"],
}
KEYWORDS = ["VAC1", "VBAT", "nQON", "DTEST", "AGND", "K13", "K65", "K21", "K64"]
# DFT-declared check pin (TM108): the digital test-output muxed onto nQON
DFT_CHECK_PIN = "DTEST0"


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def read_text(p):
    """Read raw bytes via python (DLP-authorized) and report both hash views.

    The bytes are decoded CRLF-preserving (newline='') so that the python-read
    sha256 is byte-identical to the on-disk hash for non-encrypted files.
    """
    disk = p.read_bytes()                      # ciphertext view on disk
    with open(p, "r", encoding="utf-8", errors="replace", newline="") as fh:
        text = fh.read()                       # python/DLP plaintext view
    plain = text.encode("utf-8")
    return {
        "path": str(p).replace("\\", "/"),
        "size_disk": len(disk),
        "size_python": len(plain),
        "sha256_disk_ciphertext": sha256_bytes(disk),
        "sha256_python_plaintext": sha256_bytes(plain),
        "hash_views_match": sha256_bytes(disk) == sha256_bytes(plain),
        "lines_crlf": disk.count(b"\r\n"),
        "lines_lf_total": disk.count(b"\n"),
        "on_disk_head_hex": disk[:8].hex(" "),
        "dlp_header_on_disk": disk[:4] == b"TSZ#",
        "text": text,
    }


def grep_lines(lines, kws):
    out = []
    pat = re.compile("|".join(re.escape(k) for k in kws), re.IGNORECASE)
    for i, l in enumerate(lines, 1):
        if pat.search(l):
            out.append({"line": i, "text": l.rstrip()})
    return out


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    report = {
        "runId": RUNID,
        "task": "t3 TM108 schematic fact audit - extract",
        "artifacts": {},
        "tm108_pins_from_ir": {},
        "relays_from_ir": {},
        "connect_map_hits": {},
        "component_stat_hits": {},
        "ir_self_validation": {},
    }

    loaded = {}
    for name in ARTIFACTS:
        info = read_text(PROJ / name)
        loaded[name] = info
        report["artifacts"][name] = {k: v for k, v in info.items() if k != "text"}

    ir = json.loads(loaded["schematic-ir.json"]["text"])
    pins = {p["pin"]: p for p in ir["pins"]}
    paths_by_id = {p["id"]: p for p in ir["paths"]}
    relays_by_number = {}
    for r in ir["relays"]:
        relays_by_number.setdefault(int(r["number"]), {})[r["instance"]] = r

    for group, pinids in TM_PINS.items():
        report["tm108_pins_from_ir"][group] = []
        for pid in pinids:
            p = pins.get(pid)
            if not p:
                report["tm108_pins_from_ir"][group].append({"pin": pid, "present": False})
                continue
            path = paths_by_id.get("PIN_" + pid)
            entry = {
                "pin": pid,
                "present": True,
                "base": p["base"],
                "role": p["role"],
                "nets": p["nets"],
                "sources": p["sources"],
                "requiredRelays": p["requiredRelays"],
                "proofCount": p["proofCount"],
                "rejectedCount": p["rejectedCount"],
                "kelvinPairs": p["kelvinPairs"],
            }
            if path:
                entry["path_to"] = path["to"]
                entry["path_from"] = path["from"]
                entry["confidence"] = path["confidence"]
                entry["relayChainUnion"] = path["relayChainUnion"]
                entry["path_nets"] = path["nets"]
                entry["path_evidence"] = path.get("evidence", [])
                entry["kelvinPairDetail"] = path.get("kelvinPairs", [])
            report["tm108_pins_from_ir"][group].append(entry)

    # relay facts for every relay number appearing on the TM108 pin paths
    nums = set()
    for group in report["tm108_pins_from_ir"].values():
        for e in group:
            if e.get("present"):
                nums.update(e.get("requiredRelays", []))
    report["relays_from_ir"]["relay_numbers_on_tm108_pins"] = sorted(nums)
    report["relays_from_ir"]["detail"] = []
    for n in sorted(nums):
        insts = relays_by_number.get(n, {})
        for inst, r in insts.items():
            report["relays_from_ir"]["detail"].append({
                "number": n,
                "instance": inst,
                "name": r.get("name"),
                "state_default": r.get("state"),
                "proofCount": r.get("proofCount"),
                "dutPins": r.get("dutPins"),
                "evidence": r.get("evidence"),
            })

    report["ir_self_validation"] = {
        "runId": ir.get("runId"),
        "generatedAt": ir.get("generatedAt"),
        "generatedBy": ir.get("generatedBy"),
        "engine": ir.get("engine"),
        "scope": ir.get("scope"),
        "pinsPerTm": ir.get("pinsPerTm"),
        "scopeNote": ir.get("scopeNote"),
        "counts": {k: (len(v) if isinstance(v, list) else v)
                   for k, v in ir.items() if isinstance(v, list)},
        "status": ir["validation"].get("status"),
        "checks": ir["validation"].get("checks"),
        "determinismVsCanonical": ir["validation"].get("determinismVsCanonical"),
        "issues": ir["validation"].get("issues"),
        "warnings": ir["validation"].get("warnings"),
        "openQuestions": ir.get("openQuestions"),
        "inputs": ir.get("inputs"),
        "sources": ir.get("sources"),
    }

    # grep raw text artifacts for TM108-relevant keywords
    for name in ["SCH-Connect-Map.txt", "Component-Statistic.txt"]:
        lines = loaded[name]["text"].splitlines()
        hits = grep_lines(lines, KEYWORDS)
        key = "connect_map_hits" if name.startswith("SCH") else "component_stat_hits"
        report[key] = {"file": name, "total_lines": len(lines),
                       "hit_count": len(hits), "hits": hits}

    (OUT / "tm108-extract.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")

    # readable rendering
    txt = []
    txt.append("# TM108 extract (generated by tm108-sch-extract.py)")
    for name in ARTIFACTS:
        a = report["artifacts"][name]
        txt.append(f"\n== {name} == size_disk={a['size_disk']} size_python={a['size_python']}"
                   f" dlp_header_on_disk={a['dlp_header_on_disk']}"
                   f" hash_views_match={a['hash_views_match']}"
                   f"\n   sha256_disk={a['sha256_disk_ciphertext']}"
                   f"\n   sha256_python={a['sha256_python_plaintext']}")
    txt.append("\n## IR pins (TM108 relevant)")
    txt.append(json.dumps(report["tm108_pins_from_ir"], ensure_ascii=False, indent=1))
    txt.append("\n## IR relays on TM108 pin paths")
    txt.append(json.dumps(report["relays_from_ir"], ensure_ascii=False, indent=1))
    txt.append("\n## IR self validation")
    txt.append(json.dumps(report["ir_self_validation"], ensure_ascii=False, indent=1))
    for key in ["connect_map_hits", "component_stat_hits"]:
        txt.append(f"\n## {key} ({report[key]['file']}): {report[key]['hit_count']} hits"
                   f" of {report[key]['total_lines']} lines")
        for h in report[key]["hits"]:
            txt.append(f"{h['line']:5d}| {h['text']}")
    (OUT / "tm108-extract.txt").write_text("\n".join(txt) + "\n", encoding="utf-8")

    hits_txt = []
    for key in ["connect_map_hits", "component_stat_hits"]:
        h = report[key]
        hits_txt.append(f"##### {key} {h['file']} hits={h['hit_count']} of {h['total_lines']} lines")
        for x in h["hits"]:
            hits_txt.append(f"{x['line']:5d} | {x['text']}")
        hits_txt.append("")
    (OUT / "tm108-keyword-hits.txt").write_text("\n".join(hits_txt) + "\n", encoding="utf-8")
    print("WROTE", OUT / "tm108-keyword-hits.txt")

    print("WROTE", OUT / "tm108-extract.json")
    print("WROTE", OUT / "tm108-extract.txt")
    for name in ARTIFACTS:
        a = report["artifacts"][name]
        print(f"{name}: disk={a['size_disk']} python={a['size_python']}"
              f" dlp_header_on_disk={a['dlp_header_on_disk']}"
              f" hash_views_match={a['hash_views_match']}")
    print("connect_map hits:", report["connect_map_hits"]["hit_count"])
    print("component_stat hits:", report["component_stat_hits"]["hit_count"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
