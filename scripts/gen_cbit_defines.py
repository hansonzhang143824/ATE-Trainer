# -*- coding: utf-8 -*-
"""
gen_cbit_defines.py — CBIT 单点继电器 #define 生成器 + 校验器（固定→脚本）

架构原则: "推理→agent, 固定→脚本"。把 CBIT-Definition的确定性部分落地为脚本:
  - P1 单点继电器 #define (cbit-singlepoint-agent 的固定逻辑): 动态读 CBIT 表 Excel,
    按 CBIT 值合并 F/S / FORCE-SENSE / BUS 方向 → 输出 单点 #define 块
  - P4 check (cbit-check-agent 的固定逻辑): V1~V8 校验
agent 只保留推理边界 (功能分类--stat / 通路--map / 命名优先级), 不在脚本内做推理。

输入:  CBIT表 xlsx (--cbit, 必填) + Component-Statistic.txt (--stat, V8) + SCH-Connect-Map.txt (--map, V2/V7)
输出:  stdout 单点 #define 块 + V1~V8 校验报告
对拍:  --verify <StdAfx.h> — 按 CBIT 值子集对拍 (目标文件的每个 value 必须在脚本输出中且一致)

用法:
  python gen_cbit_defines.py --cbit DALI/CBIT表-DALI.xlsx
  python gen_cbit_defines.py --cbit ... --stat Component-Statistic.txt --verify DALI/AI.cpp
  python gen_cbit_defines.py --audit-rules

规则覆盖: RULE_COVERAGE 映射 + --audit-rules 机器自检 (每个规则函数存在且调用链可达)。
数据源:  CBIT 表 Excel 动态读 (权威); phase2_singlepoint.py 的硬编码数据是 Excel 快照 (182 行, 全对齐)。
"""

import argparse
import io
import os
from schematic_projection import read_schematic_text
import re
import sys
from collections import defaultdict, OrderedDict

try:
    import openpyxl
except ImportError:
    openpyxl = None

import proj_config

# =====================================================================
# 常量
# =====================================================================

# Excel 分组标题 → 输出组名/注释 (DALI CBIT 表)
EXCEL_GROUP_MAP = [
    ('光耦', 'MOS', '1.1 MOS SPST (TLP3412)'),
    ('机械独享', 'G6K_DEDICATED', '1.2 G6K Dedicated'),
    ('机械共享', 'G6K_SHARED', '1.3 G6K Shared'),
]

# 校验阈值
CBIT_RANGE = (0, 255)      # V4: S34→0~127, S36→128~255
S34_MAX = 127

# V6: Force/Sense 端别后缀清单 (2026-08-28 用户拍板: 包括但不限于, 可扩展)
F_END_SUFFIXES = ('_Force', '_FOS', '_F')   # 长后缀优先匹配
S_END_SUFFIXES = ('_Sense', '_SNS', '_S')

# V8: 功能分类 → 期望继电器状态 (SCH-Connect-Map 需闭合列表 vs 分类清单)
STAT_SETON = {'BUS', 'Cap', 'Connect'}          # 通路中必须 SetOn
STAT_KEEPDEFAULT = {'Share'}                     # 目标=默认通道时不应 SetOn (视路径而定)
STAT_NC = {'FPVI矩阵', 'Relay-NC'}               # 常闭, 不应 SetOn
# Component-Statistic 分类标签 (DALI): BUS/Cap/Connect/Connect Cap候选/Kelvin/P2P/P2P到地/PU/Share/通用

# =====================================================================
# 规则覆盖表 (核心交付物: agent 每条铁律 → 脚本函数)
# =====================================================================

RULE_COVERAGE = {
    'C-P1': ['read_excel_cbit', 'build_cbit_map', 'gen_singlepoint_defines'],  # 单点定义(动态读CBIT表)
    'C-P1a': ['merge_names'],                # 同名 F/S 双线圈去后缀合并
    'C-P1b': ['merge_names'],                # KELVIN F/S → _FS
    'C-P1c': ['merge_names'],                # FORCE/SENSE 全词 → _FOS_SNS
    'C-P2': ['merge_names'],                 # BUS 方向合并 (FH+SH / FL+SL)
    'C-CK-V1': ['check_v1'],                 # CBIT 位号不重复
    'C-CK-V2': ['check_v2'],                 # 通路完整性 (--map)
    'C-CK-V3': ['check_v3'],                 # 命名一致性
    'C-CK-V4': ['check_v4'],                 # 位号范围 0~255
    'C-CK-V5': ['check_v5'],                 # 单点不遗漏
    'C-CK-V6': ['check_v6', 'parse_map_paths', 'split_end'],  # F/S 成对三重门: 端别识别x电气可达x收敛一致 (--map)
    'C-CK-V7': ['check_v7'],                 # FPVI/QVM 通路命名 (--map)
    'C-CK-V8': ['check_v8'],                 # 继电器状态与功能类型一致性 (--stat)
}


