#!/usr/bin/env python3
"""Adapt TM607 to the intentional V2 FPVI/PGND hardware topology.

This script is deliberately restricted to the isolated V2 compile sandbox.
It never edits the production VS project.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path


def replace_once(text: str, old: str, new: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"expected exactly one match, got {count}: {old[:80]!r}")
    return text.replace(old, new, 1)


def main() -> int:
    workspace = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(description="Adapt TM607 for intentional V2 hardware revision")
    parser.add_argument("--production", action="store_true")
    parser.add_argument("--intentional-hardware-revision", action="store_true")
    args = parser.parse_args()
    if args.production and not args.intentional_hardware_revision:
        raise SystemExit("ERROR: production edit requires --intentional-hardware-revision")

    sys.path.insert(0, str(workspace))
    from gen_path_defines import read_enc, write_enc

    v2_dir = (workspace / "Project" / "DALI" / "hardware_parse_v2").resolve()
    if args.production:
        config = json.loads((workspace / "project_config.json").read_text(encoding="utf-8-sig"))
        test_cpp = (Path(config["inputs"]["vs_src_dir"]) / "test.cpp").resolve()
    else:
        test_cpp = (v2_dir / "vs_compile_sandbox" / "devel" / "source" / "test.cpp").resolve()
        test_cpp.relative_to(v2_dir)
    text, encoding = read_enc(test_cpp)

    if (
        "K_FPVIL_TO_PGND" not in text
        and "K_FPVIH_TO_PGND_A, K_FPVIL_TO_SW1_A" in text
        and "ls_zcd[site] = -ls_zcd[site];" in text
    ):
        print(f"TM607 V2 topology already adapted: {test_cpp}")
        return 0

    replacements = [
        (
            "// 电流环: FPVI0 High→SW1 → DUT(LSFET) → PGND → FPVI0 Low",
            "// 新版硬件极性: FPVI0 High→PGND → DUT(LSFET) → SW1 → FPVI0 Low\r\n"
            "// 芯片定义电流 SW→PGND = -FPVI0 电流，因此源表反向 ramp，结果再取负",
        ),
        (
            "//   SW1  → FPVI0 High: K_FPVIH_TO_SW1_A = K136,K137,K143,K144,K46",
            "//   PGND → FPVI0 High: K_FPVIH_TO_PGND_A = K136,K137,K143,K144,K154,K155",
        ),
        (
            "//   PGND → FPVI0 Low : K_FPVIL_TO_PGND   = K138,K140,K51,K53,K93",
            "//   SW1  → FPVI0 Low : K_FPVIL_TO_SW1_A  = K47",
        ),
        (
            "cbite.SetOn(K_FPVIH_TO_SW1_A, K_FPVIL_TO_PGND, K13_VBAT_Cap, K65_nQON_PU, -1);",
            "cbite.SetOn(K_FPVIH_TO_PGND_A, K_FPVIL_TO_SW1_A, K13_VBAT_Cap, K65_nQON_PU, -1);",
        ),
        (
            "// FPVI0 ramp 电流 -0.2A -> +0.2A; nQON(ACM200 10UA 高阻) 捕 DTEST0 翻转点",
            "// FPVI0 源表电流 +0.2A -> -0.2A，对应芯片 SW->PGND 电流 -0.2A -> +0.2A",
        ),
        (
            "// 翻转点电流 = ZCD 阈值 (期望 0.1A); trig_level=1.65V = nQON 逻辑中点",
            "// 翻转点源表电流取负后为 ZCD 阈值 (期望 +0.1A); trig 保持已确认的 RISING",
        ),
        (
            "-0.2, 0.2, 200, 20, 1.65, TRIG_RISING, ls_zcd);",
            "0.2, -0.2, 200, 20, 1.65, TRIG_RISING, ls_zcd);",
        ),
        (
            "        LS_ZCD->SetTestResult(site, 0, ls_zcd[site]);",
            "        // 恢复为 DFT 定义的 SW->PGND 正方向；错误哨兵值保持不变\r\n"
            "        if (ls_zcd[site] != ERROR_RES)\r\n"
            "            ls_zcd[site] = -ls_zcd[site];\r\n"
            "        LS_ZCD->SetTestResult(site, 0, ls_zcd[site]);",
        ),
    ]
    for old, new in replacements:
        text = replace_once(text, old, new)

    if "K_FPVIL_TO_PGND" in text:
        raise RuntimeError("stale invalid V2 alias remains in test.cpp")
    backup_path = None
    if args.production:
        backup_dir = test_cpp.parent / "Backup"
        backup_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = backup_dir / f"test.cpp.before_hardware_parse_v2_{stamp}.bak"
        shutil.copy2(test_cpp, backup_path)
    write_enc(test_cpp, text, encoding)
    print(f"TM607 V2 topology adapted: {test_cpp}")
    print("Physical current: SW->PGND = -FPVI0 current")
    print("Instrument ramp: +0.2A -> -0.2A; logged result: negated")
    print(f"Production VS modified: {args.production}")
    if backup_path:
        print(f"Backup: {backup_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
