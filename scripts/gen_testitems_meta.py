# -*- coding: utf-8 -*-
# gen_testitems_meta.py — TestItemMeta 生成器 (纯 DFT 派生, 不碰原理图)
#
# 职责: 以 OVERVIEW (DFT 意图层权威) 机械生成 meta json。
#   capAuthority 四权威集 (供 check_testitems_meta / verify_relay_trace 检查E):
#     powered_pins  本函数被 FV/FI 供电的 PIN (vset/iset/Power列/Dynamic裸PIN)
#     mi_pins       本函数测电流的 PIN (Check/Dynamic 列 I(pin)) → Cap 豁免
#     ramp_pins     本函数 ramp/扫描源 PIN (vset 同 pin ≥2 不同值) → Cap 豁免
#     testpad_pins  测试垫偏置 PIN (AMUX/VDM/ATEST/DTEST0/NTC) → 不查 Cap
#
# 边界: 原理图通路由 sch_parse.py → SCH-Connect-Map 独立产出, 二者在消费端 join。
#       收尾覆盖完整性校验 (门禁) 由 check_testitems_meta.py 负责, 本脚本只生成。
#
# 路径约定: 默认读 project_config.json (--config 可覆盖), --* 参数可单独覆盖。
#   VS 工程源 (test.cpp / StdAfx.h) 与输入 xlsx 默认取自 config。
#
# 用法:
#   python gen_testitems_meta.py [--dump] [--audit] [--legacy <tm000_102.json>]
#   python gen_testitems_meta.py ... --dump     # 每函数派生结果预览 (人工审核, 不写)
#   python gen_testitems_meta.py ... --audit    # 全函数 4 集对照表 (不写)
#   python gen_testitems_meta.py ... --legacy <tm000_102.json>   # 合并手工丰富字段 (可选)
#
# 数据源:
#   OVERVIEW  = *.xlsx /OVERVIEW 表 (DFT 意图层, 权威)
#   test.cpp  = 函数名单 (仅函数名与 Item 编号)
#   StdAfx.h  = Cap 继电器定义 (cap family: VCC/VBAT/VAC/VBUS)
# 原则: 信息源层级 — DFT 意图层(OVERVIEW) > 对象名反推

import argparse
import io
import json
import os
import re
import sys

import proj_config

try:
    import openpyxl
except ImportError:
    openpyxl = None

# Cap 家族: PIN token → Cap 继电器名 (cap_defs 权威, StdAfx.h #define)
# VAC1/VAC2/VAC3/VAC123 均属 VAC 家族 (K21_VAC_Cap)
TESTPAD_NODES = frozenset(['ATEST0', 'ATEST1', 'ATEST2', 'VDM', 'AMUX', 'DTEST0', 'NTC'])


def read_enc(path):
    """DLP 透明加密回退: utf-8-sig→utf-8→gbk→latin-1"""
    with open(path, 'rb') as f:
        raw = f.read()
    for enc in ('utf-8-sig', 'utf-8', 'gbk', 'latin-1'):
        try:
            return raw.decode(enc)
        except (UnicodeDecodeError, ValueError):
            continue
    return raw.decode('utf-8', errors='replace')


def load_overview(xlsx):
    """OVERVIEW → {Item: row}, row 为 dict (列名→值, 已去 None 换空串)"""
    wb = openpyxl.load_workbook(xlsx, read_only=True, data_only=True)
    ws = wb['OVERVIEW']
    rows = list(ws.iter_rows(values_only=True))
    header = [str(h).strip() if h is not None else '' for h in rows[0]]
    rec = {}
    for r in rows[1:]:
        if not r[0] or not str(r[0]).startswith('TM'):
            continue
        row = {}
        for i, h in enumerate(header):
            v = r[i] if i < len(r) else None
            row[h] = '' if v is None else v
        rec[str(r[0])] = row
    return rec