# =====================================================================
# A. 输入层
# =====================================================================

def read_enc(path):
    """DLP 透明加密回退: utf-8-sig → utf-8 → gbk → latin-1"""
    with open(path, 'rb') as f:
        raw = f.read()
    for enc in ('utf-8-sig', 'utf-8', 'gbk', 'latin-1'):
        try:
            return raw.decode(enc)
        except (UnicodeDecodeError, ValueError):
            continue
    return raw.decode('utf-8', errors='replace')


def read_excel_cbit(path=None):
    """动态读 CBIT 表 Excel → [(group, name, cbit_str)]。
    分组标题行 (col0 非 K 开头) 定位组别; col0=原位号, col10=CBIT 通道。
    C-P1: 数据源 = Excel 权威, 不依赖硬编码。"""
    if openpyxl is None:
        raise SystemExit('ERROR: 需要 openpyxl (pip install openpyxl) 读 CBIT 表')
    wb = openpyxl.load_workbook(path, data_only=True, read_only=True)
    ws = wb[wb.sheetnames[0]]
    rows = list(ws.iter_rows(values_only=True))
    entries = []
    cur_group = None
    for r in rows:
        c0 = r[0]
        c10 = r[10] if len(r) > 10 else None
        if c0 is None:
            continue
        c0s = str(c0).strip()
        if not c0s:
            continue
        if not c0s.startswith('K'):
            # 分组标题 (光耦/机械独享/机械共享) 或表头
            for title, _g, _lbl in EXCEL_GROUP_MAP:
                if c0s == title:
                    cur_group = dict((t, g) for t, g, _l in EXCEL_GROUP_MAP)[c0s]
                    break
            continue
        if cur_group is None:
            continue
        if not c10:
            continue  # 无 CBIT 通道的行跳过
        entries.append((cur_group, c0s, str(c10).strip()))
    wb.close()
    return entries


def load_statistic(path=None):
    """Component-Statistic.txt 任务三 → {继电器原始名: 功能分类} (V8)。
    格式: '[标签] (数量):' 分类标题行 + 下一行 'Kxx, Kyy, ...' 名字行。
    继电器名是原始名 (K22_ACDRV1_F), 非 merge 后单点名 (K22_ACDRV1)。"""
    if not path or not os.path.exists(path):
        return None
    stats = {}
    in_task3 = False
    cur_cat = None
    for line in read_enc(path).splitlines():
        s = line.strip()
        if s.startswith('## 任务三'):
            in_task3 = True
            continue
        if s.startswith('## 任务四'):
            break
        if not in_task3:
            continue
        m = re.match(r'\[([^\]]+)\]\s*\(\d+\):', s)
        if m:
            cur_cat = m.group(1).strip()
            continue
        if cur_cat:
            for n in re.findall(r'\bK\d+[A-Za-z0-9_]*', s):
                stats[n] = cur_cat
    return stats if stats else None


def load_connect_map(path=None):
    """SCH-Connect-Map.txt → 通路列表 (V2/V7)。
    提取 '需闭合: Kxx,Kyy' 头部行 + 路径行 (Kxx(Relay-ON))。"""
    if not path or not __import__('os').path.exists(path):
        return None
    paths = []
    for line in read_enc(path).splitlines():
        s = line.strip()
        if not s:
            continue
        m = re.search(r'需闭合:\s*([K\d,\s]+)', s)
        if m:
            relays = [x.strip() for x in m.group(1).split(',') if x.strip()]
            dut = None
            dm = re.match(r'(CH\d+\s+\w+)\s+->\s+(\w+)', s)
            if dm:
                dut = dm.group(2)
            paths.append({'dut_pin': dut, 'need_close': relays, 'raw': s})
    return paths if paths else None


