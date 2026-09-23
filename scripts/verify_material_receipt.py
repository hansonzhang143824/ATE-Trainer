# -*- coding: utf-8 -*-
"""
verify_material_receipt.py — 材料门（生成前拦截）

生成代码前，校验该 TM **有没有可参考的案例**，且**该案例确实被读过并用上**：

  路径1（索引）: 参数类型已在 param_type_index 登记，
                 且**登记的必读材料全部已在 receipt 声明 + 文件全部存在**
  路径2（案例+要点）: 声明的 code 黄金案例存在 + 有同名 .md 要点总结
  ── 二者其一满足 ──
  【读证】声明了 code 黄金案例时，必须同时给出:
    ① goldenSha256: 读过的 golden 文件内容哈希（可与磁盘复核，证明按内容处理过）
    ② structures  : 四类关键特殊结构已提取（非空）——context-management.md §5 铁律
                   dut_body / fpvi_short / paired_staircase / measure_essence

  没有可参考的案例 → FAIL 禁止生成；缺材料由用户 action 提供。

用法:
  python verify_material_receipt.py [--receipt <receipt.json>] [--tm TMxxx,TMyyy]
                                    [--no-read-proof] [--audit-rules]

receipt JSON 结构（skill/agent 在生成循环材料门步写入；路径相对 references 根）:
  {
    "TM641": {
      "param_type": "UVLO",
      "materials": ["L1-chip/UVLO.md", "L3-method/UVLO.md", "L4-Golden-code/UVLO.cpp"],
      "goldenSha256": {"L4-Golden-code/UVLO.cpp": "<sha256>"},
      "structures": {
        "dut_body": "...", "fpvi_short": "...",
        "paired_staircase": "...", "measure_essence": "..."
      },
      "note": "自由备注"
    },
    "OTP_XXX": {                                   # 分支型 + 三档阶梯的完整形态
      "param_type": "OTP·MTP",
      "branch": "OTP",                             # 必填: OTP / MTP（决定 Tier2 读哪批案例）
      "tier1": "insufficient",                     # 必填: Tier1 通用方法够不够写码
      "materials": ["L1-chip/OTP-MTP.md",
                    "L3-method/OTP-MTP-Readback-Burn.md",
                    "L4-Golden-code/OTP_READ_PRE_POST_BURN-案例1.md",
                    "L4-Golden-code/OTP_READ_PRE_POST_BURN-案例2.md",
                    "L4-Golden-code/OTP_READ_PRE_POST_BURN-案例3.md",
                    "L4-Golden-code/OTP_READ_PRE_POST_BURN-案例1.txt"],   # Tier3 按需(仅分支匹配的 1 份)
      "goldenSha256": { ... },
      "structures": { ... }
    },
    "TM_LEGACY": { ..., "readProofWaived": "本条为既有收据补录，读证自下一批起强制" }
  }

三档消费顺序（2026-09-13 用户拍板，context-management.md §6）:
  Tier1 通用方法(L1-chip + L3-method)   ← 第一步且必做
     └─ 够写吗? ── 够 → tier1=sufficient, **不加载任何案例**（声明 Tier3 一律 FAIL: 矛盾）
                 └─ 不够 → tier1=insufficient → Tier2 类型层(.md, 按 branch 过滤, 必读)
                                            └─ 仍不够 → Tier3 原文(按需, 只读 branch 匹配的 1 份)

不传 --receipt 时默认读 <project_dir>/material_receipts.json。

2026-09-13 修（用户拍板 A+B）:
  A 路径修复: MATERIAL_REQUIREMENTS 原用旧前缀 chip/·method/·code/（实际目录早已是
    L1-chip/·L3-method/·L4-Golden-code/）→ 全部 18 条指向不存在的文件、--audit-rules FAIL。
    同时补齐索引里有而脚本缺的 4 类（PSM_THREHOLD / VC_OFFSET / VC_CLAMP_LOW / OTP·MTP）。
  B 主门升级: 原 `path1 = bool(req)` —— 参数类型一登记就直接 PASS，**根本不比对 receipt
    声明的材料**（receipt 形同装饰）。改为「登记要求 ⊆ 已声明 且 全部存在」；
    并新增【读证】：golden 哈希冻结 + 四类结构提取，把「存在性门」升级为「被用性门」
    （TM607-609 根因正是「材料存在却未读取」）。
"""

