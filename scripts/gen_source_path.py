#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gen_source_path.py — 源表需求→能力→冲突 规划门（第一版）
===========================================================
目的: 写码前, 输入本 TM 的源表需求清单, 检测"需求组合是否超出本项目可用源表",
      重点抓 FPVIe 双重稀缺的结构性冲突:
        · FPVIe 是唯一大电流源 (≥200mA, ±1A/2A/10A)
        · FPVIe 又是唯一天然浮动差分源 (每通道独立全浮动, 单通道跨两点)
      两个属性挤在一块卡上(每工位仅 2 通道) → 需求同时点名时必然争用。

范围: 第一版只做 ①需求→源表类型映射(硬约束) ②类型→实例分配 ③冲突检测,
      输出"源表约束 + 冲突点 + 备选方案", 不生成链路 (生成留第二版)。
      继电器链重叠检测留第二版 (SCH-Connect-Map 列1-10)。

找通路三原则 (用户权威 2026-08-30, 每次找通路的第一原则):
  ① 精度第一(是"门"不是"筛"): 精度是 满足性 而非 择优性。
     重要工程经验 (2026-08-30 用户): DFT 没有特殊强调精度时,
     ACM200/FOVIe/FXVIe/FXVIe_PLUS/FPVIe 精度全部满足 → 精度不淘汰任何驱动源,
     决策落到 ②。
     只有 DFT 点名特殊精度 (DSL 加 '!' 前缀, 如 '!diff:BST-SW') 才收窄到精密源
     {FPVIe, ACM200}。能力硬约束(大电流/真差分/超量程)是另一层, 与精度门无关:
       · hc ≥200mA → 仅 FPVIe (ACM200 顶格 200mA 不满足量程≥2×)
       · 真差分两点 (pinA-pinB 都非地) → 需浮动源: FPVIe 单通道 / ACM200 跨单元
       · fv >40V / fi ≥200mA → 仅 FPVIe
  ② 最短通路: 精度门内选闭合/经过继电器最少 — 从 SCH-Connect-Map 列2/6/7 解析
     每条路径的 "需闭合:" 继电器数, 升序取最短; 最短被占 → 第二短兜底。
     实测 VBAT: FXVIe_PLUS ch5(K8 默认导通=0) < FPVIe CH1(K7=1) < FPVIe CH0(5);
     BST: ACM200 ch5(K48+K76=2) < FPVIe CH0(K46+K48+K76=3) < FPVIe CH1(4)
     ②' Pin2Pin 特殊规则 (用户 2026-08-30): 需求涉及 Pin2Pin 电压或电流时,
     若有可用 FPVIe 单通道浮动跨两点 (H→pinA + L→pinB), 算作最短通路,
     优先级高于 拆两个独立源表单端 (即使每端各自都是最短通路/0继电器)。
     即: 真差分语义 > 单端各自最短之和。TM641 方案B 即此例 (FPVI0 跨 BST-SW,
     不用 "两源各自驱动再软件扣偏置" 的 Option A 绕路)。
  ③ 并行效率: 非必要不串行执行, 多用不同源并行

用法 (--req 可重复, 逗号分隔参数):
  python gen_source_path.py --req "hc:0.2A,ACDRV1" --req "diff:BST-SW,2.5-4.0"
  python gen_source_path.py --req "diff:BST-SW" --req "fv:VCP_SW,3V"
  python gen_source_path.py --req "hc:0.5A,ACDRV1" --req "diff:BST-SW" --req "diff:PMID-PGND"
  python gen_source_path.py --demo            # 内置 4 场景自检

需求 DSL (前缀 '!' = DFT 特殊强调精度, 精度门收窄到精密源 {FPVIe,ACM200}):
  hc:  <currentA>,<pin>           大电流源 (≥200mA) → 必须 FPVIe
  diff:<pinA>-<pinB>[,<vmin>-<vmax>]  浮动差分/ramp 压差 → 真差分需浮动源 FPVIe/ACM200跨单元;
                                       单端对地(pinB=AGND) 默认全源过精度门→最短通路(如 VBAT→FXVIe_PLUS)
  fv:  <pin>,<V>                  精密绝对电压 → 默认最短通路; 电压>40V 才需 FPVIe
  fi:  <pin>,<A>                  精密绝对电流 → 默认最短通路; 电流>200mA 才需 FPVIe
  meas:<pin>[,<range>]            普通测量 → ACM200/QVMe
  smp: <pin>                      高速采样/FFT → QVMe
  tmu: <pin>                      时间测量 → QTMUe

例:  !diff:BST-SW,2.5-4.0  (DFT 点名精密差分管线)
     diff:VBAT-AGND,3-5    (BUBO 阈值斜坡, 未点名精度 → 最短通路 FXVIe_PLUS)