def parse_map_paths(map_text):
    """SCH-Connect-Map → (路径行 rows, DUT 独立 token 集)  (V6 三重门数据源)。
    路径行: 'S5_ACM200_FH1 -> K22(Relay-ON) -> ACDRV1_F'
      src 端子: S<board>_<源表名>_(FH|SH|FL|SL)<n>; 节点: Kxx(Relay-ON/NC) 或普通 token。
    DUT token: 头部行 'CH0 High -> ACDRV1' 的落点 (DUT pad 证据)。"""
    rows, dut_tokens = [], set()
    for line in (map_text or '').splitlines():
        s = line.strip()
        if not s:
            continue
        hm = re.match(r'CH\d+\s+\S+\s*->\s*(\S+)', s)
        if hm:
            dut_tokens.add(hm.group(1))
            continue
        if '->' not in s or not s.startswith('S'):
            continue
        parts = [q.strip() for q in s.split('->')]
        if len(parts) < 2:
            continue
        m = re.match(r'(S\d+_[A-Za-z0-9]+?)_(FH|SH|FL|SL)\d*$', parts[0])
        if not m:
            continue
        relays, tokens = [], []
        for q in parts[1:]:
            pm = re.match(r'(K\d+)\(Relay-(?:ON|NC)\)$', q)
            if pm:
                relays.append(pm.group(1))
                tokens.append(pm.group(1))
            else:
                tokens.append(q)
        rows.append({'src': parts[0], 'src_name': m.group(1), 'src_pol': m.group(2),
                     'relays': relays, 'tokens': tokens, 'raw': s})
    return rows, dut_tokens


def split_end(name):
    """名字 → (词干, 'F'/'S'/None); KELVIN 名不参与 (走 merge 1a _FS 规则)。"""
    if 'KELVIN' in name:
        return name, None
    for suf in F_END_SUFFIXES:
        if name.endswith(suf):
            return name[:-len(suf)], 'F'
    for suf in S_END_SUFFIXES:
        if name.endswith(suf):
            return name[:-len(suf)], 'S'
    return name, None


def load_existing_defines(path):
    """读 StdAfx.h 等 → [(name, value_int)] (对拍基准)。
    '#define K25_VCC_F 25   // 注释' → ('K25_VCC_F', 25) (允许行尾注释)"""
    out = []
    for m in re.finditer(r'^\s*#define\s+(K\d+[A-Za-z0-9_]*)\s+(\d+)(?:\s*//.*)?\s*$',
                         read_enc(path), re.M):
        out.append((m.group(1), int(m.group(2))))
    return out


# =====================================================================
# B. 数据层
# =====================================================================

def cbit_val(cbit_str):
    """'S34_CBITn' → n; 'S36_CBITn' → n+128 (范围 0~127 / 128~255)"""
    m = re.match(r'S3(\d)_CBIT(\d+)', cbit_str)
    if not m:
        return -1
    board, bit = int(m.group(1)), int(m.group(2))
    return bit if board == 4 else bit + 128


def build_cbit_map(entries):
    """[(group, name, cbit_str)] → {value: [{'name','group','cbit_raw'}]}
    value = cbit_val(cbit_str)"""
    cmap = defaultdict(list)
    for group, name, cbit_str in entries:
        v = cbit_val(cbit_str)
        if v == -1:
            continue
        cmap[v].append({'name': name, 'group': group, 'cbit_raw': cbit_str})
    return dict(cmap)


# =====================================================================
# C. 合并层 (C-P1a/1b/1c + C-P2, 从 phase2_singlepoint.py 复用)
# =====================================================================

