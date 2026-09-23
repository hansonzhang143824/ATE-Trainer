#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""列11 角色继电器定义生成器 (稳压 / P2P / 短路 / 上拉 / 下拉).

读 SCH-Connect-Map.txt 的 `## 列11: 通路分类` 段 → 角色名 #define →
插入工程编译头 StdAfx.h 的 RELAY_ROLE_START..END 段 (幂等替换)。

命名规则 (2026-08-26 用户拍板):
  稳压 (电容≥100nF, 需闭合继电器):  K_<Pin>_Cap            (单端去耦 pin→GND)
                                    K_<Pin1>_<Pin2>_Cap    (两脚电容, 如自举 Cap_SW_BST)
  P2P-到地:                        K_<Pin>_P2P
  P2P-互短 (短路):                 K_<PinA>_<PinB>_ST      (单继电器短接两 DUT 节点)
  上拉:                            K_<Pin>_PU
  下拉:                            K_<Pin>_PD
短路判据 (2026-08-26 用户拍板): 闭合一个继电器(单 CBIT, ≤1)即短接两个 DUT 节点 → 短路继电器。
  源/地 Kelvin F/S (K86/K130/K92) 不是 (用户确认排除)。
  注: K25 (VCC↔ACDRV1/2/3 公共轨) 曾被并入短路, 2026-08-26 用户放弃并入 → 不再硬编码,
  短路仅来自 map 列11 P2P-互短 的直接型 (KLV1↔KLV2 K38)。

值 = 需闭合继电器的 CBIT 值 (逗号分隔)。稳压「需闭合: 无」= 无继电器 → 跳过。

DLP 纪律: StdAfx.h 是 DLP 编译头, 本脚本只经 DLP 环境 (PowerShell python) 运行;
  read_enc 沙箱读到 TSZ# 密文直接报错; write_enc 先编码后写 (编码失败绝不截断)。

用法:
  python gen_relay_role_defines.py --map Project/DALI/SCH-Connect-Map.txt   # 生成+插入
  python gen_relay_role_defines.py --map ... --no-write                    # 仅输出段, 不写
  python gen_relay_role_defines.py --map ... --verify                      # 只校验 StdAfx.h 段
  python gen_relay_role_defines.py --map ... --classify [--out roles.json] # 仅角色分类→JSON (Step0 分类, 不写 StdAfx.h)

角色分类 (--classify, 2026-08-27 方案A): Step0 只做继电器角色分类, 产出结构化分类数据
  供 Step4 环节② relay-agent 查询 (角色类型 → 继电器名 + CBIT); StdAfx.h #define 生成时机不变。