# Trim 函数名 → OVERVIEW Item 编号 (Trim_* 命名不符合 TM\d+_ 前缀)
TRIM_ITEM_MAP = {
    'Trim_IZTC_RES':   '133',   # TM133 IZTC_RES (ATEST0_MUX=8)
    'Trim_BG_RES_DIV': '135',   # TM135 BG_RES_DIV (ATEST0_MUX=10)
    'Trim_VBG':        '139',   # TM139 VBG (ATEST0_MUX=12)
}


def load_testcpp_fns(src):
    """test.cpp -> {Item编号: 函数名} (仅名单, 非权威内容源)
    支持 'TM<digits>_*' 与 Trim_* 命名 (Trim 函数按 TRIM_ITEM_MAP 映射到 Item)"""
    out = {}
    for line in read_enc(src).splitlines():
        m = re.match(r'DUT_API int ((?:TM\d+(?:_\d+)?_\w+|Trim_\w+))\(short funcindex', line)
        if m:
            name = m.group(1)
            tm = re.match(r'TM(\d+(?:_\d+)?)_', name)
            item = tm.group(1) if tm else TRIM_ITEM_MAP.get(name)
            if item:
                out.setdefault(item, name)
    return out


def load_cap_defs(defs):
    """StdAfx.h #define Kxx_<PIN>_Cap → {PIN: relay}"""
    caps = {}
    for m in re.finditer(r'#define\s+(K\d+_(\w+)_Cap)\s+\d+', read_enc(defs)):
        caps.setdefault(m.group(2), m.group(1))
    return caps


def _split_multi(v):
    return [s.strip() for s in str(v).split('\n') if s.strip()]


def _pin_of(expr):
    """'I(VBUS)'/'V(ATEST0)'/裸 'VAC1' → 'VBUS'/'ATEST0'/'VAC1' (大写)"""
    m = re.match(r'[IV]\(([^)]+)\)', expr)
    if m:
        return m.group(1).upper()
    return expr.upper()


def is_toggle(row):
    """toggle 测试判定 (Vth/CMP/UV/PRST/HT/SNK_DET 比较器 / Indirect / 观测 DTEST0)"""
    name = str(row['Name']).upper()
    ck = str(row['Check'])
    # ATEST 模拟测量守卫 (TM1008 联动): Check 只含 V/I(ATESTx) (无 DTEST) 且无 Dynamic
    # 且 vset 无多值 ramp → 纯 ATEST mux 静态测量 (VREF 类), 名字含 VTH/CMP 也不算 toggle
    ck_toks = [t.strip() for t in _split_multi(ck) if t.strip()]
    if ck_toks and 'DTEST' not in ck.upper() and not str(row['Dynamic']).strip():
        code_all = '\n'.join(_split_multi(row['Code1']) + _split_multi(row['Code2'])
                             + _split_multi(row['Code3']))
        vs = {}
        for _pin, _val in re.findall(r'vset\[(\w+),([-\d.eE+]+)', code_all):
            vs.setdefault(_pin.upper(), set()).add(_val)
        only_atest = all(t.replace(' ', '').upper() in ('V(ATEST0)', 'I(ATEST0)',
                                                        'V(ATEST1)', 'I(ATEST1)')
                         for t in ck_toks)
        if only_atest and not any(len(v) >= 2 for v in vs.values()):
            return False
    if ('_VTH' in name or '_CMP' in name or '_UV' in name or '_PRST' in name
            or '_HT_' in name or '_MAX_CMP' in name or '_SNK_DET' in name
            or 'SNK_DET' in name or 'Path_ON' in str(row['Name']).lower()
            or 'V(DTEST0)' in ck or str(row['Test']) == 'Indirect'):
        return True
    return False