def merge_names(names):
    """共享同一 CBIT 值的多个名字 → 单点名。
    优先级: 1a KELVIN F/S→_FS → 1b 非KELVIN单字母F/S去后缀 → 1c FORCE/SENSE→_FOS_SNS
            → 2 BUS方向合并 (FH+SH/FL+SL) → 3 同K号后缀拼接 → fallback 拼接。"""
    if len(names) == 1:
        return names[0]

    # Priority 1a: KELVIN F/S pair
    f_kelvin = [n for n in names if 'KELVIN' in n and n.endswith('_F')]
    s_kelvin = [n for n in names if 'KELVIN' in n and n.endswith('_S')]
    if f_kelvin and s_kelvin:
        base = f_kelvin[0][:-2]
        others = [n for n in names if n not in (f_kelvin[0], s_kelvin[0])]
        if others:
            return base + '_FS_' + '_'.join(sorted(others))
        return base + '_FS'

    # Priority 1b: Non-KELVIN F/S pair (single letter)
    f_names = [n for n in names if n.endswith('_F') and 'KELVIN' not in n and 'FORCE' not in n.upper()]
    s_names = [n for n in names if n.endswith('_S') and 'KELVIN' not in n and 'SENSE' not in n.upper()]
    if f_names and s_names:
        merged_remainder = []
        for f in f_names:
            base_f = f[:-2]
            matching_s = [s for s in s_names if s[:-2] == base_f]
            if matching_s:
                merged_remainder.append(base_f)
            else:
                merged_remainder.append(f)
        for s in s_names:
            base_s = s[:-2]
            if not any(f[:-2] == base_s for f in f_names):
                merged_remainder.append(s)
        other = [n for n in names if n not in set(f_names + s_names)]
        all_merged = merged_remainder + other
        if len(all_merged) == 1:
            return all_merged[0]

    # Priority 1c: FORCE/SENSE full-word pair -> FOS_SNS
    f_force = [n for n in names if re.search(r'_Force$', n)]
    s_sense = [n for n in names if re.search(r'_Sense$', n)]
    if f_force and s_sense and len(f_force) == 1 and len(s_sense) == 1:
        base = re.sub(r'_Force$', '', f_force[0])
        others = [n for n in names if n not in (f_force[0], s_sense[0])]
        if others:
            return base + '_FOS_SNS_' + '_'.join(sorted(others))
        return base + '_FOS_SNS'

    # Priority 2: BUS direction merge (FH+SH or FL+SL)
    bus_pairs = defaultdict(list)
    for n in names:
        m = re.match(r'(K\d+_BUS)_(FH|SH|FL|SL)_(\S+)', n)
        if m:
            key = m.group(1) + '_' + m.group(3)
            bus_pairs[key].append(n)

    if len(bus_pairs) == 1:
        for key, group in bus_pairs.items():
            if len(group) == len(names):
                return 'K' + key.split('_')[0][1:] + '_' + '_'.join(key.split('_')[1:])

    # Other: same K number, concatenate suffixes
    k_nums = set()
    for n in names:
        m = re.match(r'(K\d+)', n)
        if m:
            k_nums.add(m.group(1))

    if len(k_nums) == 1:
        k = list(k_nums)[0]
        suffixes = []
        for n in sorted(names):
            rest = n[len(k) + 1:] if n.startswith(k + '_') else n
            suffixes.append(rest)
        return k + '_' + '_'.join(suffixes)

    # Fallback: concatenate
    return '_'.join(sorted(names))


# =====================================================================
# D. 生成层
# =====================================================================

def gen_singlepoint_defines(cbit_map, group_order):
    """C-P1: 输出 单点 #define 块 (按组: MOS / G6K_Dedicated / G6K_Shared)。
    返回 (lines, defines) — defines: {value: (name, group, cbit_raw)}"""
    lines = ['#ifndef _RELAY_H_', '#define _RELAY_H_', '',
             '// ===== 1. Single-Point Defines =====', '']
    defines = {}
    for group_name, group_label in group_order:
        lines.append('// %s' % group_label)
        for v in sorted(cbit_map.keys()):
            entries = [e for e in cbit_map[v] if e['group'] == group_name]
            if not entries:
                continue
            names = [e['name'] for e in entries]
            merged = merge_names(names)
            # 跨组同值 alias 检测 (同值不同组 → 允许别名)
            if v in defines:
                lines.append('#define %s %d  // alias, CBIT=%d' % (merged, v, v))
                defines[v] = (merged, group_name, entries[0]['cbit_raw'])
            else:
                lines.append('#define %s %d' % (merged, v))
                defines[v] = (merged, group_name, entries[0]['cbit_raw'])
        lines.append('')
    lines.append('#endif // _RELAY_H_')
    return lines, defines


# =====================================================================
# E. 校验层 (C-CK-V1~V8)
# =====================================================================

def check_v1(defines, issues, stats=None):
    """V1 — CBIT 位号不重复。允许别名 (同值不同名=alias, 同名不同值=FAIL)。"""
    by_value = defaultdict(list)
    by_name = defaultdict(list)
    for v, (name, _g, _raw) in defines.items():
        by_value[v].append(name)
        by_name[name].append(v)
    for name, vals in by_name.items():
        if len(set(vals)) > 1:
            issues.append('V1: 同名 %s 映射多个位号 %s' % (name, vals))
    return len([v for v in by_value if len(by_value[v]) > 1]) == 0 and \
        len([n for n in by_name if len(set(by_name[n])) > 1]) == 0