import json
import os
import sys

import proj_config

# references/ 下的四个 L 层目录（案例材料实际位置）
DIR_CHIP = 'L1-chip'
DIR_METHOD = 'L3-method'
DIR_CODE = 'L4-Golden-code'
DIR_DEBUG = 'L5-debug'

# 四类关键特殊结构（context-management.md §5「黄金案例 = 关键特殊结构参考」）
STRUCT_KEYS = ('dut_body', 'fpvi_short', 'paired_staircase', 'measure_essence')
STRUCT_DESC = {
    'dut_body': '被测件本体结构（两端各连哪个节点）',
    'fpvi_short': '大电流/差分路径 → 浮动源跨两点',
    'paired_staircase': '配对/台阶结构（含该配对上的电容处理）',
    'measure_essence': '测试方法本质（测量值怎么来）',
}

# Tier1（通用方法）判定 —— 2026-09-13 用户拍板「Tier1 是黄金案例使用的第一步且必做，
# 只有它撑不住写码才按需往下加载（Tier2 类型层 → Tier3 原文）」。
# 有 Tier3 阶梯的类型（定义了 code_ondemand）必须显式记录这个判定，否则「只读 Tier1 就写码」
# 与「判过 Tier1 够用」无法区分 —— 后者才是允许跳过案例的依据。
TIER1_STATES = ('sufficient', 'insufficient')