def derive(row, hw=None):
    """从 OVERVIEW 行派生 capAuthority 四权威集
    powered_pins 语义 = 本函数被 FV 供电的供电轨 (vset + Power列 + Dynamic裸PIN);
    iset 负载 (VMCU/VCC 输出) 是测量目标非供电轨, 不参与 Cap 闭合判定。
    (与 OVERVIEW Power 列只列供电轨的语义一致)"""
    code = '\n'.join(_split_multi(row['Code1']) + _split_multi(row['Code2'])
                     + _split_multi(row['Code3']))
    vs, is_ = {}, {}
    for cmd, pin, val in re.findall(r'(vset|iset)\[(\w+),([-\d.eE+]+)', code):
        (vs if cmd == 'vset' else is_).setdefault(pin.upper(), set()).add(val)
    pw = {_pin_of(x) for x in _split_multi(row['Power'])}
    dy_raw = _split_multi(row['Dynamic'])
    dy_bare = {_pin_of(x) for x in dy_raw if not re.match(r'[IV]\(', x)}
    dy_pins = {_pin_of(x) for x in dy_raw}
    ck = _split_multi(row['Check'])
    ck_pins = {_pin_of(x) for x in ck if re.match(r'[IV]\(', x)}

    forced = set(vs) | pw | dy_bare
    mi = {_pin_of(x) for x in (dy_raw + ck) if re.match(r'I\(', x)}
    # ramp: 仅 toggle 测试中 vset 同 pin ≥2 个不同值 (Vth/CMP ramp 扫描源);
    # 非 toggle (如 shipmode 掉电序列) 的 2 值不算 ramp (供电→闭 Cap)
    toggle = is_toggle(row) or bool(hw and _two_seg_ramp_pin(hw))  # 两段斜坡(升+降) 亦判 toggle (TM643 联动)
    ramp = {p for p, vals in vs.items() if toggle and len(vals) >= 2}
    helper = str(row['HELPER']).upper()
    if toggle and 'RAMP' in helper:
        for p in vs:
            base = re.sub(r'[0-9]+$', '', p)
            if p in helper or base in helper:
                ramp.add(p)
    testpad = forced & TESTPAD_NODES
    return {
        'powered_pins': sorted(forced),
        'mi_pins': sorted(mi),
        'ramp_pins': sorted(ramp),
        'testpad_pins': sorted(testpad),
        '_vs': {p: sorted(v) for p, v in vs.items()},
        '_iset': sorted(is_),
        '_pw': sorted(pw),
        '_dy': sorted(dy_pins),
        '_ck': sorted(ck_pins),
    }


def build_param(row):
    """Check 列 → params (check/MV→'MV', I/MI→'MI')"""
    params = []
    for x in _split_multi(row['Check']):
        m = re.match(r'([IV])\(([^)]+)\)', x)
        if m:
            params.append({'check': 'MI' if m.group(1) == 'I' else 'MV',
                           'checkPin': m.group(2).upper(),
                           'dftItem': str(row['Item'])})
    return params


def build_hwinit(row):
    """Code 列 vset/iset/en_tm/field/delay → hardwareInit 列表"""
    code = '\n'.join(_split_multi(row['Code1']) + _split_multi(row['Code2'])
                     + _split_multi(row['Code3']))
    hw = []
    for m in re.finditer(r'(vset|iset)\[(\w+),([-\d.eE+]+),([\d.e+-]+),([01])\]', code):
        cmd, pin, val, t, ig = m.groups()
        hw.append({'cmd': cmd, 'pin': pin.lower(), 'value': float(val),
                   'time': t, 'ignore': int(ig)})
    for m in re.finditer(r'(en_tm|en_scan|wait_warmup)\[\]', code):
        hw.append({'cmd': m.group(1)})
    for m in re.finditer(r'field\[', code):
        hw.append({'cmd': 'field'})
    return hw


def classify_testtype(row, hw=None):
    """Test/Trim/Purpose 列 → testType（2026-08-27 拍板: 两段斜坡 升+降 → 强制 toggle，覆盖 DFT 声明）"""
    if hw and _two_seg_ramp_pin(hw):
        return 'toggle'   # 两段斜坡(升+降) → AWG toggle（TM210/211/615/616 命中）
    if str(row['Trim']).strip():
        return 'trim'
    if is_toggle(row):
        return 'toggle'   # Vth/CMP/UV/PRST 比较器 toggle (含 ramp)
    return 'normal'