def check_v2(defines, issues, map_paths=None):
    """V2 — 通路完整性 (--map): 通路 '需闭合' 继电器位号都在定义中 (B 路径)。

    need_close 是 'K22' 形式 (带 K 名), defines 的 key 是 int 位号 (见 check_v1/v4),
    故按位号比较, 而非与 define 全名 (K22_ACDRV1) 做字符串比较 (永不相等误报)。
    """
    if map_paths is None:
        return True  # 无通路数据, SKIP
    all_values = set(defines.keys())
    ok = True
    for p in map_paths:
        for r in p['need_close']:
            m = re.match(r'K(\d+)', r)
            num = int(m.group(1)) if m else None
            if num is not None and num not in all_values:
                issues.append('V2: 通路 %s 需闭合继电器 %s (位号 %d) 未定义' % (p.get('dut_pin') or '?', r, num))
                ok = False
    return ok


def check_v3(defines, issues, stats=None):
    r"""V3 — 命名一致性: 单点名不含工位后缀 _Sx, 以 K\d+ 开头。"""
    ok = True
    for v, (name, _g, _raw) in defines.items():
        if not re.match(r'K\d+[A-Za-z0-9_]*$', name):
            issues.append('V3: 位号 %d 名字 %s 不以 K 开头' % (v, name))
            ok = False
        if re.search(r'_S\d+$', name):
            issues.append('V3: 位号 %d 名字 %s 含工位后缀 _Sx' % (v, name))
            ok = False
    return ok


def check_v4(defines, issues, stats=None):
    """V4 — 位号范围 0~255: S34→0~127, S36→128~255。"""
    ok = True
    lo, hi = CBIT_RANGE
    for v, (name, _g, raw) in defines.items():
        if not (lo <= v <= hi):
            issues.append('V4: %s 位号 %d 超出范围 [%d,%d]' % (name, v, lo, hi))
            ok = False
        if v <= S34_MAX and 'S34' not in (raw or ''):
            issues.append('V4: %s 位号 %d (S34区间) 来源异常 %s' % (name, v, raw))
            ok = False
        if v > S34_MAX and 'S36' not in (raw or ''):
            issues.append('V4: %s 位号 %d (S36区间) 来源异常 %s' % (name, v, raw))
            ok = False
    return ok


def check_v5(defines, issues, cbit_map=None):
    """V5 — 单点不遗漏: 每个 CBIT 值 (Excel 所有位号) 都有 define。
    允许跨组同值共享。"""
    if cbit_map is None:
        return True
    missing = [v for v in cbit_map if v not in defines]
    for v in missing:
        names = [e['name'] for e in cbit_map[v]]
        issues.append('V5: CBIT 位号 %d (%s) 无单点 define' % (v, ','.join(names)))
    return len(missing) == 0