"""
import re, sys, os, argparse, shutil, datetime

SECTION_START = "// ==== RELAY_ROLE_START (gen_relay_role_defines.py) ===="
SECTION_END   = "// ==== RELAY_ROLE_END ===="

CAT_ORDER = {"CAP": 0, "P2P": 1, "ST": 2, "PU": 3, "PD": 4}
CAT_LABEL = {"CAP": "稳压 (电容>=100nF)", "P2P": "P2P-到地 (PIN<->AGND)",
             "ST": "P2P-互短/短路 (PIN<->PIN)", "PU": "上拉", "PD": "下拉"}


# =====================================================================
# A. DLP 安全读写 (与 gen_path_defines.py 同款)
# =====================================================================
def detect_encoding(raw):
    if raw.startswith(b"\xef\xbb\xbf"):
        return "utf-8-sig"
    for enc in ("utf-8", "gbk", "latin-1"):
        try:
            raw.decode(enc)
            return enc
        except (UnicodeDecodeError, ValueError):
            continue
    return "utf-8"


def read_enc(path):
    if str(path).lower().endswith('.json'):
        return read_schematic_text(path), "utf-8"
    with open(path, "rb") as f:
        raw = f.read()
    if raw.startswith(b"TSZ#"):
        raise SystemExit(
            f"ERROR: {path} 是 DLP 加密文件(TSZ#), 沙箱/Bash 读到的是密文。"
            f"请在 DLP 环境(PowerShell python)运行本脚本。")
    return raw.decode(detect_encoding(raw)), detect_encoding(raw)


def write_enc(path, text, encoding):
    # 先编码后打开: 编码失败绝不截断目标文件
    data = text.encode(encoding)
    with open(path, "wb") as f:
        f.write(data)


# =====================================================================
# B. 列11 解析
# =====================================================================
def parse_relay_role(map_text):
    """从 SCH-Connect-Map.txt 列11 段解析 [(category, name, relays_tuple, comp, note)]."""
    defines = []
    in_col11 = False
    sec = []
    for raw in map_text.splitlines():
        s = raw.strip()
        if s.startswith("## 列11"):
            in_col11 = True
            continue
        if in_col11 and s.startswith("## ") and not s.startswith("### "):
            break
        if in_col11:
            sec.append(s)

    cur = None
    for s in sec:
        if s.startswith("### "):
            cur = s
            continue
        if not s or s.startswith(("注:", "[")):
            continue
        if cur is None:
            continue
        toks = s.split()
        # 需闭合: token
        try:
            idx = toks.index("需闭合:")
        except ValueError:
            continue
        rel_tok = toks[idx + 1] if idx + 1 < len(toks) else "无"
        if rel_tok == "无":
            continue  # 无继电器 → 不定义
        relays = tuple(int(x.lstrip("K")) for x in rel_tok.split(","))
        comp = toks[2] if len(toks) > 2 else ""

        if "P2P-到地" in cur:
            pin = toks[0]
            defines.append(("P2P", "K_%s_P2P" % pin, relays, comp, ""))

        elif "P2P-互短" in cur:
            a, b = toks[0], toks[2]
            defines.append(("ST", "K_%s_%s_ST" % (a, b), relays, "", ""))

        elif "上拉" in cur:
            pin = toks[0]
            defines.append(("PU", "K_%s_PU" % pin, relays, comp, ""))

        elif "下拉" in cur:
            pin = toks[0]
            defines.append(("PD", "K_%s_PD" % pin, relays, comp, ""))

        elif "稳压" in cur:
            pin = toks[0]
            m2 = re.match(r"^Cap_(\w+)_(\w+)_S\d+$", comp)
            if m2 and m2.group(1) == pin:
                name = "K_%s_%s_Cap" % (pin, m2.group(2))   # 两脚电容 (如自举 SW↔BST)
            else:
                name = "K_%s_Cap" % pin                     # 单端去耦
            defines.append(("CAP", name, relays, comp, ""))

    return defines


def classify_json(defines):
    """角色分类结构化输出 (Step0 分类, 供 Step4 环节② relay-agent 查询).

    [{category, label, items:[{name, relays, comp}]}], category ∈ CAT_ORDER。
    只分类不生成: 不依赖 StdAfx.h, 不写编译头。
    """
    out = []
    for cat in ("CAP", "P2P", "ST", "PU", "PD"):
        items = sorted((d for d in defines if d[0] == cat), key=lambda d: d[1])
        if not items:
            continue
        out.append({
            "category": cat,
            "label": CAT_LABEL[cat],
            "items": [{"name": name, "relays": list(relays), "comp": comp}
                      for _, name, relays, comp, note in items],
        })
    return {"classify": out, "total": len(defines)}


def build_phys(stdafx_text):
    """从 StdAfx.h 现有单点定义提取 number -> [物理名...] (供注释)."""
    out = {}
    for m in re.finditer(r"#define\s+(K\d+_\w+)\s+(\d+)", stdafx_text):
        out.setdefault(int(m.group(2)), []).append(m.group(1))
    return out


def build_section(defines, phys):
    lines = [SECTION_START,
             "// 列11 角色继电器定义 (值=需闭合继电器 CBIT 值), 规则见 gen_relay_role_defines.py 头"]
    for cat in ("CAP", "P2P", "ST", "PU", "PD"):
        items = sorted((d for d in defines if d[0] == cat), key=lambda d: d[1])
        if not items:
            continue
        lines.append("// -- %s (%d)" % (CAT_LABEL[cat], len(items)))
        for _, name, relays, comp, note in items:
            val = ",".join(str(x) for x in relays)

            def _fmt(r):
                ns = phys.get(r)
                return " + ".join(ns) if ns else "K%d" % r
            names = " + ".join(_fmt(r) for r in relays)
            tail = names
            if comp:
                tail += "  " + comp
            if note:
                tail += "  " + note
            lines.append("#define %-32s %-12s // %s" % (name, val, tail))
    lines.append(SECTION_END)
    return "\n".join(lines) + "\n"


def insert_into_stdafx(text, section):
    """已有 RELAY_ROLE_START → 幂等替换; 否则插到末尾 #endif 前."""
    section = section.rstrip("\r\n") + "\n"
    if SECTION_START in text:
        start = text.index(SECTION_START)
        end = text.index(SECTION_END, start) + len(SECTION_END)
        before = re.sub(r"[\r\n]+$", "\n", text[:start])
        after = re.sub(r"^[\r\n]+", "\n", text[end:])
        return before + section + after
    lines = text.splitlines(keepends=True)
    idx = None
    for i in range(len(lines) - 1, -1, -1):
        if lines[i].lstrip().startswith("#endif"):
            idx = i
            break
    if idx is None:
        raise SystemExit("ERROR: StdAfx.h 无 include guard 末尾 #endif, 无法定位插入点")
    before = "".join(lines[:idx])
    if before and not before.endswith("\n"):
        before += "\n"
    return before + section + "".join(lines[idx:])