def _two_seg_ramp_pin(hw):
    """同 pin 全部 vset 序列（跨 power/ramp 段收集）中，3 值滑动窗口「首尾相等且中值不同」→ 两段斜坡(升+降) pin；无则 None。
    与 gen_test_conditions._split_power_ramps 同逻辑（窗口滑动 1），
    保证 meta.testType 与 YAML 摘要一致（TM210/211 vac1 3→0→3→0 / TM643 vbat 5→3→5 → 命中）。
    TM643 修正: 原实现只看连续同 pin run (power 段 5 与 ramp 段 3→5 分离 → run 长度不足) → 误判 normal;
    改为跨段收集全长序列再滑窗，5→3→5 命中两段斜坡 (2026-08-30 TM643 DFT 修正联动)。"""
    seqs = {}
    for c in hw:
        if c.get('cmd') == 'vset':
            seqs.setdefault(str(c.get('pin', '')).upper(), []).append(str(c.get('value')))
    for pin, vals in seqs.items():
        for k in range(len(vals) - 2):
            if vals[k] != vals[k + 1] and vals[k] == vals[k + 2]:
                return pin
    return None


# 具体参数类型（11 类）关键词判定：Name 大写后按序正则命中即停
PARAM_TYPE_RULES = (
    (r'RDS.?ON',        'RDSON'),
    (r'UVLO|OVP|PRST|VBAT_LOW|RECHG', 'UVLO'),
    (r'ZCD|IPEAK|IPEK', 'Current Threshold'),
    (r'OSC|FREQ',       'Freq Related'),
    (r'AMUX',           'AMUX'),
    (r'OFFSET|VOS|GAIN', '电压阈值'),   # offset/gain = 普通电压阈值测试，非 current sense
    (r'P2P|LEAK',       'Leakage'),
    (r'SENSE',          'CurrentSense'),  # current sense: 给电流测试电压，且一定不是 ramp 形式（下方守卫）
    (r'OTP|MTP|BURN|READBACK', 'OTP/MTP'),
)


def _is_ramp_test(hw):
    """ramp 形式 = 两段斜坡(升+降) vset ∨ iset 斜坡；CurrentSense 判定的反条件。"""
    return bool(_two_seg_ramp_pin(hw)) or any(c.get('cmd') == 'iset' for c in hw)


def _classify_param_type(name, hw=None):
    """参数名 → 具体参数类型（11 类）；无命中 → '一般'（agent 复核）。
    CurrentSense 铁律（2026-08-27 用户定）：给电流测试电压(静态 FV+MI)，且一定不是 ramp 形式——
    命中 SENSE 但为 ramp 斜坡测试时跳过（如 VC_OFFSET 斜坡测电流阈值 → 电压阈值）。"""
    n = str(name).upper()
    for pat, t in PARAM_TYPE_RULES:
        if re.search(pat, n):
            if t == 'CurrentSense' and hw and _is_ramp_test(hw):
                continue  # ramp 形式不可能是 current sense → 落回后续规则/一般
            return t
    return '一般'


def _classify_project_type(row, hw):
    """OVERVIEW 行 + hardwareInit → 项目结构类型（7 类，按序命中即停）
    Trim 优先（机制最重）；两段斜坡/比较器 → 一般测试项目(AWG)；其余 → 一般测试项目。
    Contact/OTP/Leakage/P2P 需用户意图（Notes/对话），机械不可判 → 归一般，由 agent 复核。"""
    if row['Trim']:
        return 'trim'
    if is_toggle(row) or _two_seg_ramp_pin(hw):
        return '一般测试项目(AWG)'
    return '一般测试项目'