"""

import argparse
import os
import re
import sys
from functools import lru_cache
from pathlib import Path
from schematic_projection import read_schematic_text

import proj_config  # noqa: E402  (同目录共享 loader; config 在 workspace 根, 上溯解析)

_CFG = proj_config.load(proj_config.config_from_argv(sys.argv))

# ---------- 能力模型 (来源: knowledge/sources/hardware-specs.md + 工程实卡映射 2026-08-30) ----------

FPVIE_CHANNELS = 2          # FPVI0/FPVI1, 每通道独立全浮动 (SM8228)
ACM200_GROUPS = [           # 2 浮动单元 × 2 组 × 6ch, 组内共 SL (同组不能真差分)
    {'unit': 1, 'group': 1, 'chs': list(range(0, 6))},
    {'unit': 1, 'group': 2, 'chs': list(range(6, 12))},
    {'unit': 2, 'group': 1, 'chs': list(range(12, 18))},
    {'unit': 2, 'group': 2, 'chs': list(range(18, 24))},
]
SHARED_CARDS = ['QVMe (S7/S8)', 'QTMUe (S10/S23)']   # NOSITE 共享卡, 跨工位占用静态查不到

# 量程表 (±V / ±A), 用于能力检查与量程推荐 (量程 ≥ 2×设定值)
RANGES = {
    'FPVIe':      {'V': [1, 2, 5, 10, 20, 40, 100],
                   'I': [0.000010, 0.000100, 0.001, 0.01, 0.1, 1, 2, 10]},
    'ACM200':     {'V': [3.6, 10, 20, 40],
                   'I': [0.000001, 0.000010, 0.000100, 0.001, 0.01, 0.1, 0.2]},
    'FXVIe_PLUS': {'V': [3.6, 10, 20, 30, 40],
                   'I': [0.000001, 0.000010, 0.000100, 0.001, 0.01, 0.1, 1]},
    'QVMe':       {'V': [0.1, 1, 5, 10, 100], 'I': []},
}

# PIN → 可用驱动源表 (来源: SCH-Connect-Map 列1-10, 2026-08-30 实测)
#   · 列7 FXVIe_PLUS 8 实例: SW1_SW2(0) PMID_HG2(1) VCC_VMCU(2) AMUX_PGND(3)
#     NRST_PB5(4) VBAT_PD3(5) V1P5_VDRV(6) AMPOUT_U2PS(7) → 上电轨主力, 不占 FPVIe
#   · 列6 ACM200: BST(S5_ACM200_FH5) / SW(VCP_SW_ACM) / NQON_HG1 等
#   · 列2 FPVIe: VBAT(K7) / PMID(K83) / BST(K46+48+76) / SW(K60+K61)
#   · QTMUe/QVMe 只测不源, 列在末尾表示"可测量"非"可驱动"
PIN_SOURCES = {
    'VBAT':   ['FXVIe_PLUS', 'FPVIe', 'QTMUe', 'QVMe'],
    'PMID':   ['FXVIe_PLUS', 'FPVIe', 'QTMUe', 'QVMe'],
    'VDRV':   ['FXVIe_PLUS'],                 # 经 TP_VDRV 短接 V1P5 (列7 ch6)
    'V1P5':   ['FXVIe_PLUS'],
    'VCC':    ['FXVIe_PLUS', 'ACM200'],
    'SW1':    ['FXVIe_PLUS'],
    'SW2':    ['FXVIe_PLUS'],
    'HG2':    ['FXVIe_PLUS', 'ACM200'],
    'BST':    ['FPVIe', 'ACM200', 'QTMUe', 'QVMe'],
    'SW':     ['ACM200', 'FPVIe', 'QVMe'],
    'BST_SW': ['FPVIe', 'ACM200'],            # 差分对: BST-High / SW-Low
    # ACM200 专用实例 PIN (列6): VCP_SW(S5_8) / NQON_HG1(S5_9) / SW12_U1REF_BST(S5_5)
    'VCP_SW':   ['ACM200', 'FPVIe'],
    'NQON_HG1': ['ACM200', 'FPVIe'],
    'SW12_U1REF_BST': ['ACM200'],
    'VAC123':   ['ACM200'],
    'ACDRV1':   ['ACM200', 'FPVIe'],
    # 未收录 PIN → resolve_source_for_pin 返回 None, 调用处显式提示"未收录, 需写码复核"
}
# 三原则·精度门: 精密源 (DFT 点名特殊精度时收窄到这两个) vs 全驱动源
#   普通精度 (DFT 无特殊强调) → 精度全部满足, 不淘汰任何驱动源, 决策落最短通路
PRECISE_SOURCES = ['FPVIe', 'ACM200']
RAIL_SOURCES = ['FXVIe_PLUS', 'ACM200', 'FPVIe']   # 驱动源全集 (FOVIe=FXVIe_PLUS)

# ---------- SCH-Connect-Map 继电器通路解析 (三原则②最短通路) ----------
# 地图按 (源表, 通道, 端点) 逐条记录路径, 每条带 "需闭合:" 继电器清单 →
# 对每个 PIN 所有可达 (源,通道) 按继电器数升序 = 最短/第二短天然可得 (无需地图预存第二短字段)。

MAP_PATH = Path(_CFG['intermediates']['sch_connect_map'])
COL_SOURCE = {  # 地图列号 → 源表
    '1': 'FPVIe', '2': 'FPVIe', '3': 'QTMUe', '4': 'QVMe',
    '5': 'ACM', '6': 'ACM200', '7': 'FXVIe_PLUS', '8': 'QTMUe',
    '9': 'QVMe', '10': 'DCM',
}
NON_DRIVE_SOURCES = {'QTMUe', 'QVMe', 'ACM', 'DCM'}   # 只测不源 (或本板无卡)
# FPVIe 列2 组头: "CH0 High -> BST [Kelvin] 需闭合: K46,K48,K76"
FPVIE_HEADER_RE = re.compile(
    r'^CH(\d+)\s+(High|Low)\s*->\s*([A-Za-z0-9_]+)(.*)$')
# ACM200/FXVIe_PLUS 组头: "BST  [Kelvin]  需闭合: K48,K76" (通道取下一行 F: 实例)
PIN_HEADER_RE = re.compile(
    r'^([A-Za-z0-9_]+)\s+\[[^\]]*\]\s*需闭合:\s*(\S.*?)\s*$')
# F:/S: 子行 → 实例通道, 如 "F: S5_ACM200_FH5 -> ..." / "S: S3_FXVIe_PLUS_SH5 -> ..."
FS_TERM_RE = re.compile(r'^([FS]):\s+(\S+)')
# QTMUe/QVMe 单线: "S10_CH0_A -> K141(Relay-ON) -> ... -> BST"
SINGLE_TERM_RE = re.compile(r'^(\S+)\s*->')
# 通道在实例名: CH0 / FH5 / SH6 (FPVIe=CHx, ACM200/FXVIe_PLUS=FHx/SHx)
INST_CH_RE = re.compile(r'(?:CH|FH|SH)(\d+)')
# 地图节点名别名 (工程引脚名 ↔ 地图记录名; V1P5/VDRV 共享 V1P5_VDRV 节点经 TP_VDRV 短接)
PIN_ALIAS = {'V1P5': 'V1P5_VDRV', 'VDRV': 'V1P5_VDRV',
             'VCP_SW': 'VCP', 'NQON_HG1': 'nQON'}


def _relay_cost(relays_field):
    """'K46,K48,K76' → 3; '无(默认导通)' → 0"""
    if '无' in relays_field:
        return 0
    return len(re.findall(r'K\d+', relays_field))


def load_path_costs():
    """解析 SCH-Connect-Map.txt → PATH_COSTS
    PATH_COSTS[PIN][(source, channel, endpoint)] = {'cost': 需闭合数, 'relays': [..]}
    endpoint: 'H'(High/Force) | 'L'(Low/Sense) | None(单线/QTMUe/QVMe测量)
    """
    costs = {}
    if not MAP_PATH.exists():
        return costs
    col = None
    cur = None     # ACM200/FXVIe_PLUS 组头暂存 {pin, cost, relays}
    with open(MAP_PATH, encoding='utf-8') as f:
        for line in f:
            m = re.match(r'## 列(\d+):', line)
            if m:
                col, cur = m.group(1), None
                continue
            if col is None or col not in COL_SOURCE:
                continue
            src = COL_SOURCE[col]
            if src == 'ACM' and '无 ACM' in line:
                continue

            # --- 列2 FPVIe 组头 ---
            mh = FPVIE_HEADER_RE.match(line.strip())
            if mh:
                ch, ep, pin = mh.group(1), ('H' if mh.group(2) == 'High' else 'L'), mh.group(3)
                mr = re.search(r'需闭合:\s*(\S.*?)\s*$', mh.group(4))
                relays = re.findall(r'K\d+', mr.group(1)) if mr else []
                valid = '非有效' not in mh.group(4) and '⚠' not in mh.group(4)
                if valid:
                    costs.setdefault(pin.upper(), {})[(src, ch, ep)] = {
                        'cost': len(relays), 'relays': relays}
                continue

            # --- 列6/7 ACM200/FXVIe_PLUS 组头 (通道在下一行 F: 实例) ---
            mp = PIN_HEADER_RE.match(line.strip())
            if mp and not line.strip().startswith('CH'):
                cur = {'pin': mp.group(1).upper(), 'cost': _relay_cost(mp.group(2)),
                       'relays': re.findall(r'K\d+', mp.group(2))}
                continue

            # --- F:/S: 子行 (列6/7 归到 cur) ---
            ms = FS_TERM_RE.match(line.strip())
            if ms:
                ep = 'H' if ms.group(1) == 'F' else 'L'
                inst = ms.group(2)
                mch = INST_CH_RE.search(inst)
                ch = mch.group(1) if mch else '?'
                if cur is not None:
                    costs.setdefault(cur['pin'], {})[(src, ch, ep)] = {
                        'cost': cur['cost'], 'relays': cur['relays']}
                continue

            # --- 列3/4/8/9 QTMUe/QVMe 单线 (测量, 非驱动) ---
            ms2 = SINGLE_TERM_RE.match(line.strip())
            if ms2 and src in NON_DRIVE_SOURCES:
                inst = ms2.group(1)
                mch = INST_CH_RE.search(inst)
                ch = mch.group(1) if mch else '?'
                tail = re.findall(r'->\s*([A-Za-z0-9_]+)\s*$', line.strip())
                pin = tail[-1].upper() if tail else '?'
                cost = line.count('(Relay-ON)')
                costs.setdefault(pin, {})[(src, ch, None)] = {'cost': cost, 'relays': []}
    return costs


PATH_COSTS = load_path_costs()


@lru_cache(maxsize=None)
def ranked_paths(pin):
    """PIN 所有可达 (源,通道) 按需闭合继电器数升序 → 最短=首位, 第二短=次位。
    遍历范围 = 该 PIN 在 SCH-Connect-Map 列2/6/7 收录的行 (PATH_COSTS[pin]),
    不枚举全网表。lru 缓存: PATH_COSTS 建好只读, 同 PIN 重复调用不重排。"""
    pin = PIN_ALIAS.get(pin.upper(), pin.upper())
    if pin not in PATH_COSTS:
        return []
    items = [(src, ch, ep, v['cost'], v['relays'])
             for (src, ch, ep), v in PATH_COSTS[pin].items()]
    items.sort(key=lambda x: (x[3], x[0]))
    return items


def drive_paths(pin, srcs=None, exclude_fpvie=False, precise=False):
    """候选通路 (三原则筛选后的遍历范围):
      srcs 源表白名单(按 REQ_RULES 需求类型锁) / exclude_fpvie(单端对地) / precise(精度门收窄)。
    先按白名单只取该 PIN 对应源表的地图行, 再做能力过滤 — 不做"全网表枚举再筛"。
    返回 [(src, ch, ep, cost, relays), ...] 按继电器数升序 (最短=首位)。"""
    paths = ranked_paths(pin)
    cands = [p for p in paths
             if p[0] not in NON_DRIVE_SOURCES and (p[2] == 'H' or p[2] is None)]
    if srcs:
        cands = [p for p in cands if p[0] in srcs]
    if exclude_fpvie:
        cands = [p for p in cands if p[0] != 'FPVIe']
    if precise:
        cands = [p for p in cands if p[0] in PRECISE_SOURCES]
    return cands


def pick_drive(pin, need_precise=False, exclude_fpvie=False, srcs=None):
    """三原则: 精度门(默认全驱动源过/DFT点名精度→精密源) → 最短通路(继电器最少)。
    遍历范围 = drive_paths: 源表白名单 ∩ 精度门 ∩ 排除不可驱动, 最短=首位。
    返回 (source, channel, endpoint, cost, relays) 或 None (未收录 PIN, 需写码复核)。
    exclude_fpvie=True: 单端对地驱动排除 FPVIe (地图 CH0/CH1 Low→AGND 均标"非有效通路",
      即 FPVIe 不能正经单端对地, 只做差分/大电流)。srcs: 需求类型允许的源表白名单(REQ_RULES)。"""
    pin = pin.upper()
    if PATH_COSTS:
        cands = drive_paths(pin, srcs=srcs, exclude_fpvie=exclude_fpvie, precise=need_precise)
        if cands:
            return cands[0]   # 已按 cost 升序 → 最短通路
    # 兜底: 地图缺失/未收录 → 退回静态连接图 (旧行为, 无通路成本)
    avail = PIN_SOURCES.get(pin)
    if avail is None:
        return None
    order = PRECISE_SOURCES if need_precise else RAIL_SOURCES
    if srcs:
        order = [s for s in order if s in srcs] or list(srcs)
    for src in order:
        if src in avail and src not in NON_DRIVE_SOURCES and not (exclude_fpvie and src == 'FPVIe'):
            return (src, '按实例', 'H', None, [])
    return (avail[0], '按实例', 'H', None, [])


def second_path(pin, need_precise=False, exclude_fpvie=False, srcs=None):
    """同组候选里的第二短通路 (供备选报告)"""
    pin = pin.upper()
    if not PATH_COSTS:
        return None
    cands = drive_paths(pin, srcs=srcs, exclude_fpvie=exclude_fpvie, precise=need_precise)
    return cands[1] if len(cands) > 1 else None


def path_note(src, ch, cost, relays):
    """通路报告: 'FXVIe_PLUS ch5 (默认导通=0继电器)' 或兜底说明"""
    if cost is None:
        return f'{src} {ch} (地图无通路数据, 连接图兜底)'
    rel = ','.join(relays) if relays else '默认导通'
    return f'{src} ch{ch} ({rel}={cost}继电器)'


def second_note(second):
    """第二短通路报告; second=(src,ch,ep,cost,relays)"""
    if not second:
        return ''
    return '; 第二短 ' + path_note(second[0], second[1], second[3], second[4])


# ---------- v2: 跨需求继电器重叠检测 (三原则③并行效率) ----------

def req_pins(r):
    """需求的受测 PIN 集 (用于重叠分类: 共享继电器是否落在同一节点)"""
    if r['type'] == 'diff':
        single_end = r['pinB'].upper() in ('AGND', 'GND', 'AGND_F', 'DGND', 'PGND', 'AGNDS')
        return {r['pinA']} if single_end else {r['pinA'], r['pinB']}
    if r['type'] == 'fi' and r.get('pinB'):
        return {r['pin'], r['pinB']}
    return {r['pin']}


def relays_for_assignment(r, src, ch):
    """从 PATH_COSTS 反查某需求所选 (src,ch) 的需闭合继电器集 (重叠检测用);
    遍历范围 = drive_paths 白名单 (按需求类型允许的源表), 不扫无关源表行。
    地图缺失/兜底 → 空集 (无继电器数据不参与检测)。"""
    if r['type'] == 'diff':
        single_end = r['pinB'].upper() in ('AGND', 'GND', 'AGND_F', 'DGND', 'PGND', 'AGNDS')
        if not single_end:
            for o in diff_paths(r['pinA'], r['pinB']):
                if o[0] == src and o[1] == ch:
                    return set(o[3])
            return set()
        # 单端对地 diff: 同 pick_drive 单端逻辑 (pinA 为驱动端)
        for p in drive_paths(r['pinA'], srcs=[src]):
            if p[0] == src and p[2] == 'H':
                return set(p[4])
        return set()
    if r['type'] == 'fi' and r.get('pinB'):
        for o in diff_paths(r['pin'], r['pinB']):
            if o[0] == src and o[1] == ch:
                return set(o[3])
        return set()
    if r['type'] == 'hc':
        for p in drive_paths(r['pin'], srcs=['FPVIe']):   # hc 走 FPVIe, 只枚举 FPVIe 行
            if p[0] == 'FPVIe' and p[2] == 'H':
                return set(p[4])
        return set()
    for p in drive_paths(r['pin'], srcs=[src]):
        if p[0] == src and p[2] == 'H':
            return set(p[4])
    return set()


def detect_relay_overlaps(assignments, relay_sets=None):
    """跨需求继电器重叠检测 (v2):
      · 同一继电器被 ≥2 个需求需闭合 → 找出;
      · 共享落在同一节点 (两需求 pin 集相交) → 良性共用 (TM641 先例: FPVI0 Low 与 ACM200 共用 K61 到 SW);
      · 共享落在不同节点 → 继电器冲突 (会短接两路或需串行), 建议第二短通路避让。
    relay_sets: 可预传每需求的继电器集 (avoid_relay_conflicts 增量更新), 不传则现算。
    返回 (overlaps, conflicts): overlaps=信息, conflicts=需裁决。"""
    if relay_sets is None:
        relay_sets = [relays_for_assignment(r, src, ch)
                      for (r, src, ch, _note, _spec) in assignments]
    relay_use = {}      # K -> [(idx, pins)]
    for i, ((r, src, ch, _note, _spec), rset) in enumerate(zip(assignments, relay_sets)):
        pins = req_pins(r)
        for k in rset:
            relay_use.setdefault(k, []).append((i, pins))

    overlaps, conflicts = [], []
    for k, users in sorted(relay_use.items()):
        if len(users) < 2:
            continue
        # 所有用户 pin 集两两是否共节点 (至少一对相交 → 该继电器至少有一次良性共用)
        shared_node = any(users[a][1] & users[b][1]
                          for a in range(len(users)) for b in range(a + 1, len(users)))
        label = ', '.join(f'需求{idx + 1}({"/".join(sorted(p))})' for idx, p in users)
        if shared_node:
            overlaps.append(f'{k}: 共用节点 {" / ".join(sorted(pins))} → 良性共用, 可并行'
                            f' (参与: {label})')
        else:
            conflicts.append(
                f'{k}: 被 {label} 需闭合但落不同节点 → 继电器冲突'
                f' (短接两路或需串行; 建议任一需求换第二短通路避让)')
    return overlaps, conflicts


@lru_cache(maxsize=None)
def diff_paths(pinA, pinB):
    """真差分两点: 按同源同通道拼 H→pinA + L→pinB (FPVIe 单通道浮动),
    或 ACM200 跨单元双通道 (单元1 ch0-11 / 单元2 ch12-23, 各自独立 Low)。
    遍历范围 = 只枚举 FPVIe/ACM200 两源表的行 (真差分能力白名单), 不扫其他源表。
    返回 [(source, ch, cost, relays_union, note), ...] 升序。lru 缓存同 (pinA,pinB)。"""
    pinA, pinB = pinA.upper(), pinB.upper()
    res = []
    for (src, ch, ep), v in PATH_COSTS.get(pinA, {}).items():
        if src not in ('FPVIe', 'ACM200'):
            continue
        if ep == 'H':
            vB = PATH_COSTS.get(pinB, {}).get((src, ch, 'L'))
            if vB is not None:
                relays = list(dict.fromkeys(v['relays'] + vB['relays']))
                cost = len(relays)      # 需闭合继电器数 = 两路径继电器并集 (cbite.SetOn 一次闭合)
                res.append((src, ch, cost, relays, 'FPVIe 单通道浮动'))
        if src == 'ACM200' and ep == 'H':
            # 跨单元双通道: pinB 取另一单元任一通道的 H 端点
            for (s2, ch2, ep2), v2 in PATH_COSTS.get(pinB, {}).items():
                if s2 == 'ACM200' and ep2 == 'H':
                    same_unit = (int(ch) < 12) == (int(ch2) < 12)
                    if not same_unit:
                        relays = list(dict.fromkeys(v['relays'] + v2['relays']))
                        cost = len(relays)
                        res.append((src, f'{ch}+{ch2}', cost, relays, 'ACM200 跨单元双通道'))
    res.sort(key=lambda x: x[2])
    return res


def alternative_path_for(r, src, ch):
    """对需求 r 当前所选 (src,ch), 返回下一可选通路 (src2,ch2,cost2,relays2) 或 None。
    diff/fi Pin2Pin → diff_paths 里除当前的下一项; hc → FPVIe 通道; 单端 → ranked_paths 下一项。
    用于 v2.1 继电器冲突自动避让 (借第二通路可满足 → 不裁决)。"""
    if r['type'] == 'diff':
        single_end = r['pinB'].upper() in ('AGND', 'GND', 'AGND_F', 'DGND', 'PGND', 'AGNDS')
        if not single_end:
            for o in diff_paths(r['pinA'], r['pinB']):
                if not (o[0] == src and o[1] == ch):
                    return o[:4]            # (src, ch, cost, relays)
            return None
        pin = r['pinA']                     # 单端对地 diff 等同单端驱动
    elif r['type'] == 'fi' and r.get('pinB'):
        for o in diff_paths(r['pin'], r['pinB']):
            if not (o[0] == src and o[1] == ch):
                return o[:4]
        return None
    else:
        pin = r['pin']
    if r['type'] == 'hc':
        cands = drive_paths(pin, srcs=['FPVIe'])
    else:
        cands = drive_paths(pin, precise=r.get('precise'))
    for p in cands:
        if not (p[0] == src and p[1] == ch):
            return (p[0], p[1], p[3], p[4]) # 统一 4 元组 (src, ch, cost, relays)
    return None


def avoid_relay_conflicts(assignments):
    """v2.1 继电器冲突自动避让 (用户原则: 借第二通路可满足 → 不裁决)。
    对每个冲突继电器, 给涉及的某个需求换第二短通路 (relays 不含该 K 才换);
    换后重查。返回 (new_assignments, avoided_msgs, residual_conflicts)。
    residual = 第二短也撞同一继电器 (电路结构决定) → 需串行, 不阻塞但提示。
    遍历优化: 预计算每需求继电器集, 仅被换路的那条增量重算, 不每轮全扫。"""
    assignments = list(assignments)
    avoided = []
    relay_sets = [set(relays_for_assignment(r, s, c))
                  for (r, s, c, _n, _sp) in assignments]
    for _ in range(len(assignments) + 2):       # 防死循环上限
        _, rc = detect_relay_overlaps(assignments, relay_sets)
        if not rc:
            break
        progressed = False
        for k in rc:
            kname = k.split(':', 1)[0]          # 冲突消息首 token = 继电器名 (如 K46)
            users = [(i, r, s, c)
                     for i, (r, s, c, _n, _sp) in enumerate(assignments)
                     if kname in relay_sets[i]]
            for i, r, s, c in users:
                alt = alternative_path_for(r, s, c)
                if not alt or kname in set(alt[3]):
                    continue                    # 无第二短 / 第二短也撞该继电器
                if alt[0] == 'FPVIe':           # 防 FPVIe 通道撞车: 目标通道不得已被其他需求占用
                    used = {ch for (_rr, _ss, ch, _nn, _pp) in assignments
                            if _ss == 'FPVIe' and ch != '—'}
                    used.discard(c)             # 自身当前通道不算占用
                    if alt[1] in used:
                        continue
                new_src, new_ch, cost, relays = alt
                assignments[i] = (r, new_src, new_ch,
                                  f'避让 {kname}: {s} {c} → {new_src} {new_ch} '
                                  f'({",".join(relays) if relays else "默认导通"}={cost}继电器)',
                                  assignments[i][4])
                relay_sets[i] = set(relays_for_assignment(r, new_src, new_ch))  # 只更新被换这条
                avoided.append(f'{fmt_req(r)}: {kname} 被占且落不同节点 → '
                               f'自动换第二短 {new_src} {new_ch} ({cost}继电器)')
                progressed = True
                break
            if progressed:
                break
        if not progressed:
            break                               # 全部冲突均无法避让 (第二短也撞)
    _, residual = detect_relay_overlaps(assignments, relay_sets)
    return assignments, avoided, residual


def resolve_source_for_pin(pin, need_precise=False, prefer=None):
    """兼容入口: pick_drive 的最短通路版 (精度门 + 继电器最少)。
    prefer 仅作并列 tiebreaker, 不再决定选择顺序。"""
    hit = pick_drive(pin, need_precise=need_precise)
    if hit is None:
        return None
    return hit[0]


# 需求类型 → 候选源表(顺序=首选) + FPVIe 通道成本 + 约束理由
REQ_RULES = {
    'hc':   {'sources': ['FPVIe'],
             'fpvie': 1,
             'why': '本项目唯一大电流源 (ACM200 顶格 200mA 不满足量程≥2×规则)'},
    'diff': {'sources': ['FPVIe', 'ACM200'],
             'fpvie': 1,
             'why': 'FPVIe 单通道独立浮动可跨两点差分; ACM200 备选需跨单元(组内共 SL 不能真差分)'},
    'fv':   {'sources': ['ACM200', 'FPVIe', 'FXVIe_PLUS'],
             'fpvie': 0,
             'why': '主力精密源 ACM200; 电压 >40V 才需 FPVIe(±100V)'},
    'fi':   {'sources': ['ACM200', 'FPVIe'],
             'fpvie': 0,
             'why': '主力精密源 ACM200; 电流 >200mA 需 FPVIe'},
    'meas': {'sources': ['ACM200', 'QVMe'],
             'fpvie': 0,
             'why': '普通测量 ACM200 或 QVMe 差分表'},
    'smp':  {'sources': ['QVMe'],
             'fpvie': 0,
             'why': '高速采样/FFT 仅 QVMe'},
    'tmu':  {'sources': ['QTMUe'],
             'fpvie': 0,
             'why': '时间测量仅 QTMUe'},
}


# ---------- 解析 ----------

def parse_ampere(s):
    """'0.2A'/'200mA'/'10uA'/'10µA' → 安培浮点"""
    m = re.match(r'([\d.]+)\s*([uµm]?)A?', s.strip())
    if not m:
        raise ValueError(f'电流格式错误: {s}')
    v = float(m.group(1))
    unit = m.group(2)
    if unit in ('u', 'µ'):
        v *= 1e-6
    elif unit == 'm':
        v *= 1e-3
    return v


def fmt_ampere(v):
    """安培浮点 → 友好显示 (µA/mA/A)"""
    if v >= 1:
        return f'{v:g}A'
    if v >= 1e-3:
        return f'{v * 1e3:g}mA'
    if v >= 1e-6:
        return f'{v * 1e6:g}µA'
    return f'{v:g}A'


def parse_volt(s):
    """'3V'/'2.5' → 伏特浮点"""
    m = re.match(r'([\d.]+)\s*V?', s.strip())
    if not m:
        raise ValueError(f'电压格式错误: {s}')
    return float(m.group(1))


def parse_req(s):
    s = s.strip()
    precise = s.startswith('!')          # '!' = DFT 特殊强调精度 → 精度门收窄精密源
    if precise:
        s = s[1:]
    typ, _, arg = s.partition(':')
    typ = typ.strip().lower()
    parts = [p.strip() for p in arg.split(',')]
    if typ == 'hc':
        return {'type': 'hc', 'cur': parse_ampere(parts[0]),
                'pin': parts[1] if len(parts) > 1 else '?', 'precise': precise}
    if typ == 'diff':
        p = parts[0].split('-')
        pinA, pinB = p[0], p[1] if len(p) > 1 else '?'
        vrng = parts[1] if len(parts) > 1 and '-' in parts[1] else None
        return {'type': 'diff', 'pinA': pinA, 'pinB': pinB, 'vrng': vrng, 'precise': precise}
    if typ in ('fv', 'fi', 'pw'):
        val = None
        if len(parts) > 1:
            val = parse_volt(parts[1]) if typ in ('fv', 'pw') else parse_ampere(parts[1])
        # fi:pinA-pinB,<A> → Pin2Pin 电流 (需浮动源 FPVIe/ACM200 跨单元)
        pinB = None
        if typ == 'fi' and '-' in parts[0]:
            a, _, b = parts[0].partition('-')
            parts[0], pinB = a.strip(), b.strip()
        return {'type': typ, 'pin': parts[0], 'pinB': pinB, 'val': val, 'precise': precise}
    if typ in ('meas', 'smp', 'tmu'):
        return {'type': typ, 'pin': parts[0], 'precise': precise}
    raise ValueError(f'未知需求类型: {typ} (可用 !hc/diff/fv/fi/pw/meas/smp/tmu, ! 前缀=DFT点名精度)')


# ---------- 量程推荐 (量程 ≥ 2×设定值, 选最接近一档) ----------

def recommend_range(src, kind, val):
    if val is None or src not in RANGES or not RANGES[src].get(kind):
        return None
    target = 2 * abs(val)
    for r in RANGES[src][kind]:
        if r >= target:
            return r
    return None     # 超量程 → 无档


# ---------- 核心: 分配 + 冲突检测 ----------

def analyze(reqs):
    # 排序: hc(硬约束) 先占 FPVIe, 再 diff, 再 fv/fi 超限
    order = sorted(reqs, key=lambda r: {
        'hc': 0, 'diff': 1, 'fv': 2, 'fi': 2, 'pw': 2, 'meas': 3, 'smp': 4, 'tmu': 4
    }[r['type']])

    assignments = []
    fpvie_used = 0
    fpvie_chans = set()     # 已占用的 FPVIe 逻辑通道索引 {0,1} (FPVI0=CH0, FPVI1=CH1)
    conflicts = []          # 硬冲突 (阻塞生成)
    downgrades = []         # 软降级 (有备选, 需人工确认)
    tips = []               # 提示

    def assign_p2p(pinA, pinB, kind, spec, tag):
        """②' Pin2Pin 特殊规则 (diff 电压 / fi 电流 共享):
        有可用 FPVIe 单通道浮动跨两点 → 算最短通路, 优先级高于拆两独立源表单端;
        满 → ACM200 跨单元备选; 无浮动通路 → 冲突。"""
        nonlocal fpvie_used
        opts = diff_paths(pinA, pinB)
        fpvie_opts = [o for o in opts if o[0] == 'FPVIe']
        free_opts = [o for o in fpvie_opts if int(o[1]) not in fpvie_chans]
        if free_opts and fpvie_used < FPVIE_CHANNELS:
            src, ch, cost, relays, how = free_opts[0]   # 最短空闲 FPVIe 通道
            idx = int(ch)
            fpvie_used += 1
            fpvie_chans.add(idx)
            second = next((o for o in opts
                           if not (o[0] == src and o[1] == ch)
                           and (o[0] != 'FPVIe' or int(o[1]) not in fpvie_chans)), None)
            note = (f'Pin2Pin {kind} (②\'规则: FPVIe 单通道浮动=最短) {how} '
                    + path_note(src, ch, cost, relays)
                    + (f'; 第二短 {second[0]} {second[1]} ({second[2]}继电器)'
                       if second else ''))
            assignments.append((r, src, ch, note, spec))
            return
        # FPVIe 不可用 → 自动降级 (用户原则: 借第二通路/拆两独立源表 可满足 → 不裁决)
        acm = [o for o in opts if o[0] == 'ACM200']
        if acm:
            src, ch, cost, relays, how = acm[0]
            downgrades.append(f'{tag}: FPVIe 满 → 自动 ACM200 跨单元双通道 {ch} ({cost}继电器)')
            assignments.append((r, src, ch,
                                f'{kind} 自动降级 {how} ' + path_note(src, ch, cost, relays), spec))
            return
        hA = pick_drive(pinA, need_precise=r.get('precise'))
        hB = pick_drive(pinB, need_precise=r.get('precise'))
        if hA and hB:
            downgrades.append(
                f'{tag}: FPVIe 满且无 ACM 跨单元 → 自动拆两独立源表单端 '
                f'(A→{hA[0]} {hA[1]}, B→{hB[0]} {hB[1]}; 非浮动, 需软件差分/扣偏置)')
            assignments.append((r, f'{hA[0]}+{hB[0]}', '拆源表',
                                f'{kind} 自动拆两独立源表单端驱动 (非浮动, 需软件差分)', spec))
            return
        conflicts.append(
            f'{tag}: 无浮动 Pin2Pin 通路且 {pinA if not hA else pinB} 无任何驱动源 → 本电路缺失')
        assignments.append((r, '—', '—', '无通路!', spec))

    for r in order:
        t = r['type']
        if t == 'hc':
            if fpvie_used < FPVIE_CHANNELS:
                idx = fpvie_used
                ch = f'FPVI{idx}'
                fpvie_used += 1
                fpvie_chans.add(idx)
                assignments.append((r, 'FPVIe', ch, '硬约束: 唯一大电流源', None))
            else:
                tips.append(
                    f'hc({r["cur"]}A@{r["pin"]}): FPVIe {FPVIE_CHANNELS}通道已满, 大电流无法并行 '
                    f'→ 需串行分时(同一通道复用)或删减需求')
                assignments.append((r, 'FPVIe', '—', '需串行(通道复用)', None))

        elif t == 'diff':
            single_end = r['pinB'].upper() in ('AGND', 'GND', 'AGND_F', 'DGND', 'PGND', 'AGNDS')
            if single_end:
                # 单端斜坡对地 (如 VBAT-AGND): 精度门(默认全驱动源过, 除非 '!') → 最短通路
                #   排除 FPVIe: 地图 CH0/CH1 Low→AGND 标"非有效通路", FPVIe 不做单端对地
                hit = pick_drive(r['pinA'], need_precise=r['precise'], exclude_fpvie=True)
                if hit is None:
                    assignments.append((r, 'FXVIe_PLUS', '按实例',
                                       f'单端斜坡, {r["pinA"]} 无可用驱动源(地图未收录/精密源不可用), 写码复核', r['vrng']))
                else:
                    src, ch, _, cost, relays = hit
                    if src == 'FPVIe':      # exclude_fpvie 后不应出现, 防御
                        fpvie_used += 1
                    second = second_path(r['pinA'], r['precise'], exclude_fpvie=True)
                    note = '单端斜坡 ' + path_note(src, ch, cost, relays) + second_note(second)
                    assignments.append((r, src, ch, note, r['vrng']))
            else:
                # Pin2Pin 电压: ②' 特殊规则 — FPVIe 单通道浮动跨两点=最短, 优先于两独立源表单端
                assign_p2p(r['pinA'], r['pinB'], '电压', r['vrng'],
                           f'diff({r["pinA"]}-{r["pinB"]})')

        elif t in ('fv', 'pw'):
            hit = pick_drive(r['pin'], need_precise=r['precise'])
            need_fpvie = r['val'] is not None and abs(r['val']) > 40   # >40V 能力硬约束
            if hit is None:
                assignments.append((r, 'FXVIe_PLUS', '按实例',
                                   f'{t} {r["pin"]} 未收录连接图, 默认 FXVIe_PLUS 写码复核', r['val']))
            elif need_fpvie:
                if fpvie_used < FPVIE_CHANNELS:
                    idx = fpvie_used
                    ch = f'FPVI{idx}'
                    fpvie_used += 1
                    fpvie_chans.add(idx)
                    assignments.append((r, 'FPVIe', ch,
                                       f'电压 {r["val"]}V > 40V 需 FPVIe ±100V', r['val']))
                else:
                    tips.append(f'fv({r["pin"]},{r["val"]}V): >40V 需 FPVIe 但通道已满 '
                                f'→ 需串行(等 FPVIe 释放后分时)')
                    assignments.append((r, 'FPVIe', '—', '需串行(FPVIe 满)', r['val']))
            else:
                src, ch, _, cost, relays = hit
                second = second_path(r['pin'], r['precise'])
                note = t + ' ' + path_note(src, ch, cost, relays) + second_note(second)
                if src == 'FPVIe':
                    if fpvie_used >= FPVIE_CHANNELS:
                        alt = pick_drive(r['pin'], need_precise=r['precise'], exclude_fpvie=True)
                        if alt:
                            src, ch, _, cost, relays = alt
                            downgrades.append(
                                f'{t}({r["pin"]}): 最短 FPVIe 被占 → 自动换非 FPVIe 最短 '
                                f'{src} {ch} ({cost}继电器)')
                            note = t + ' 自动避让FPVIe ' + path_note(src, ch, cost, relays)
                        else:
                            tips.append(f'{t}({r["pin"]}): 最短 FPVIe 被占且无其他驱动源 → 需串行')
                            assignments.append((r, 'FPVIe', '—', '需串行(FPVIe 满)', r['val']))
                            continue
                    idx = fpvie_used
                    fpvie_used += 1
                    fpvie_chans.add(idx)
                    ch = f'FPVI{idx}'
                assignments.append((r, src, ch, note, r['val']))

        elif t == 'fi':
            if r.get('pinB'):
                # Pin2Pin 电流: ②' 特殊规则 — FPVIe 单通道浮动 H→pinA + L→pinB 算最短
                assign_p2p(r['pin'], r['pinB'], '电流', r['val'],
                           f'fi({r["pin"]}-{r["pinB"]})')
                continue
            hit = pick_drive(r['pin'], need_precise=r['precise'])
            need_fpvie = r['val'] is not None and abs(r['val']) >= 0.2  # ≥200mA 能力硬约束
            if hit is None:
                assignments.append((r, 'FXVIe_PLUS', '按实例',
                                   f'fi {r["pin"]} 未收录连接图, 默认 FXVIe_PLUS 写码复核', r['val']))
            elif need_fpvie:
                if fpvie_used < FPVIE_CHANNELS:
                    idx = fpvie_used
                    ch = f'FPVI{idx}'
                    fpvie_used += 1
                    fpvie_chans.add(idx)
                    assignments.append((r, 'FPVIe', ch,
                                       f'电流 {fmt_ampere(r["val"])} ≥200mA 需 FPVIe', r['val']))
                else:
                    tips.append(f'fi({r["pin"]},{fmt_ampere(r["val"])}): ≥200mA 需 FPVIe 但通道已满 '
                                f'→ 需串行(等 FPVIe 释放后分时)')
                    assignments.append((r, 'FPVIe', '—', '需串行(FPVIe 满)', r['val']))
            else:
                src, ch, _, cost, relays = hit
                second = second_path(r['pin'], r['precise'])
                note = 'fi ' + path_note(src, ch, cost, relays) + second_note(second)
                if src == 'FPVIe':
                    if fpvie_used >= FPVIE_CHANNELS:
                        alt = pick_drive(r['pin'], need_precise=r['precise'], exclude_fpvie=True)
                        if alt:
                            src, ch, _, cost, relays = alt
                            downgrades.append(
                                f'fi({r["pin"]}): 最短 FPVIe 被占 → 自动换非 FPVIe 最短 '
                                f'{src} {ch} ({cost}继电器)')
                            note = 'fi 自动避让FPVIe ' + path_note(src, ch, cost, relays)
                        else:
                            tips.append(f'fi({r["pin"]}): 最短 FPVIe 被占且无其他驱动源 → 需串行')
                            assignments.append((r, 'FPVIe', '—', '需串行(FPVIe 满)', r['val']))
                            continue
                    idx = fpvie_used
                    fpvie_used += 1
                    fpvie_chans.add(idx)
                    ch = f'FPVI{idx}'
                assignments.append((r, src, ch, note, r['val']))

        elif t == 'meas':
            assignments.append((r, 'ACM200', '按实例', '普通测量', None))

        elif t == 'smp':
            assignments.append((r, 'QVMe', '按实例', '高速采样/FFT', None))
            tips.append('QVMe 是共享卡(S7/S8, 4通道), 机台实时占用无法静态查 — 上机前确认空闲')

        elif t == 'tmu':
            assignments.append((r, 'QTMUe', '按实例', '时间测量', None))
            tips.append('QTMUe 是共享卡(S10/S23, 4单元), 机台实时占用无法静态查 — 上机前确认空闲')

    # --- FPVIe 总账冲突 (用户点名的核心场景) ---
    if fpvie_used > FPVIE_CHANNELS:
        conflicts.append(
            f'FPVIe 双重稀缺: 大电流+浮动差分都锁定 FPVIe(唯一大电流源+唯一天然浮动差分源), '
            f'通道需求 {fpvie_used} > 可用 {FPVIE_CHANNELS}')

    # --- 能力越界检查 (无源可满足) ---
    for r in order:
        if r['type'] == 'hc' and r['cur'] > 10:
            conflicts.append(f'hc({r["cur"]}A): 超过 FPVIe 最大 10A, 本工程无源可满足')
        if r['type'] == 'fv' and r['val'] is not None and abs(r['val']) > 100:
            conflicts.append(f'fv({r["val"]}V): 超过 FPVIe 最大 ±100V, 本工程无源可满足')

    return assignments, conflicts, downgrades, tips, fpvie_used


# ---------- 报告输出 ----------

def fmt_req(r):
    t = r['type']
    if t == 'hc':
        return f'hc {fmt_ampere(r["cur"])} @ {r["pin"]}'
    if t == 'diff':
        s = f'diff {r["pinA"]}-{r["pinB"]}'
        return s + (f' ({r["vrng"]})' if r['vrng'] else '')
    if t == 'fv':
        return f'fv {r["pin"]}' + (f' = {r["val"]:g}V' if r['val'] is not None else '')
    if t == 'fi':
        s = f'fi {r["pin"]}' + (f'-{r["pinB"]}' if r.get('pinB') else '')
        return s + (f' = {fmt_ampere(r["val"])}' if r['val'] is not None else '')
    return f'{t} {r["pin"]}'


def render(reqs):
    assignments, conflicts, downgrades, tips, fpvie_used = analyze(reqs)
    # v2.1: 继电器冲突自动避让 (用户原则: 借第二短可满足 → 不裁决) — 先避让再出清单
    assignments, avoided, residual_rc = avoid_relay_conflicts(assignments)
    overlaps, _ = detect_relay_overlaps(assignments)
    # 重算 FPVIe 预算 (避让/降级可能换源)
    fpvie_used = len({ch for (_r, _s, ch, _n, _sp) in assignments
                      if _s == 'FPVIe' and ch != '—'})

    out = []
    out.append('=== 源表需求 → 能力 → 冲突 规划报告 ===\n')
    out.append('[需求清单]')
    for i, (r, src, ch, note, spec) in enumerate(assignments, 1):
        rng = ''
        if spec is not None:
            if r['type'] == 'fv':
                rng = f'  量程推荐: {recommend_range(src, "V", spec)}V 档' if recommend_range(src, 'V', spec) else ''
            elif r['type'] == 'fi':
                rr = recommend_range(src, 'I', spec)
                rng = f'  量程推荐: {fmt_ampere(rr)} 档' if rr else '  量程推荐: 超量程!'
            elif r['type'] == 'diff':
                peak = None
                if r['vrng']:
                    peak = max(abs(float(x)) for x in r['vrng'].split('-'))
                rng = f'  差分幅度 {peak}V → 量程推荐: {recommend_range("FPVIe", "V", peak)}V 档' if peak else ''
            elif r['type'] == 'hc':
                rr = recommend_range('FPVIe', 'I', r['cur'])
                rng = f'  量程推荐: {fmt_ampere(rr)} 档' if rr else '  量程推荐: 超量程!'
        head = f' {i}. {fmt_req(r):30s} → {src:14s} {ch:8s}'
        if note:
            out.append(head)
            out.append(f'      {note}{rng}')
        else:
            out.append(head + (rng or ''))

    out.append('')
    out.append(f'[FPVIe 通道预算] 占用 {fpvie_used} / 可用 {FPVIE_CHANNELS}  '
               f'→ {"已满" if fpvie_used >= FPVIE_CHANNELS else f"剩 {FPVIE_CHANNELS - fpvie_used} 通道"}')
    if conflicts:
        status = '✗ 缺失 — 本电路无法满足, 需人工裁决'
    elif residual_rc:
        status = '⚠ 继电器冲突避让不可行 — 第二短也撞同一继电器, 需串行分时'
    elif avoided or downgrades:
        status = '✓ 已自动解决 — 第二短/拆源表方案已给出, 可进入生成'
    else:
        status = '✓ 无冲突 — 可进入生成阶段'
    out.append(f'[结论] {status}')

    if overlaps:
        out.append('')
        out.append('[继电器共用] (同一继电器/同一节点, 良性共用可并行, 参照 TM641 K61 先例)')
        for o in overlaps:
            out.append(f'  · {o}')

    if avoided:
        out.append('')
        out.append('[继电器避让] (冲突继电器已自动换第二短, 不阻塞)')
        for a in avoided:
            out.append(f'  ✓ {a}')

    if residual_rc:
        out.append('')
        out.append('[继电器冲突·残留] (第二短也撞同一继电器 → 电路结构需串行分时, 不阻塞)')
        for c in residual_rc:
            out.append(f'  ⚠ {c}')

    if conflicts:
        out.append('')
        out.append('[缺失] (阻塞生成, 需人工裁决)')
        for c in conflicts:
            out.append(f'  ✗ {c}')

    if downgrades:
        out.append('')
        out.append('[自动降级/拆源表] (FPVIe 被占, 已自动改备选, 不阻塞)')
        for d in downgrades:
            out.append(f'  ✓ {d}')

    if tips:
        out.append('')
        out.append('[提示]')
        for t_ in tips:
            out.append(f'  · {t_}')

    return '\n'.join(out)


# ---------- demo 自检 ----------

DEMOS = {
    'demo1 大电流+差分 (FPVIe 2/2 刚好)': ['hc:0.2A,ACDRV1', 'diff:BST-SW,2.5-4.0'],
    'demo2 大电流+双差分 (FPVIe 3>2 → 自动拆两独立源表)': ['hc:0.2A,ACDRV1', 'diff:BST-SW', 'diff:ACDRV1-SW'],
    'demo3 差分+钉基准 (TM641 方案B 复现)': ['diff:BST-SW,2.5-4.0', 'fv:VCP_SW,3V'],
    'demo4 大电流+差分+钉基准 (FPVIe 满配+ACM200)': ['hc:0.5A,ACDRV1', 'diff:BST-SW', 'fv:VCP_SW,3V'],
    'demo5 TM643 BUBO (单端斜坡走最短, 不占FPVIe)': [
        'diff:VBAT-AGND,5-3-5', 'pw:PMID,5V', 'pw:VDRV,5V', 'pw:V1P5,5V', 'meas:NQON_HG1'],
    'demo6 真差分+精密点名 (DCM_UV 类, !前缀=DFT点名精度)': ['!diff:BST-SW,2.5-4.0', '!fv:VCP_SW,3V'],
    'demo7 Pin2Pin电流 (②\'规则: FPVIe浮动=最短, 优先两独立源)': ['fi:BST-SW,150mA'],
    'demo8 Pin2Pin优先于单端最短 (两独立源各0继电器也不换)': ['diff:BST-SW,2.5-4.0', 'fi:BST-SW,150mA'],
    'demo9 继电器共用·良性 (K48/K76 同落 BST, 可并行)': ['diff:BST-SW,2.5-4.0', 'fv:BST,3V'],
    'demo10 继电器冲突→自动避让 (K46 被双占不同节点, SW1-SW2 换 ACM200)': [
        'diff:BST-SW,2.5-4.0', 'diff:SW1-SW2'],
    'demo11 真缺失 (超量程 11A → ✗ 阻塞需裁决)': ['hc:11A,ACDRV1'],
    'demo12 串行残留 (3×hc 并行不可行 → ⚠ 需串行, 不阻塞)': [
        'hc:0.2A,ACDRV1', 'hc:0.3A,ACDRV2', 'hc:0.4A,ACDRV3'],
}


def main():
    try:                                      # 兼容 GBK 控制台 (win32)
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
    ap = argparse.ArgumentParser(description='源表需求→能力→冲突 规划门 (第一版, 只分析不生成)')
    ap.add_argument('--req', action='append', default=[], help='需求 DSL, 可重复')
    ap.add_argument('--demo', action='store_true', help='运行内置 4 场景自检')
    args = ap.parse_args()

    if args.demo:
        for name, reqs in DEMOS.items():
            print('=' * 74)
            print(name)
            print('=' * 74)
            print(render([parse_req(r) for r in reqs]))
            print()
        return

    if not args.req:
        ap.print_help()
        sys.exit(1)

    try:
        reqs = [parse_req(r) for r in args.req]
    except ValueError as e:
        print(f'解析错误: {e}', file=sys.stderr)
        sys.exit(2)

    print(render(reqs))


if __name__ == '__main__':
    main()