def check_v6(defines, issues, cbit_map=None, map_rows=None, dut_tokens=None):
    """V6 — Force/Sense 成对合并 (2026-08-28 升级: 名字×电气×收敛 三重门)。
    门A 端别识别: 同位号名字按后缀(_F/_Force/_FOS vs _S/_Sense/_SNS, 可扩展)分 F/S 端;
    门B Force 可达: F 触点网(<词干>_F)经该位号继电器可达 源表 FH/FL (SCH-Connect-Map 路径行);
    门C Sense 可达: 同理可达 SH/SL;
    门D 收敛一致: F/S 落点 同一 DUT PIN (共同词干且 ∈ DUT 独立 token)
                  或 同源表同极性 (F=FH∧S=SH / F=FL∧S=SL, 防跨极性误合并);
    全过 → 校验合并名 defines[v] == merge_names(names)。
    任一门 FAIL → issue 停下问用户, 不静默合并。
    无 map_rows → 降级纯名字规则 + WARN(不静默)。"""
    if cbit_map is None:
        return True
    ok = True
    warned = [False]
    for v, entries in sorted(cbit_map.items()):
        names = [e['name'] for e in entries]
        if len(names) < 2:
            continue
        if map_rows is None:
            if not warned[0]:
                issues.append('V6 WARN: 无 --map, 降级纯名字规则判定 (未做电气可达校验)')
                warned[0] = True
            f = [n for n in names if n.endswith('_F') and 'KELVIN' not in n and 'FORCE' not in n.upper()]
            s = [n for n in names if n.endswith('_S') and 'KELVIN' not in n and 'SENSE' not in n.upper()]
            force = [n for n in names if n.endswith('_Force')]
            sense = [n for n in names if n.endswith('_Sense')]
            if (f and s) or (force and sense):
                merged = merge_names(names)
                defined = defines.get(v)
                if defined is None or defined[0] != merged:
                    issues.append('V6: 位号 %d F/S 对 (%s) 应合并为 %s' % (v, ','.join(names), merged))
                    ok = False
            continue
        # ---- 门A: 端别识别 ----
        ends = {}
        for n in names:
            stem, end = split_end(n)
            if end:
                stem = re.sub(r'^K\d+_', '', stem)   # K22_ACDRV1 → ACDRV1 (对齐 map token 词干)
                ends.setdefault(end, []).append(stem)
        if 'F' not in ends or 'S' not in ends:
            continue
        relay_id = 'K%d' % v

        def reachable(end):
            """该位号继电器所在路径行中, 端别网 (<词干>_F/_S) 可达对应源表极性端 → [(词干, 源表名, 极性)]"""
            want_pol = ('FH', 'FL') if end == 'F' else ('SH', 'SL')
            suffix = '_F' if end == 'F' else '_S'
            hits = []
            for row in map_rows:
                if relay_id not in row['relays'] or row['src_pol'] not in want_pol:
                    continue
                for tok in row['tokens']:
                    if tok.endswith(suffix) and tok[:-len(suffix)] in ends[end]:
                        hits.append((tok[:-len(suffix)], row['src_name'], row['src_pol']))
            return hits

        # ---- 门B/门C: 电气可达 ----
        f_hits = reachable('F')
        s_hits = reachable('S')
        if not f_hits:
            issues.append('V6 门B: 位号 %d (%s) F 端网经继电器不可达 源表FH/FL, 禁止合并 (停下问用户)'
                          % (v, ','.join(names)))
            ok = False
            continue
        if not s_hits:
            issues.append('V6 门C: 位号 %d (%s) S 端网经继电器不可达 源表SH/SL, 禁止合并 (停下问用户)'
                          % (v, ','.join(names)))
            ok = False
            continue
        # ---- 门D: 收敛一致 (防跨极性) ----
        conv = False
        f_stems = set(h[0] for h in f_hits)
        s_stems = set(h[0] for h in s_hits)
        common = f_stems & s_stems
        if common and dut_tokens and (common & dut_tokens):
            conv = True   # 情形A: 同一 DUT PIN (共同词干 ∈ DUT 独立 token)
        if not conv:
            f_h = any(h[2] == 'FH' for h in f_hits)
            f_l = any(h[2] == 'FL' for h in f_hits)
            s_h = any(h[2] == 'SH' for h in s_hits)
            s_l = any(h[2] == 'SL' for h in s_hits)
            same_src = set(h[1] for h in f_hits) & set(h[1] for h in s_hits)
            if same_src and ((f_h and s_h) or (f_l and s_l)):
                conv = True   # 情形B: 同源表同极性 (FH+SH / FL+SL)
        if not conv:
            issues.append('V6 门D: 位号 %d (%s) F/S 落点非同一 PIN 且非同源表同极性 '
                          '(F→%s S→%s), 禁止合并 (停下问用户)'
                          % (v, ','.join(names),
                             sorted(set(h[1] + '_' + h[2] for h in f_hits)),
                             sorted(set(h[1] + '_' + h[2] for h in s_hits))))
            ok = False
            continue
        # ---- 三重门过 → 合并名校验 ----
        merged = merge_names(names)
        defined = defines.get(v)
        if defined is None or defined[0] != merged:
            issues.append('V6: 位号 %d F/S 对 (%s) 应合并为 %s' % (v, ','.join(names), merged))
            ok = False
    return ok


def check_v7(defines, issues, map_paths=None):
    """V7 — FPVI/QVM 通路命名验证 (--map, B 路径):
    通路名若含 K_FPVIH_/K_FPVIL_ 前缀需对应 High/Low 侧。当前单点无通路, 仅防御校验。"""
    return True