def _extract_registers(sv_path):
    """reg_config/<tm>.sv → [{reg, data, desc}]（entertestmode() 后 I2CWriteSameData 序列）
    找不到文件返回 None，找到但无 I2C 写返回 []。黄金 test.cpp 是其镜像。"""
    if not sv_path or not os.path.exists(sv_path):
        return None
    text = read_enc(sv_path)
    idx = text.find('entertestmode')
    body = text[idx:] if idx >= 0 else text
    lines = body.splitlines()
    regs = []
    rx_w = re.compile(r'I2CWriteSameData\s*\(\s*DEV_ADDR\s*,\s*(0x[0-9A-Fa-f]+)\s*,\s*(0x[0-9A-Fa-f]+)\s*\)')
    rx_f = re.compile(r'//\s*field\[([^\]]+)\]')
    rx_p = re.compile(r'\(\s*([A-Za-z0-9_]+)\s*,\s*([0-9]+)\s*\)')
    rx_wc = re.compile(r'Write\s+reg\s+0x\w+\s*=\s*[0-9]+')
    for i, ln in enumerate(lines):
        m = rx_w.search(ln)
        if not m:
            continue
        desc = ''
        for j in range(i + 1, min(i + 6, len(lines))):
            fm = rx_f.search(lines[j])
            if fm:
                pairs = rx_p.findall(fm.group(1))
                desc = ', '.join('%s=%s' % (k, v) for k, v in pairs)
                break
            if rx_w.search(lines[j]) or 'vset[' in lines[j] or 'entertestmode' in lines[j]:
                break
        if not desc:
            wc = rx_wc.search(ln)
            if wc:
                desc = wc.group(0)
        # 定稿格式: 小写 0x 前缀 + 大写 hex 最小 2 位
        regs.append({'reg': '0x%02X' % int(m.group(1), 16),
                     'data': '0x%02X' % int(m.group(2), 16), 'desc': desc})
    return regs


def load_legacy(legacy):
    """合并 tm000_102.json 手工丰富字段 (sources/softwareInit/measure/powerOn/relaySetOn/merged)"""
    if not legacy or not os.path.exists(legacy):
        return {}, {}
    with open(legacy, encoding='utf-8') as f:
        data = json.load(f)
    rich = {fn['functionName']: fn for fn in data.get('functions', [])}
    return rich, data.get('merged', [])