# 材料要求（机器权威）。与 knowledge/references/param_type_index.md 同名联动索引保持一致;
# 改索引（新增/改参数类型、归档/改名材料）必须同步改这里 + 跑 --audit-rules 核对。
# 每条: chip/method/code 均为「存在即必读」, debug 按需不强制; code 多文件 = 全部必读。
MATERIAL_REQUIREMENTS = {
    'RDSON': {
        'chip': [DIR_CHIP + '/RDSON.md'],
        'method': [DIR_METHOD + '/RDSON.md'],
        'code': [DIR_CODE + '/Rdson.cpp'],
    },
    'VBG': {
        'chip': [], 'method': [],
        # Trim 类必须同时有: ①test.cpp 的 trim 函数 ②sub.cpp 的 measure 实现 ③Trim sub 通用模板
        # （2026-09-13 补: 原只登记 ①，sub.cpp measure 漏登 —— 而没它 Trim 根本写不出）
        'code': [DIR_CODE + '/TM130_Trim_VBG.cpp',
                 DIR_CODE + '/TM130_sub_measure.cpp',
                 DIR_CODE + '/sub-measure-template.cpp'],
    },
    'BUCK HS Gain': {
        'chip': [], 'method': [],
        'code': [DIR_CODE + '/TM623_Trim_BUCK_HS_Gain.cpp',
                 DIR_CODE + '/TM623_sub_measure.cpp',
                 DIR_CODE + '/sub-measure-template.cpp'],
    },
    'VAC GD present': {
        'chip': [], 'method': [],
        'code': [DIR_CODE + '/toggle-template.cpp'],
    },
    'UVLO': {
        'chip': [DIR_CHIP + '/UVLO.md'],
        'method': [DIR_METHOD + '/UVLO.md'],
        'code': [DIR_CODE + '/UVLO.cpp'],
    },
    'Current Threshold': {
        'chip': [DIR_CHIP + '/Current-Threshold.md'],
        'method': [DIR_METHOD + '/Current-Threshold.md'],
        'code': [DIR_CODE + '/HS_ZCD.cpp', DIR_CODE + '/LS_ZCD.cpp'],   # 双案例, 缺一 FAIL
    },
    'CurrentSense': {
        'chip': [DIR_CHIP + '/CurrentSense.md'],
        'method': [DIR_METHOD + '/CurrentSense.md'],
        'code': [],                                                     # 待归档
    },
    'VBAT OVP': {
        'chip': [DIR_CHIP + '/UVLO.md'],
        'method': [DIR_METHOD + '/UVLO.md'],
        'code': [DIR_CODE + '/OVP.cpp'],
    },
    'PSM_THREHOLD': {
        'chip': [DIR_CHIP + '/UVLO.md'],
        'method': [DIR_METHOD + '/UVLO.md'],
        'code': [DIR_CODE + '/UVLO.cpp'],
    },
    'VC_OFFSET': {
        'chip': [DIR_CHIP + '/UVLO.md'],
        'method': [DIR_METHOD + '/UVLO.md'],
        'code': [DIR_CODE + '/UVLO.cpp'],
    },
    'VC_CLAMP_LOW': {
        'chip': [], 'method': [],
        'code': [DIR_CODE + '/toggle-template.cpp'],
    },
    'OTP·MTP': {
        # 三档结构（2026-09-13 用户拍板）—— 先吃「通用方法」，不足以写码再按分支进「类型层」，
        # 原文（Tier3）一律按需，避免 357KB 原文把上下文打爆。
        'chip': [DIR_CHIP + '/OTP-MTP.md'],
        'method': [DIR_METHOD + '/OTP-MTP-Readback-Burn.md'],          # Tier1 通用方法(公共流程)
        'code': [],
        'code_branch': {                                               # Tier2 类型层(按 OTP/MTP 分支)
            'OTP': [DIR_CODE + '/OTP_READ_PRE_POST_BURN-案例%d.md' % n for n in (1, 2, 3)],
            'MTP': [DIR_CODE + '/OTP_READ_PRE_POST_BURN-案例%d.md' % n for n in (4, 5)],
        },
        'code_ondemand': [                                             # Tier3 原文(按需, 建议 subagent 隔离读)
            DIR_CODE + '/OTP_READ_PRE_POST_BURN-案例%d.txt' % n for n in range(1, 6)
        ],
    },
    # 差分电压对（BST−SW 自举为例）: 2026-09-13 新增（用户拍板 C）——
    # 原索引无此类，导致差分对测试只能回 test.cpp 现翻旧函数（context-management §4 明令禁止）
    'Diff Pair': {
        'chip': [DIR_CHIP + '/UVLO.md', DIR_CHIP + '/01-bootstrap-hs-drive.md'],
        'method': [DIR_METHOD + '/diff-pair-spec.md'],
        'code': [DIR_CODE + '/TM1205_TRX_BST_UV_GD.cpp'],
    },
}


def read_enc(path):
    """rb 读(经 DLP 白名单解密) + 编码回退解码。"""
    with open(path, 'rb') as f:
        raw = f.read()
    for enc in ('utf-8-sig', 'utf-8', 'gbk', 'latin-1'):
        try:
            return raw.decode(enc)
        except (UnicodeDecodeError, ValueError):
            continue
    return raw.decode('utf-8', errors='replace')


def _norm(p):
    return os.path.normpath(str(p)).replace('\\', '/')


def branch_names(param_type):
    """该参数类型登记的分支（如 OTP·MTP → OTP / MTP）；无分支返回 []。"""
    req = MATERIAL_REQUIREMENTS.get(param_type) or {}
    return sorted((req.get('code_branch') or {}).keys())


def ondemand_materials(param_type):
    """Tier3「按需」菜单: 原文级大件 —— 不强制, 按分支选, 声明了才校验存在性 + 读证。"""
    req = MATERIAL_REQUIREMENTS.get(param_type) or {}
    return [_norm(p) for p in (req.get('code_ondemand') or [])]


def required_materials(param_type, branch=None):
    """Tier1+Tier2 必读: chip + method + code + (指定 branch 的 code_branch)。

    code_branch 型参数类型必须给 branch —— 对应「OTP 只看 OTP 的、MTP 只看 MTP 的」。
    """
    req = MATERIAL_REQUIREMENTS.get(param_type)
    if req is None:
        return None
    out = []
    for key in ('chip', 'method', 'code'):
        out.extend(req.get(key, []))
    if branch:
        out.extend((req.get('code_branch') or {}).get(branch, []))
    return [_norm(p) for p in out]


