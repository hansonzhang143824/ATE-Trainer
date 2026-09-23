#!/usr/bin/env python3
"""Apply the golden-code BST-SW staircase invariant to TM607..TM609.

Invariant throughout power transitions:
    BST >= SW and 0 V <= BST-SW <= 5 V
Target operating point:
    BST-SW = 5 V
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected one match, got {count}")
    return text.replace(old, new, 1)


def function_block(text: str, name: str) -> tuple[int, int, str]:
    start = text.index(f"DUT_API int {name}")
    next_start = text.find("DUT_API int ", start + 1)
    end = len(text) if next_start < 0 else next_start
    return start, end, text[start:end]


def update_function(text: str, name: str, transform) -> str:
    start, end, block = function_block(text, name)
    updated = transform(block)
    return text[:start] + updated + text[end:]


def adapt_tm607(block: str) -> str:
    block = replace_once(
        block,
        "cbite.SetOn(K_FPVIH_TO_PGND_A, K_FPVIL_TO_SW1_A, K13_VBAT_Cap, K65_nQON_PU, -1);",
        "cbite.SetOn(K_FPVIH_TO_PGND_A, K_FPVIL_TO_SW1_A, K13_VBAT_Cap, "
        "K45_Cap_SW1_BST1, K65_nQON_PU, -1);",
        "TM607 relay",
    )
    old_power = (
        "    // vset[vbat,3.5] / vset[pmid,5] / vset[vdrv,5]\r\n"
        "    VBAT_PD3_FXVI.Set(FV, 3.5, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);\r\n"
        "    PMID_HG2_FXVI.Set(FV, 5, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);\r\n"
        "    V1P5_U34PS_FXVI.Set(FV, 5, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);  // VDRV=V1P5 短接\r\n"
        "    delay_ms(1);\r\n"
        "    // FPVI0 浮动源初始化: FV=0 + FI=0 (为电流 ramp 做准备)\r\n"
        "    FPVI0.Set(FV, 0, FPVIe_1V, FPVIe_2A, FPVIe_RELAY_ON);\r\n"
        "    delay_us(200);\r\n"
        "    FPVI0.Set(FI, 0, FPVIe_1V, FPVIe_2A, FPVIe_RELAY_ON);\r\n"
        "    delay_us(200);"
    )
    new_power = (
        "    // Golden LSZCD: 先用 FPVI0 FV=0 固定 SW=PGND=0，再建立 BST-SW=5V\r\n"
        "    // 全程保证 BST>=SW 且 BST-SW<=5V\r\n"
        "    FPVI0.Set(FV, 0, FPVIe_1V, FPVIe_2A, FPVIe_RELAY_ON);\r\n"
        "    delay_us(200);\r\n"
        "    VBAT_PD3_FXVI.Set(FV, 3.5, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);\r\n"
        "    BST12_U1PS_ACM.Set(FV, 5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);  // SW=0V, BST-SW=5V\r\n"
        "    V1P5_U34PS_FXVI.Set(FV, 5, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);  // VDRV=V1P5 短接\r\n"
        "    PMID_HG2_FXVI.Set(FV, 5, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);\r\n"
        "    delay_ms(1);"
    )
    block = replace_once(block, old_power, new_power, "TM607 power-on")
    block = replace_once(
        block,
        "    test_method.rampi_capv(FPVI0, FPVIe_1V, FPVIe_2A,",
        "    // LS FET 已导通后才从 FV 切 FI，避免切换期间 SW 浮动\r\n"
        "    FPVI0.Set(FI, 0, FPVIe_1V, FPVIe_2A, FPVIe_RELAY_ON);\r\n"
        "    delay_us(200);\r\n"
        "    test_method.rampi_capv(FPVI0, FPVIe_1V, FPVIe_2A,",
        "TM607 measure handoff",
    )
    old_down = (
        "    FPVI0.Set(FI, 0, FPVIe_1V, FPVIe_2A, FPVIe_RELAY_ON);\r\n"
        "    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);\r\n"
        "    PMID_HG2_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);\r\n"
        "    V1P5_U34PS_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);\r\n"
        "    NQON_HG1_ACM.Set(FV, 0, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);  // nQON cap 源下电"
    )
    new_down = (
        "    FPVI0.Set(FI, 0, FPVIe_1V, FPVIe_2A, FPVIe_RELAY_ON);\r\n"
        "    FPVI0.Set(FV, 0, FPVIe_1V, FPVIe_2A, FPVIe_RELAY_ON);  // 保持 SW=PGND=0\r\n"
        "    PMID_HG2_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);\r\n"
        "    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);\r\n"
        "    V1P5_U34PS_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);\r\n"
        "    BST12_U1PS_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);\r\n"
        "    NQON_HG1_ACM.Set(FV, 0, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);  // nQON cap 源下电"
    )
    block = replace_once(block, old_down, new_down, "TM607 power-off")
    block = replace_once(
        block,
        "    V1P5_U34PS_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);\r\n"
        "    NQON_HG1_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);",
        "    V1P5_U34PS_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);\r\n"
        "    BST12_U1PS_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);\r\n"
        "    NQON_HG1_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);",
        "TM607 relay-off",
    )
    return block


def adapt_hs(block: str, name: str, irange: str, has_vdrv: bool) -> str:
    block = replace_once(
        block,
        "cbite.SetOn(K_FPVIH_TO_PMID_A, K_FPVIL_TO_SW1_A, K13_VBAT_Cap, K65_nQON_PU, -1);",
        "cbite.SetOn(K_FPVIH_TO_PMID_A, K_FPVIL_TO_SW1_A, K13_VBAT_Cap, "
        "K45_Cap_SW1_BST1, K65_nQON_PU, -1);",
        f"{name} relay",
    )
    start = block.index("    // ====== Step 2: Power On")
    end = block.index("    // ====== Step 3: Register Config", start)
    old_section = block[start:end]
    vdrv_on = (
        "    V1P5_U34PS_FXVI.Set(FV, 5, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);  // VDRV=V1P5 短接\r\n"
        if has_vdrv else ""
    )
    new_section = (
        "    // ====== Step 2: Power On (BST-SW 台阶上电) ======\r\n"
        "    // Golden HS_ZCD: FPVI0 FV=0 先固定 PMID=SW，再用独立源建立 BST-SW=5V\r\n"
        "    // 全程保证 BST>=SW 且 BST-SW<=5V\r\n"
        f"    FPVI0.Set(FV, 0, FPVIe_1V, {irange}, FPVIe_RELAY_ON);\r\n"
        "    delay_us(200);\r\n"
        "    VBAT_PD3_FXVI.Set(FV, 3.5, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);\r\n"
        "    BST12_U1PS_ACM.Set(FV, 5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);  // PMID=SW=0V, BST-SW=5V\r\n"
        + vdrv_on +
        "    delay_us(200);\r\n"
        "    PMID_HG2_FXVI.Set(FV, 5, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);  // FPVI FV=0 使 SW 跟随到 5V\r\n"
        "    delay_us(200);\r\n"
        "    BST12_U1PS_ACM.Set(FV, 10, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON); // SW=5V, BST-SW=5V\r\n"
        "    delay_ms(1);\r\n\r\n"
    )
    block = block[:start] + new_section + block[end:]
    block = replace_once(
        block,
        f"    test_method.rampi_capv(FPVI0, FPVIe_1V, {irange},",
        "    // HS FET 已导通后才从 FV 切 FI，保证切换前 PMID=SW\r\n"
        f"    FPVI0.Set(FI, 0, FPVIe_1V, {irange}, FPVIe_RELAY_ON);\r\n"
        "    delay_us(200);\r\n"
        f"    test_method.rampi_capv(FPVI0, FPVIe_1V, {irange},",
        f"{name} measure handoff",
    )
    down_start = block.index("    // ====== Step 5: Power Off")
    down_end = block.index("    // ====== Step 6: LogData", down_start)
    vdrv_down = (
        "    V1P5_U34PS_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);\r\n"
        if has_vdrv else ""
    )
    vdrv_off = (
        "    V1P5_U34PS_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);\r\n"
        if has_vdrv else ""
    )
    new_down = (
        "    // ====== Step 5: Power Off (BST-SW 反向台阶下电) ======\r\n"
        f"    FPVI0.Set(FI, 0, FPVIe_1V, {irange}, FPVIe_RELAY_ON);\r\n"
        f"    FPVI0.Set(FV, 0, FPVIe_1V, {irange}, FPVIe_RELAY_ON);  // PMID=SW=5V\r\n"
        "    BST12_U1PS_ACM.Set(FV, 5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);  // BST-SW: 5V->0V\r\n"
        "    delay_us(200);\r\n"
        "    PMID_HG2_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);  // SW 跟随到 0V, BST-SW=5V\r\n"
        "    delay_us(200);\r\n"
        "    BST12_U1PS_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);\r\n"
        + vdrv_down +
        "    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);\r\n"
        "    NQON_HG1_ACM.Set(FV, 0, ACM200_10V, ACM200_10UA, ACM200_RELAY_ON);\r\n"
        "    delay_ms(1);\r\n"
        "    FPVI0.Set(FV, 0, FPVIe_10V, FPVIe_10MA, FPVIe_RELAY_OFF);\r\n"
        "    PMID_HG2_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);\r\n"
        "    BST12_U1PS_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);\r\n"
        + vdrv_off +
        "    VBAT_PD3_FXVI.Set(FV, 0, FXVIe_PLUS_10V, FXVIe_PLUS_10MA, FXVIe_PLUS_RELAY_OFF);\r\n"
        "    NQON_HG1_ACM.Set(FV, 0, ACM200_10V, ACM200_10MA, ACM200_RELAY_OFF);\r\n\r\n"
    )
    block = block[:down_start] + new_down + block[down_end:]
    return block


def main() -> int:
    workspace = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(description="Apply BST-SW golden-code sequence")
    parser.add_argument("--production", action="store_true")
    parser.add_argument("--confirmed", action="store_true")
    args = parser.parse_args()
    if args.production and not args.confirmed:
        raise SystemExit("ERROR: production edit requires --confirmed")
    sys.path.insert(0, str(workspace))
    from gen_path_defines import read_enc, write_enc

    if args.production:
        config = json.loads((workspace / "project_config.json").read_text(encoding="utf-8-sig"))
        target = Path(config["inputs"]["vs_src_dir"]) / "test.cpp"
    else:
        target = workspace / "Project" / "DALI" / "hardware_parse_v2" / "vs_compile_sandbox" / "devel" / "source" / "test.cpp"
    target = target.resolve()
    text, encoding = read_enc(target)
    if "Step 2: Power On (BST-SW 台阶上电)" in text and "K45_Cap_SW1_BST1" in function_block(text, "TM607_BUCK_LS_ZCD")[2]:
        print(f"BST-SW golden sequence already applied: {target}")
        return 0

    text = update_function(text, "TM607_BUCK_LS_ZCD", adapt_tm607)
    text = update_function(text, "TM608_BOOST_HS_ZCD", lambda b: adapt_hs(b, "TM608", "FPVIe_2A", False))
    text = update_function(text, "TM609_BOOST_HS_NEG", lambda b: adapt_hs(b, "TM609", "FPVIe_10A", True))

    backup = None
    if args.production:
        backup_dir = target.parent / "Backup"
        backup_dir.mkdir(parents=True, exist_ok=True)
        backup = backup_dir / f"test.cpp.before_bst_sw_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}.bak"
        shutil.copy2(target, backup)
    write_enc(target, text, encoding)
    print(f"BST-SW golden sequence applied: {target}")
    print("Invariant: BST>=SW and 0<=BST-SW<=5V; target BST-SW=5V")
    print(f"Production modified: {args.production}")
    if backup:
        print(f"Backup: {backup}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