def main():
    cfg = proj_config.load(proj_config.config_from_argv(sys.argv))
    ap = argparse.ArgumentParser(description='TestItemMeta 生成器 (纯 DFT 派生, 不碰原理图)')
    ap.add_argument('--config', default=None, help='project_config.json (默认 workspace 根)')
    ap.add_argument('--xlsx', default=cfg['inputs']['dft'], help='OVERVIEW 源 xlsx (DFT 意图层权威) 路径')
    ap.add_argument('--src', default=cfg['derived']['test_cpp'], help='test.cpp 路径 (VS 工程源, 函数名单)')
    ap.add_argument('--defs', default=cfg['derived']['stdafx_h'], help='StdAfx.h 路径 (Cap 继电器定义)')
    ap.add_argument('--out', default=cfg['outputs']['meta'], help='输出 meta json 路径')
    ap.add_argument('--reg-config', default=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                    'Project', 'DALI', 'reg_config'), help='reg_config 目录（寄存器补充源，Tom AMS Test Code）')
    ap.add_argument('--legacy', default=None, help='可选: tm000_102.json 手工丰富字段')
    ap.add_argument('--dump', action='store_true', help='每函数派生结果预览 (不写)')
    ap.add_argument('--audit', action='store_true', help='全函数 4 集对照表 (不写)')
    args = ap.parse_args()

    ov = load_overview(args.xlsx)
    fns = load_testcpp_fns(args.src)
    cap_defs = load_cap_defs(args.defs)
    legacy, merged = load_legacy(args.legacy)

    functions = []
    audit_lines = []
    for item in sorted(fns, key=lambda x: [int(p) for p in x.split('_')]):
        name = fns[item]
        row = ov.get('TM' + item)
        if not row:
            print(f'[WARN] {item} {name}: 无 OVERVIEW 记录, 跳过')
            continue
        hw = build_hwinit(row)
        ca = derive(row, hw)
        dft_item = str(row['Item'])
        fn = {
            'functionName': name,
            'testType': classify_testtype(row, hw),
            'dftItem': dft_item,
            'projectType': _classify_project_type(row, hw),
            'paramType': _classify_param_type(row['Name'], hw),
            'overview': {
                'level': str(row['Level']), 'name': str(row['Name']),
                'desc': str(row['Description'])[:160],
                'expectValue': row['ExpectValue'], 'unit': row['Unit'],
                'test': row['Test'], 'helper': str(row['HELPER'])[:200],
            },
            'params': build_param(row),
            'hardwareInit': hw,
            'registers': (_extract_registers(os.path.join(args.reg_config, dft_item.lower() + '.sv'))
                          or []),
            'capAuthority': {k: ca[k] for k in
                             ('powered_pins', 'mi_pins', 'ramp_pins', 'testpad_pins')},
        }
        # 合并 legacy 手工丰富字段 (sources/softwareInit/measure/powerOn/relaySetOn)
        if name in legacy:
            lg = legacy[name]
            for k in ('sources', 'softwareInit', 'measure', 'powerOn', 'relaySetOn', 'dftItems'):
                if k in lg:
                    fn[k] = lg[k]
        functions.append(fn)
        # 与 Cap 家族交集审计
        fam_hit = sorted({pt for pt in cap_defs for p in ca['powered_pins']
                          if p == pt or p.startswith(pt) or pt.startswith(p)})
        fam_exempt = sorted({pt for pt in fam_hit
                             if any(p == pt or p.startswith(pt) or pt.startswith(p)
                                    for p in ca['mi_pins'] + ca['ramp_pins'])
                             or any(p == pt or p.startswith(pt) or pt.startswith(p)
                                    for p in ca['testpad_pins'])})
        need = sorted(set(fam_hit) - set(fam_exempt))
        audit_lines.append((item, name, ','.join(ca['powered_pins']),
                            ','.join(ca['mi_pins']), ','.join(ca['ramp_pins']),
                            ','.join(ca['testpad_pins']), ','.join(need)))

    if args.dump:
        for item, name, pw, mi, rp, tp, need in audit_lines:
            print(f'{item:8s} {name:34s} pw[{pw}] mi[{mi}] ramp[{rp}] tp[{tp}] need_cap[{need}]')
        return

    if args.audit:
        print('%-8s %-34s %-24s %-16s %-14s %-14s %s' %
              ('Item', 'fn', 'powered', 'mi', 'ramp', 'testpad', 'cap_need'))
        for line in audit_lines:
            print('%-8s %-34s %-24s %-16s %-14s %-14s %s' % line)
        return

    meta = {
        '_comment': 'TestItemMeta — gen_testitems_meta.py 从 OVERVIEW(DFT意图层)权威生成, '
                    '寄存器补充自 reg_config/<tm>.sv, 项目/参数类型解析时判定; '
                    'capAuthority 供 check_testitems_meta / verify_relay_trace 检查E',
        'source': 'OVERVIEW 表 (DFT意图层)',
        # 输入同步 stamp: 记录本 meta 派生自哪一版 DFT (check_input_sync.py 判 DFT↔meta 同版本)。
        # 只放源哈希、不放时间戳 → 生成保持字节可复现。
        '_syncStamp': {
            'dftSha256': proj_config.sha256_file(args.xlsx),
        },
        'capFamilies': cap_defs,
        'merged': merged,
        'functions': functions,
    }
    with open(args.out, 'w', encoding='utf-8') as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    print(f'[ok] 生成 {args.out}: {len(functions)} 个函数')
    print('[ok] Cap 家族: ' + json.dumps(cap_defs))
    if audit_lines:
        need_all = set()
        for _, _, _, _, _, _, need in audit_lines:
            need_all.update(need.split(',') if need else [])
        need_all.discard('')
        print(f'[ok] 需闭 Cap 家族分布: {sorted(need_all)}')


if __name__ == '__main__':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    main()