def _abs(refs_root, p):
    if os.path.isabs(p):
        return p
    return os.path.join(refs_root, p.replace('/', os.sep))


def _summary_path(p):
    """要点总结与案例同名: L4-Golden-code/HS_ZCD.cpp → L4-Golden-code/HS_ZCD.md

    2026-09-13: 原实现只认 'code/' 前缀 + '.cpp' —— 路径修复后前缀变 L4-Golden-code/，
    且 OTP 家族是 .txt，故改为「L4-Golden-code 下 .cpp/.txt 都取同名 .md」。
    """
    if p.startswith(DIR_CODE + '/') and p.endswith(('.cpp', '.txt')):
        return p.rsplit('.', 1)[0] + '.md'
    return None


def _existing(refs_root, paths):
    return [p for p in paths if not os.path.isfile(_abs(refs_root, p))]


def check_read_proof(tm, entry, refs_root, errors, warns):
    """【读证】证明 golden 确实被按内容处理过 + 四类结构已提取。

    ① goldenSha256: receipt 冻结的哈希必须与磁盘当前一致（不一致 = 案例被改过/抄错文件）
    ② structures  : 四类关键特殊结构非空（context-management.md §5）
    条目带非空 readProofWaived → 跳过读证, 只出 WARN（既有收据补录用, 不追溯伪造证据）。
    """
    waived = str(entry.get('readProofWaived') or '').strip()
    code_declared = [p for p in (_norm(x) for x in entry.get('materials', []))
                     if p.startswith(DIR_CODE + '/')]
    if not code_declared:
        return True
    if waived:
        warns.append('%s: 读证豁免（%s）' % (tm, waived))
        return True

    ok = True
    hashes = entry.get('goldenSha256') or {}
    for p in code_declared:
        got = hashes.get(p)
        if not got:
            errors.append('%s: 缺读证 goldenSha256["%s"] — 未证明该案例被读取（生成前必须真读）' % (tm, p))
            ok = False
            continue
        cur = proj_config.sha256_file(_abs(refs_root, p))
        if cur and str(cur) != str(got).strip().lower():
            errors.append('%s: 读证哈希不符 goldenSha256["%s"] — 案例文件在读取后被改动，或抄错文件' % (tm, p))
            ok = False

    st = entry.get('structures') or {}
    miss = [k for k in STRUCT_KEYS if not str(st.get(k, '')).strip()]
    if miss:
        errors.append('%s: 四类关键特殊结构未提取 → 缺 %s（见 context-management.md §5；'
                      '只声明文件不提取结构 = 材料存在却没用上）'
                      % (tm, ' / '.join('%s(%s)' % (k, STRUCT_DESC[k]) for k in miss)))
        ok = False
    return ok


def load_status_index(refs_root):
    """读 Step1 收尾生成的材料状态索引（只读状态+哈希，不载内容）。缺 → None。"""
    p = os.path.join(refs_root, 'material_status.json')
    if not os.path.isfile(p):
        return None
    try:
        with open(p, encoding='utf-8') as f:
            return json.load(f)
    except ValueError:
        return None


def check_test_type(tm, entry, status, gaps, warns):
    """Test Type 检查（2026-09-13 新增）: 该测试项的**代码框架**是否已有。

    Test Type 来源 = 收据显式 `test_type`（Contact / OTP Readback / OTP Burn / P2P / Leakage
    这几类需要显式信号，无法纯机械派生）；未标则不判（Step3 可用 test_conditions.yaml 的
    testType 机械派生 #1 Trim / #7 一般测试项目）。
    框架不可用 → **软门**: 记录缺口 + 按 DFT 写码。
    """
    tt = str(entry.get('test_type') or '').strip()
    if not tt:
        return
    if not status:
        warns.append('%s: 标了 test_type="%s" 但 material_status.json 缺失 → 无法判框架可用性'
                     '（Step1 收尾应跑 gen_material_status.py）' % (tm, tt))
        return
    info = (status.get('testTypes') or {}).get(tt)
    if info is None:
        gaps.append('%s: test_type="%s" 不在 7 类登记中 → 记录缺口，按 DFT 写码' % (tm, tt))
        return
    if not info.get('available'):
        gaps.append('%s: Test Type「%s」**现无代码框架模板** → 记录缺口，按 DFT 写码'
                    '（补框架待用户提供案例）' % (tm, tt))