def parse_section_defines(text):
    """从 StdAfx.h RELAY_ROLE 段解析 name -> relays."""
    if SECTION_START not in text or SECTION_END not in text:
        return {}
    start = text.index(SECTION_START)
    end = text.index(SECTION_END, start)
    out = {}
    for m in re.finditer(r"#define\s+(K_[A-Za-z0-9_]+)\s+([\d,\s]+)", text[start:end]):
        out[m.group(1)] = tuple(int(x) for x in m.group(2).replace(" ", "").split(","))
    return out


def verify_stdafx(stdafx_text, expected):
    """StdAfx.h RELAY_ROLE 段 vs 期望一致: 缺项/异值/多余 FAIL."""
    errors, warns = [], []
    cur = parse_section_defines(stdafx_text)
    if SECTION_START not in stdafx_text:
        errors.append("StdAfx.h 缺少 RELAY_ROLE 段 (RELAY_ROLE_START 横幅) → 未生成/未插入")
    exp_map = {d[1]: d[2] for d in expected}
    for name, rel in sorted(exp_map.items()):
        if name not in cur:
            errors.append("缺项: %s (数据源=%s)" % (name, ",".join(map(str, rel))))
        elif cur[name] != rel:
            errors.append("异值: %s (StdAfx=%s vs 数据源=%s)"
                          % (name, ",".join(map(str, cur[name])), ",".join(map(str, rel))))
    for name in sorted(cur):
        if name not in exp_map:
            warns.append("StdAfx.h 多余: %s (数据源无此定义)" % name)
    return errors, warns


def backup_stdafx(path, backup_dir):
    os.makedirs(backup_dir, exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    dest = os.path.join(backup_dir, "StdAfx.h.before_role_publish_%s.bak" % ts)
    shutil.copy2(path, dest)
    print("备份: %s" % dest)
    return dest


def main():
    ap = argparse.ArgumentParser(description="列11 角色继电器定义生成器")
    ap.add_argument("--map", required=True, help="SCH-Connect-Map.txt 路径")
    ap.add_argument("--stdafx", default=None, help="StdAfx.h (目标编译头)")
    ap.add_argument("--no-write", action="store_true", help="仅输出 RELAY_ROLE 段, 不写 StdAfx.h")
    ap.add_argument("--verify", action="store_true", help="只校验 StdAfx.h RELAY_ROLE 段 vs 数据源")
    ap.add_argument("--classify", action="store_true",
                    help="仅角色分类→JSON (Step0 分类, 不写 StdAfx.h); 可选 --out 落盘")
    ap.add_argument("--out", default=None, help="--classify 输出文件路径 (默认 stdout)")
    ap.add_argument("--backup-dir", default=None, help="备份目录 (默认 StdAfx.h 同目录 Backup/)")
    args = ap.parse_args()

    map_text, _ = read_enc(args.map)
    defines = parse_relay_role(map_text)
    if not defines:
        raise SystemExit("ERROR: 列11 段解析为空, 检查 --map 内容")
    print("解析到 %d 条角色继电器定义" % len(defines))

    if args.classify:
        import json as _json
        text = _json.dumps(classify_json(defines), ensure_ascii=False, indent=2)
        if args.out:
            write_enc(args.out, text, "utf-8")
            print("已输出角色分类 JSON (%d 条) → %s" % (len(defines), args.out))
        else:
            print(text)
        return

    stdafx = args.stdafx
    if stdafx is None:
        cfg_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "project_config.json")
        if os.path.exists(cfg_path):
            import json
            with open(cfg_path, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            stdafx = cfg.get("derived", {}).get("stdafx_h")
    if not stdafx or not os.path.exists(stdafx):
        raise SystemExit("ERROR: 需 --stdafx <StdAfx.h> (DLP 环境 PowerShell python)")

    stdafx_text, enc = read_enc(stdafx)
    phys = build_phys(stdafx_text)
    section = build_section(defines, phys)

    if args.no_write:
        print(section)
        return

    if args.verify:
        errors, warns = verify_stdafx(stdafx_text, defines)
        for w in warns:
            print("WARN: " + w)
        if errors:
            for e in errors:
                print("FAIL: " + e)
            raise SystemExit(1)
        print("VERIFY PASSED: RELAY_ROLE 段 %d 条与数据源一致" % len(defines))
        return

    new_text = insert_into_stdafx(stdafx_text, section)
    if new_text == stdafx_text:
        print("StdAfx.h RELAY_ROLE 段已是最新, 无需改动")
        return
    backup_dir = args.backup_dir or os.path.join(os.path.dirname(stdafx), "Backup")
    backup_stdafx(stdafx, backup_dir)
    write_enc(stdafx, new_text, enc)
    print("已插入 RELAY_ROLE 段 (%d 定义) → %s" % (len(defines), stdafx))
    errors, warns = verify_stdafx(new_text, defines)
    for w in warns:
        print("WARN: " + w)
    if errors:
        for e in errors:
            print("FAIL: " + e)
        raise SystemExit(1)
    print("VERIFY PASSED: RELAY_ROLE 段 %d 条与数据源一致" % len(defines))


if __name__ == "__main__":
    main()