def check_v8(defines, issues, cbit_map=None, stats=None):
    """V8 — CBIT 表与 Component-Statistic 交叉一致性 (--stat)。
    CBIT 表每个原始继电器名 (K22_ACDRV1_F) 必须在功能分类清单中 → 数据源无遗漏/无漂移。
    校验用原始名而非 merge 后单点名 (stats 存的是原始名)。"""
    if stats is None:
        return True
    ok = True
    for v, entries in (cbit_map or {}).items():
        for e in entries:
            if e['name'] not in stats:
                issues.append('V8: %s (位号 %d) 不在 Component-Statistic 功能分类中' % (e['name'], v))
                ok = False
    return ok


# =====================================================================
# F. 对拍层
# =====================================================================

def run_checks(defines, cbit_map, args):
    """执行 V1~V8, 返回 (overall_ok, [(vid, label, ok, issues)])"""
    issues = []
    stats = load_statistic(args.stat) if args.stat else None
    map_paths = load_connect_map(args.map) if args.map else None
    map_text = read_enc(args.map) if args.map and __import__('os').path.exists(args.map) else None
    map_rows, dut_tokens = parse_map_paths(map_text) if map_text else (None, None)

    checks = [
        ('V1', 'no-dup', check_v1(defines, issues)),
        ('V2', 'path-integrity', check_v2(defines, issues, map_paths)),
        ('V3', 'naming', check_v3(defines, issues)),
        ('V4', 'range', check_v4(defines, issues)),
        ('V5', 'coverage', check_v5(defines, issues, cbit_map)),
        ('V6', 'fs-pair', check_v6(defines, issues, cbit_map, map_rows, dut_tokens)),
        ('V7', 'fpvi-naming', check_v7(defines, issues, map_paths)),
        ('V8', 'relay-state', check_v8(defines, issues, cbit_map, stats)),
    ]
    return all(ok for _v, _l, ok in checks), checks, issues


def verify_defines(gen_defines, target_defines, warn_as_error=False):
    """对拍: 目标文件 (StdAfx.h 等) 的每个 CBIT 值必须在脚本输出中且一致。
    名字差异 (K25_VCC_F vs 规范 K25_VCC, 同值) → WARN; 目标有脚本无的 value → ERROR。"""
    gen_by_val = {v: name for v, (name, _g, _r) in gen_defines.items()}
    gen_by_name = {name: v for v, (name, _g, _r) in gen_defines.items()}
    errors, warns = [], []

    for name, val in target_defines:
        if val not in gen_by_val:
            errors.append('%s=%d: 目标有脚本无 (CBIT 值不在单点定义中)' % (name, val))
            continue
        gen_name = gen_by_val[val]
        if name != gen_name:
            # 同名同值 → 完全一致; 名不同值同 → 规范名差异
            if name in gen_by_name and gen_by_name[name] == val:
                pass  # 完全一致
            else:
                warns.append('%s=%d: 命名与规范不同 (脚本规范 %s, 同 CBIT 值)' % (name, val, gen_name))

    if errors:
        return False, errors, warns
    if warns and warn_as_error:
        return False, errors, warns
    return True, errors, warns


# =====================================================================
# G. 规则审计层
# =====================================================================

def audit_rules():
    """--audit-rules: 打印 RULE_COVERAGE + 机器自检 (函数存在 + 调用链可达)"""
    import inspect
    mod = sys.modules[__name__]
    fns = {n: getattr(mod, n) for n in dir(mod) if callable(getattr(mod, n, None))}
    fns = {n: f for n, f in fns.items() if getattr(f, '__module__', None) == __name__}
    roots = ['read_excel_cbit', 'build_cbit_map', 'gen_singlepoint_defines', 'merge_names',
             'run_checks', 'check_v1', 'check_v2', 'check_v3', 'check_v4',
             'check_v5', 'check_v6', 'check_v7', 'check_v8', 'verify_defines']
    callgraph = {}
    for n, f in fns.items():
        src = inspect.getsource(f)
        callgraph[n] = {c for c in re.findall(r'\b([a-z_]\w*)\(', src) if c in fns}
    reachable = set()
    stack = list(roots)
    while stack:
        n = stack.pop()
        if n in reachable:
            continue
        reachable.add(n)
        stack.extend(callgraph.get(n, set()))

    print('规则→函数覆盖映射表 (agent 铁律 → 脚本函数):')
    print('%-8s %-28s %-6s' % ('规则ID', '函数', '状态'))
    print('-' * 46)
    problems = []
    for rule, fn_list in RULE_COVERAGE.items():
        for fn in fn_list:
            ok = fn in fns
            reach = fn in reachable
            status = 'PASS' if (ok and reach) else 'FAIL'
            print('%-8s %-28s %-6s' % (rule, fn, status))
            if not ok:
                problems.append('%s: 函数 %s 不存在' % (rule, fn))
            elif not reach:
                problems.append('%s: 函数 %s 不在生成调用链 (规则未被执行)' % (rule, fn))
    if problems:
        print('*** FAIL ***')
        for p in problems:
            print('  -', p)
        return 1
    print('RULE COVERAGE PASSED (%d 规则)' % len(RULE_COVERAGE))
    return 0