def check_entry(tm, entry, refs_root, errors, gaps, warns, read_proof=True,
                status=None, strict=False):
    """errors = 硬门（收据不实：声明不实/未按规程声明/读证不足）→ FAIL
    gaps   = 软门（材料缺口：世上没有这个案例）→ 记录 + WARN + **放行**（2026-09-13 用户拍板）

    分界依据（用户流程图）：两条「否」分支 = 无 Param Type / 无黄金案例 → 记录后按 DFT 写；
    「是」分支之后的检索失败（文件缺失、没读）不属于"缺材料"，是收据不实 → 硬门。
    """
    param_type = entry.get('param_type', '')
    declared = [_norm(p) for p in entry.get('materials', [])]
    declared_set = set(declared)

    # 分支型参数类型（如 OTP·MTP）: 必须先声明走哪一支 ——「OTP 只看 OTP 的、MTP 只看 MTP 的」
    branches = branch_names(param_type)
    branch = str(entry.get('branch') or '').strip()
    if branches:
        if not branch:
            errors.append('%s (%s): 缺 branch —— 该类型分 %s, 必须声明走哪一支（决定 Tier2 读哪批案例）'
                          % (tm, param_type, ' / '.join(branches)))
            return
        if branch not in branches:
            errors.append('%s (%s): branch="%s" 未登记（合法: %s）'
                          % (tm, param_type, branch, ' / '.join(branches)))
            return

    # Tier1 判定（2026-09-13 用户拍板）: Tier1 通用方法是黄金案例使用的**第一步且必做**;
    # 只有它撑不住写码才按需往下加载。有 Tier3 阶梯的类型必须显式记录这个判定。
    menu = set(ondemand_materials(param_type))
    ondemand_declared = sorted(p for p in declared if p in menu)
    tier1 = str(entry.get('tier1') or '').strip()
    if menu:
        if not tier1:
            errors.append('%s (%s): 缺 tier1 —— 必须记录「Tier1 通用方法是否足以写码」'
                          '（合法: %s）; 够→不加载案例, 不够→按需加载 Tier2/Tier3'
                          % (tm, param_type, ' / '.join(TIER1_STATES)))
            return
        if tier1 not in TIER1_STATES:
            errors.append('%s (%s): tier1="%s" 非法（合法: %s）'
                          % (tm, param_type, tier1, ' / '.join(TIER1_STATES)))
            return
        if tier1 == 'sufficient' and ondemand_declared:
            errors.append('%s: tier1=sufficient（判 Tier1 够写）却声明了 Tier3 原文 %s '
                          '—— 矛盾: 够写就不该加载原文' % (tm, ', '.join(ondemand_declared)))
            return

    # Test Type 检查（2026-09-13 新增）: 框架可用性 → 无框架同样走「记录 + 按 DFT 写」
    check_test_type(tm, entry, status, gaps, warns)

    req = required_materials(param_type, branch) or []
    req_set = set(req)

    problems = []

    # 0. 声明的材料必须都存在 —— 「声明了就要真读得到」（硬门: 声明不实/路径漂移/抄错名）
    declared_absent = sorted(_existing(refs_root, declared))
    if declared_absent:
        errors.append('%s: receipt 声明的材料文件不存在 → %s（路径漂移或抄错文件名）'
                      % (tm, ', '.join(declared_absent)))

    # 路径1（索引）: 参数类型已登记 且 登记的必读材料「全部已声明」且「全部存在」
    path1 = False
    if req_set:
        undeclared = sorted(req_set - declared_set)
        absent = sorted(_existing(refs_root, req_set))
        if undeclared:
            # 类型有登记要求却未声明 → 没按规程检索 → 硬门
            errors.append('%s (%s): 已登记必读材料但 receipt 未声明 → %s'
                          % (tm, param_type, ', '.join(undeclared)))
        if absent:
            # 登记表指向不存在的文件 → 材料/登记表缺口 → 软门（并提示修 registry）
            gaps.append('%s (%s): 登记表指向不存在的文件 → %s（需修 MATERIAL_REQUIREMENTS / 索引）'
                        % (tm, param_type, ', '.join(absent)))
        path1 = not undeclared and not absent

    # 路径2（案例+要点）: 声明的 code 黄金案例存在 且 带同名 .md 要点总结
    code_declared = [p for p in declared if p.startswith(DIR_CODE + '/')]
    path2 = False
    if code_declared:
        sums = [_summary_path(p) for p in code_declared]
        if all(sums):
            miss = sorted(set(_existing(refs_root, code_declared + sums)))
            path2 = not miss
            if miss:
                errors.append('%s: 声明的案例/要点总结缺失 → %s' % (tm, ', '.join(miss)))

    if not (path1 or path2) and not errors:
        # 纯"没有可参考的案例" → 软门: 记录缺口, 按 DFT + 规则写码
        reason = '; '.join(problems) if problems else '该参数类型无任何已登记材料'
        if not req_set:
            reason = '参数类型「%s」未登记（索引没有这一类）' % (param_type or '未标')
        msg = ('%s (%s): 没有可参考的案例 → %s。**记录缺口，按 DFT + 上电/测量/机台手册/log/框架 规则写码**；'
               '并在收尾汇总上报；同类积累后回收提炼成新 golden/规则' % (tm, param_type or '未标', reason))
        (errors if strict else gaps).append(msg)
        return

    # 【读证】（B）: 声明了 code 黄金案例就必须给出「读过 + 提取过结构」的证据（硬门）
    if read_proof and code_declared:
        check_read_proof(tm, entry, refs_root, errors, warns)


def main(argv):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except AttributeError:
        pass
    cfg = proj_config.load(proj_config.config_from_argv(argv))
    refs_root = os.path.join(cfg['_root'], 'knowledge', 'references')

    receipt_path = None
    tms = None
    gap_out = None
    for i, a in enumerate(argv):
        if a == '--receipt' and i + 1 < len(argv):
            receipt_path = argv[i + 1]
        elif a == '--tm' and i + 1 < len(argv) and not argv[i + 1].startswith('--'):
            tms = argv[i + 1]
        elif a == '--gap-out' and i + 1 < len(argv) and not argv[i + 1].startswith('--'):
            gap_out = argv[i + 1]

    if '--audit-rules' in argv:
        return audit(refs_root)

    read_proof = '--no-read-proof' not in argv   # 批次前置(--pre)阶段用: 读证留到逐组写码时
    strict = '--strict' in argv                  # 旧口径: 无案例也 FAIL（默认软门: 记录+放行）

    if receipt_path is None:
        receipt_path = os.path.join(cfg['project_dir'], 'material_receipts.json')

    if not os.path.isfile(receipt_path):
        print('[material-gate] FAIL: 没有可参考的案例（材料记录不存在）→ %s' % receipt_path)
        print('  先写收据（声明本批每个 TM 的参数类型 + 材料）；缺材料由用户 action 提供。')
        return 1

    try:
        receipt = json.loads(read_enc(receipt_path))
    except ValueError as exc:
        print('[material-gate] FAIL: receipt JSON 解析失败 → %s' % exc)
        return 1

    status = load_status_index(refs_root)
    errors, gaps, warns = [], [], []
    if tms:
        for tm in [t.strip() for t in tms.split(',') if t.strip()]:
            if tm not in receipt:
                errors.append('%s: receipt 中无此 TM 条目（生成前必须写收据）' % tm)
            else:
                check_entry(tm, receipt[tm], refs_root, errors, gaps, warns,
                            read_proof, status, strict)
    else:
        for tm, entry in receipt.items():
            check_entry(tm, entry, refs_root, errors, gaps, warns,
                        read_proof, status, strict)

    print('[material-gate] receipt=%s' % receipt_path)
    print('[material-gate] entries=%d read-proof=%s mode=%s FAIL=%d GAP=%d WARN=%d'
          % (len(receipt), 'on' if read_proof else 'off',
             'strict' if strict else 'soft', len(errors), len(gaps), len(warns)))
    if warns:
        print('\nWARNINGS:')
        for w in warns:
            print('  - ' + w)
    if gaps:
        print('\n*** GAP (材料缺口 · 软门: 记录后按 DFT + 规则继续, 不阻塞) ***')
        for g in gaps:
            print('  - ' + g)
        print('  → 收尾须把以上缺口**整批汇总上报**；同类积累后回收提炼成新 golden / 规则。')
    if gaps and gap_out:
        try:
            with open(gap_out, 'w', encoding='utf-8') as f:
                json.dump({
                    'receipt': receipt_path,
                    'count': len(gaps),
                    'gaps': gaps,
                    '_note': 'Step3 批次前置产出的「材料/框架缺口」清单（软门已放行，不阻塞）。'
                             'Step5 收尾据此做**回收提炼**：把无参照写成的 TM 提炼成新 golden'
                             '（`L4-Golden-code/<函数名>.cpp` + 同名 `.md` 要点总结）并登记索引，'
                             '或补一条 specialized rule —— 让该缺口下次不再是缺口。',
                }, f, ensure_ascii=False, indent=1)
                f.write('\n')
            print('\n[material-gate] 缺口清单已落盘 → %s（Step5 收尾据此回收提炼）' % gap_out)
        except OSError as exc:
            warns.append('缺口清单写入失败: %s' % exc)

    if errors:
        print('\n*** FAIL (材料门 · 收据不实: 声明/规程/读证) ***')
        for e in errors:
            print('  - ' + e)
        return 1
    if gaps:
        print('\n材料门 PASS（有缺口 %d 项，已记录；按 DFT + 规则继续）' % len(gaps))
    else:
        print('\n材料门 PASS（有可参考的案例 + 读证齐）')
    return 0