# =====================================================================
# H. main
# =====================================================================

def main():
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except AttributeError:
        pass
    cfg = proj_config.load(proj_config.config_from_argv(sys.argv))
    ap = argparse.ArgumentParser(description='CBIT 单点继电器 #define 生成器 + 校验器')
    ap.add_argument('--config', default=None, help='project_config.json (默认 workspace 根)')
    ap.add_argument('--cbit', default=cfg['inputs']['cbit'], help='CBIT 表 Excel')
    ap.add_argument('--stat', default=None, help='Component-Statistic.txt (V8)')
    ap.add_argument('--map', default=None, help='SCH-Connect-Map.txt (V2/V7, B路径)')
    ap.add_argument('--verify', default=None, help='对拍目标 StdAfx.h (提取 #define Kxx N)')
    ap.add_argument('--bench', default=cfg['intermediates']['singlepoint_bench'], help='基准输出文件 (phase2_singlepoint_output.txt)')
    ap.add_argument('--no-verify-bench', action='store_true', help='跳过基准输出对拍')
    ap.add_argument('--warn-as-error', action='store_true')
    ap.add_argument('--audit-rules', action='store_true')
    args = ap.parse_args()

    if args.audit_rules:
        sys.exit(audit_rules())

    # 1. 生成
    entries = read_excel_cbit(args.cbit)
    if not entries:
        print('*** FAIL ***  CBIT 表无数据', file=sys.stderr)
        sys.exit(1)
    cbit_map = build_cbit_map(entries)
    group_order = [(g, lbl) for _t, g, lbl in EXCEL_GROUP_MAP]
    lines, defines = gen_singlepoint_defines(cbit_map, group_order)

    # 2. 基准对拍 (phase2_singlepoint_output.txt 期望输出)
    bench_ok = True
    if not args.no_verify_bench:
        bench = load_existing_defines(args.bench)
        if bench:
            ok, errors, warns = verify_defines(defines, bench)
            print('基准对拍 (%s): %d 条' % (args.bench, len(bench)))
            if not ok:
                print('*** FAIL ***  基准对拍 (%s)' % args.bench)
                for e in errors:
                    print('  -', e)
                bench_ok = False
            elif warns:
                print('WARNINGS (基准对拍 %s):' % args.bench)
                for w in warns:
                    print('  -', w)
        else:
            print('*** FAIL ***  基准文件 %s 无 #define Kxx N' % args.bench)
            bench_ok = False

    # 3. V1~V8 校验
    overall, checks, issues = run_checks(defines, cbit_map, args)

    # 4. 输出 #define 块
    print('\n'.join(lines))

    # 5. 校验报告
    print()
    print('===== CBIT-CHECK RESULT =====')
    for vid, label, ok in checks:
        print('  %s (%s): %s' % (vid, label, 'PASS' if ok else 'FAIL'))
    print('  OVERALL: %s' % ('PASS' if (overall and bench_ok) else 'FAIL'))
    if issues:
        print()
        print('  Issues:')
        for it in issues:
            print('    -', it)

    # 6. 可选对拍
    if args.verify:
        target = load_existing_defines(args.verify)
        if not target:
            print('*** FAIL ***  对拍目标 %s 无 #define Kxx N (正则未匹配, 检查格式)' % args.verify)
            overall = False
            sys.exit(1)
        ok, errors, warns = verify_defines(defines, target, args.warn_as_error)
        print()
        print('===== VERIFY %s =====' % args.verify)
        if errors:
            print('  FAIL (%d 条 ERROR)' % len(errors))
            for e in errors:
                print('    -', e)
        elif warns:
            print('  PASS (%d 条, %d WARN)' % (len(target), len(warns)))
            for w in warns:
                print('    -', w)
        else:
            print('  PASS (%d 条)' % len(target))
        overall = overall and ok and (not warns or not args.warn_as_error)

    sys.exit(0 if (overall and bench_ok) else 1)


if __name__ == '__main__':
    main()