def audit(refs_root):
    """--audit-rules 自检: 全部登记材料文件存在（含分支 + 按需菜单）+ 与索引参数类型一致。"""
    errors = []
    for pt in MATERIAL_REQUIREMENTS:
        paths = list(required_materials(pt) or [])
        for b in branch_names(pt):
            paths.extend(required_materials(pt, b) or [])
        paths.extend(ondemand_materials(pt))
        for p in sorted(set(paths)):
            if not os.path.isfile(_abs(refs_root, p)):
                errors.append('MATERIAL_REQUIREMENTS[%s] 指向不存在的文件 → %s' % (pt, p))
    index_params = _index_param_types(refs_root)
    script_params = set(MATERIAL_REQUIREMENTS.keys())
    for p in sorted(index_params - script_params):
        errors.append("param_type_index 有参数类型 '%s' 但脚本缺 → 材料门漏检" % p)
    for p in sorted(script_params - index_params):
        errors.append("脚本有参数类型 '%s' 但 param_type_index 无 → 可能过时" % p)
    print('[material-gate] audit-rules: requirements=%d index_params=%d'
          % (len(script_params), len(index_params)))
    if errors:
        print('*** AUDIT FAIL ***')
        for e in errors:
            print('  - ' + e)
        return 1
    print('AUDIT PASSED')
    return 0


def _index_param_types(refs_root):
    """解析 param_type_index.md「同名联动索引」表的参数名列(最左列), 返回 set。"""
    idx = os.path.join(refs_root, 'param_type_index.md')
    if not os.path.isfile(idx):
        return set()
    params = set()
    in_table = False
    for line in read_enc(idx).splitlines():
        if line.startswith('## '):
            if in_table:
                break
            if '同名联动索引' in line:
                in_table = True
                continue
        if not in_table:
            continue
        if line.startswith('|'):
            cells = [c.strip() for c in line.strip('|').split('|')]
            if not cells:
                continue
            first = cells[0]
            if first in ('参数',) or set(first) <= set('-:'):
                continue
            if first and not first.startswith('>'):
                params.add(first)
    return params


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
