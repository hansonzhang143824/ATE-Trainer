# -*- coding: utf-8 -*-
"""
gen_material_status.py — 材料状态索引（机读 · 哈希驱动）

定位（2026-09-13 用户拍板）:
  **Step1 收尾跑一次** → 产出 `knowledge/references/material_status.json`。
  该索引**只放状态 + 哈希 + 指针，绝不放内容**。
  之后**批次材料门只读这一份 JSON + 比哈希**，就能回答「整批有没有可参考的案例、缺口在哪、
  框架能不能选」，**全程不载入任何材料内容** → 门这一步的上下文成本 ≈ 0。

  `--check`：重算哈希与索引比对，**漂移即 FAIL**（材料被改/被删/新增未登记）。
             与 `check_input_sync.py` 同一范式：记录哈希 → 复算比对。

索引结构:
  {
    "schema": 1,
    "paramTypes": {
      "<类型>": {
        "tier1": {"<path>": {"exists": bool, "sha256": str|None}},   # 通用方法(L1-chip+L3-method) · 第一步必做
        "tier2": {...},                                              # 类型层(必读)
        "tier2_by_branch": {"OTP": {...}, "MTP": {...}},             # 分支型
        "tier3": {...},                                              # 原文(按需)
        "status": "complete" | "no-tier1" | "no-golden" | "missing-file"
      }
    },
    "testTypes": {"<7类>": {"framework": str|None, "available": bool}},
    "gaps": {"noTier1": [...], "noGolden": [...], "missingFiles": [...],
             "missingFrameworks": [...]}
  }

用法:
  python gen_material_status.py            # 生成/刷新索引
  python gen_material_status.py --check    # 复算比对(漂移/缺口) → exit 1 表示有漂移
"""

import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import proj_config
import verify_material_receipt as MG   # 材料要求表 = 机器权威（单一来源，勿另维护一份）

STATUS_REL = os.path.join('knowledge', 'references', 'material_status.json')

# 黄金案例台账（人读版）写入 param_type_index.md 的标记块；由 `gen_material_status.py --write-md` 刷新
MD_BEGIN = '<!-- GOLDEN-LEDGER:BEGIN (由 gen_material_status.py --write-md 生成, 勿手改) -->'
MD_END = '<!-- GOLDEN-LEDGER:END -->'

# 7 类项目结构类型 → 框架可用性（机器副本）
# 权威：knowledge/references/func_type_index.md「代码框架」表 + knowledge/standards/test-types.md
TEST_TYPE_FRAMEWORKS = {
    'Trim 参数':                 {'framework': 'Trim（framework.md）',            'available': True},
    '接触项目 Contact':           {'framework': None,                              'available': False},
    'OTP/MTP Pre/Post Readback': {'framework': 'Readback 五段式（L4 案例1~5）',    'available': True},
    'OTP/MTP Burn':              {'framework': 'Burn 五段式（L4 案例1~5）',        'available': True},
    'P2P Leakage':               {'framework': None,                              'available': False},
    'Leakage':                   {'framework': None,                              'available': False},
    '一般测试项目':               {'framework': '普通（framework.md）',             'available': True},
}


# 要点总结的规范六要素（标准结构）。齐 = 标准要点总结；不齐但有内容 = 分支注解（如 OTP 案例）
CANON_SECTIONS = ('参数类型', '角色', '关键结构', '时序', '测量', '适用场景')


def build_golden_cases(refs_root):
    """L4 黄金案例台账（机读）—— 2026-09-13 用户要求「全黄金案例按三档法处理 + 总结文档全部入索引」。

    每条记录: 案例文件 / 同名要点总结 / 总结类型 / 归属参数类型 / 是否已登记 / 同源别名。
    人读版在 `param_type_index.md` 的「黄金案例台账」表；本段供门禁与审计用。
    """
    gd = os.path.join(refs_root, 'L4-Golden-code')
    if not os.path.isdir(gd):
        return {}
    files = sorted(os.listdir(gd))
    codes = [f for f in files if f.endswith(('.cpp', '.txt'))]

    owner = {}
    for pt, req in MG.MATERIAL_REQUIREMENTS.items():
        paths = []
        for k in ('chip', 'method', 'code', 'code_ondemand'):
            paths += list(req.get(k, []))
        for v in (req.get('code_branch') or {}).values():
            paths += list(v)
        for p in paths:
            b = os.path.basename(p)
            if b in codes:
                owner.setdefault(b, []).append(pt)

    sha = {f: proj_config.sha256_file(os.path.join(gd, f)) for f in files}
    out = {}
    for f in codes:
        stem = f.rsplit('.', 1)[0]
        mdf = stem + '.md'
        md_txt = MG.read_enc(os.path.join(gd, mdf)) if mdf in files else ''
        heads = re.findall(r'^#{2,3}\s*(.+)$', md_txt, re.M)
        joined = ' | '.join(heads)
        miss = [c for c in CANON_SECTIONS if c not in joined]
        alias = next((o for o in codes if o != f and sha[o] and sha[o] == sha[f]), None)
        out[stem] = {
            'case': 'L4-Golden-code/' + f,
            'summary': ('L4-Golden-code/' + mdf) if mdf in files else None,
            'summaryKind': ('标准要点总结' if (heads and not miss)
                            else ('分支注解' if md_txt else '缺失')),
            'summaryMissingSections': miss if md_txt else list(CANON_SECTIONS),
            'paramTypes': sorted(owner.get(f, [])),
            'registered': bool(owner.get(f)),
            'aliasOf': ('L4-Golden-code/' + alias) if alias else None,
            'size': os.path.getsize(os.path.join(gd, f)),
            'summarySize': (os.path.getsize(os.path.join(gd, mdf)) if mdf in files else 0),
            'sha256': sha[f],
        }
    return out


def _entry(refs_root, paths):
    out = {}
    for p in sorted(paths):
        ap = MG._abs(refs_root, p)
        out[p] = {'exists': os.path.isfile(ap), 'sha256': proj_config.sha256_file(ap)}
    return out


def _flat(tiers):
    """把 tier 结构展平成 {path: info}（含 tier2_by_branch）；非 dict 的标量键（如 status）跳过。"""
    out = {}
    for k, v in tiers.items():
        if not isinstance(v, dict):
            continue
        if k == 'tier2_by_branch':
            for sub in v.values():
                out.update(sub)
        else:
            out.update(v)
    return out


def build(refs_root):
    param_types, gaps = {}, {'noTier1': [], 'noGolden': [], 'missingFiles': []}
    for pt, req in MG.MATERIAL_REQUIREMENTS.items():
        tiers = {
            'tier1': _entry(refs_root, list(req.get('chip', [])) + list(req.get('method', []))),
            'tier2': _entry(refs_root, list(req.get('code', []))),
            'tier3': _entry(refs_root, list(req.get('code_ondemand', []))),
        }
        if req.get('code_branch'):
            tiers['tier2_by_branch'] = {b: _entry(refs_root, v)
                                        for b, v in sorted(req['code_branch'].items())}

        allf = _flat(tiers)
        missing = sorted(p for p, i in allf.items() if not i['exists'])
        has_golden = bool(tiers['tier2']) or bool(tiers.get('tier2_by_branch')) or bool(tiers['tier3'])
        if missing:
            status = 'missing-file'
        elif not tiers['tier1']:
            status = 'no-tier1'
        elif not has_golden:
            status = 'no-golden'
        else:
            status = 'complete'
        tiers['status'] = status
        param_types[pt] = tiers

        if status == 'no-tier1':
            gaps['noTier1'].append(pt)
        elif status == 'no-golden':
            gaps['noGolden'].append(pt)
        if missing:
            gaps['missingFiles'].append({'paramType': pt, 'files': missing})

    test_types = dict(TEST_TYPE_FRAMEWORKS)
    gaps['missingFrameworks'] = sorted(t for t, v in test_types.items() if not v['available'])

    golden = build_golden_cases(refs_root)
    gaps['unregisteredCases'] = sorted(v['case'] for v in golden.values()
                                       if not v['registered'] and not v['aliasOf'])
    gaps['missingSummaries'] = sorted(v['case'] for v in golden.values() if not v['summary'])
    gaps['nonStandardSummaries'] = sorted(v['case'] for v in golden.values()
                                          if v['summary'] and v['summaryKind'] != '标准要点总结')

    return {
        'schema': 1,
        '_generator': 'gen_material_status.py',
        '_note': '只放状态+哈希+指针，不放内容；批次材料门读本文件即可判定可用性/缺口，不必载入材料。',
        'paramTypes': param_types,
        'testTypes': test_types,
        'goldenCases': golden,
        'gaps': gaps,
    }


def do_check(refs_root, out_path, as_json=False):
    """复算哈希与索引比对 → 漂移 / 缺口 报告。"""
    if not os.path.isfile(out_path):
        print('[material-status] FAIL: 索引不存在 → %s（先在 Step1 收尾跑一次生成）' % out_path)
        return 1
    with open(out_path, encoding='utf-8') as f:
        old = json.load(f)
    new = build(refs_root)

    drift, checked = [], 0
    for pt, tiers in (old.get('paramTypes') or {}).items():
        for p, info in _flat(tiers).items():
            if p not in _flat(new['paramTypes'].get(pt, {})):
                drift.append('%s: %s 已不在要求表中（登记过时?）' % (pt, p))
                continue
            checked += 1
            cur = _flat(new['paramTypes'][pt])[p]
            if bool(info.get('exists')) != bool(cur['exists']):
                drift.append('%s: %s 存在性变化 %s → %s' % (pt, p, info.get('exists'), cur['exists']))
            elif (info.get('sha256') or '') != (cur.get('sha256') or ''):
                drift.append('%s: %s 内容已变（哈希不符）' % (pt, p))
    for pt, tiers in (new.get('paramTypes') or {}).items():
        for p in _flat(tiers):
            if p not in _flat(old.get('paramTypes', {}).get(pt, {})):
                drift.append('%s: 新增材料未登记 → %s' % (pt, p))
    for t, v in new.get('testTypes', {}).items():
        if t not in (old.get('testTypes') or {}):
            drift.append('testTypes: 新增类型未登记 → %s' % t)
    for k, v in new.get('goldenCases', {}).items():
        o = (old.get('goldenCases') or {}).get(k)
        if o is None:
            drift.append('goldenCases: 新增案例未登记 → %s' % v['case'])
        elif o.get('sha256') != v.get('sha256'):
            drift.append('goldenCases: %s 内容已变（哈希不符）' % v['case'])
    for k in (old.get('goldenCases') or {}):
        if k not in new.get('goldenCases', {}):
            drift.append('goldenCases: 案例已移除 → %s' % k)

    g = new['gaps']
    if as_json:
        print(json.dumps({'drift': drift, 'checked': checked, 'gaps': g},
                         ensure_ascii=False, indent=2))
        return 1 if drift else 0

    print('[material-status] check: 比对材料 %d 项' % checked)
    print('[material-status] 缺口: 无 Tier1 %d 类 %s' % (len(g['noTier1']), g['noTier1']))
    print('[material-status]       无黄金 %d 类 %s' % (len(g['noGolden']), g['noGolden']))
    print('[material-status]       缺文件 %d 组' % len(g['missingFiles']))
    print('[material-status]       无框架 %d 类 %s' % (len(g['missingFrameworks']), g['missingFrameworks']))
    if drift:
        print('\n*** DRIFT (材料状态索引已过期, 请重跑 gen_material_status.py) ***')
        for d in drift:
            print('  - ' + d)
        return 1
    print('\n材料状态索引：无漂移')
    return 0


def render_md(data):
    """把黄金案例台账渲染成 markdown 表（人读版，写入 param_type_index.md 的标记块）。"""
    rows = ['### 黄金案例台账（L4-Golden-code 全量 · 总结文档全部登记于此）',
            '',
            '> 机读版：`material_status.json` 的 `goldenCases` 段（含哈希，`--check` 判漂移）；'
            '**三档定位见 `../standards/context-management.md §6`**；'
            '**全部总结文档尚待用户 review**（清单见 `docs/黄金案例-要点总结-review清单.md`）。',
            '',
            '| 案例 | 要点总结 | 总结类型 | 归属参数类型 | 同源别名 |',
            '|---|---|---|---|---|']
    for k in sorted(data['goldenCases']):
        v = data['goldenCases'][k]
        rows.append('| `%s` | `%s` | %s | %s | %s |' % (
            os.path.basename(v['case']),
            os.path.basename(v['summary']) if v['summary'] else '**缺失**',
            v['summaryKind'],
            ', '.join(v['paramTypes']) or '—',
            os.path.basename(v['aliasOf']) if v['aliasOf'] else '—'))
    return '\n'.join(rows)


def write_md(path, data):
    """把台账写进 <path> 的标记块之间（无标记则追加）。"""
    block = MD_BEGIN + '\n' + render_md(data) + '\n' + MD_END
    if not os.path.isfile(path):
        print('[material-status] FAIL: 目标不存在 → %s' % path)
        return 1
    with open(path, encoding='utf-8') as f:
        t = f.read()
    if MD_BEGIN in t and MD_END in t:
        i = t.index(MD_BEGIN)
        j = t.index(MD_END) + len(MD_END)
        t = t[:i] + block + t[j:]
    else:
        t = t.rstrip('\n') + '\n\n' + block + '\n'
    with open(path, 'w', encoding='utf-8') as f:
        f.write(t)
    print('[material-status] 台账已写入 %s（%d 个案例）' % (path, len(data['goldenCases'])))
    return 0


REVIEW_Q = (
    ('角色抽象对不对', '里面对 PIN/节点/源表的描述是「角色」还是本项目具体名字？能否跨项目迁移'),
    ('四类关键特殊结构齐不齐', '① 被测件本体结构 ② 大电流/差分路径→浮动源 ③ 配对/台阶结构 ④ 测试方法本质'),
    ('协议/变体有没有被误当类判据', '项目专有的寄存器/密钥/继电器/量程应标为「变体」，不能当该类的通用判据'),
    ('档位归属对不对', '该是 Tier1（通用方法）/ Tier2（类型层）/ Tier3（原文）？'),
)


def render_review(data):
    """渲染「要点总结 review 清单」（给用户 action 用）。"""
    g = data['goldenCases']
    L = ['# 黄金案例「要点总结」review 清单（待用户 action）', '']
    L.append('> 派生自 `knowledge/references/material_status.json` 的 `goldenCases` 段'
             '（`scripts/gen_material_status.py` 生成，重跑 `--write-review` 刷新）。')
    L.append('> 规则：**新增/修订的任何总结文档必须由用户 review 确认才算落地** —— '
             '`skills/nuvolta-codegen.md` §6.1 第 4 条（**自审不算过门**）。')
    L.append('> 状态：**全部未 review**（2026-09-13 用户要求登记为待办，见 `MEMORY.md` ▶ 待办第 3 条）。')
    L.append('')
    L.append('## 一、怎么 review（对每份 `.md` 问 4 句）')
    L.append('')
    for i, (t, d) in enumerate(REVIEW_Q, 1):
        L.append('%d. **%s** —— %s' % (i, t, d))
    L.append('')
    L.append('## 二、待 review 清单（%d 份，与台账一一对应）' % len(g))
    L.append('')
    L.append('| # | 要点总结 | 对应案例 | 总结类型 | 归属参数类型 | 总结大小 | review |')
    L.append('|---|---|---|---|---|---|:---:|')
    for n, k in enumerate(sorted(g), 1):
        v = g[k]
        L.append('| %d | `%s` | `%s` | %s | %s | %s | ☐ |' % (
            n,
            os.path.basename(v['summary']) if v['summary'] else '**缺失**',
            os.path.basename(v['case']),
            v['summaryKind'],
            ', '.join(v['paramTypes']) or '—',
            ('%dK' % max(1, v.get('summarySize', 0) // 1024)) if v['summary'] else '—'))
    L.append('')
    L.append('## 三、review 通过之后')
    L.append('')
    L.append('1. 记录结论（在 `material_status.json` 对应案例记 `reviewed: true`，或直接在本清单勾选）')
    L.append('2. 若发现总结有误 → 改 `.md` → 重跑 `gen_material_status.py`'
             '（哈希变化会被 `--check` 报出）→ 再来一轮 review')
    L.append('3. 更新 `MEMORY.md` ▶ 待办第 3 条的进度')
    return '\n'.join(L) + '\n'


def main(argv):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except AttributeError:
        pass
    cfg = proj_config.load(proj_config.config_from_argv(argv))
    refs_root = os.path.join(cfg['_root'], 'knowledge', 'references')
    out_path = os.path.join(refs_root, 'material_status.json')

    if '--check' in argv:
        return do_check(refs_root, out_path, '--json' in argv)

    data = build(refs_root)
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
        f.write('\n')

    if '--write-md' in argv:
        i = argv.index('--write-md')
        target = argv[i + 1] if i + 1 < len(argv) and not argv[i + 1].startswith('--') else \
            os.path.join(refs_root, 'param_type_index.md')
        write_md(target, data)

    if '--write-review' in argv:
        i = argv.index('--write-review')
        target = argv[i + 1] if i + 1 < len(argv) and not argv[i + 1].startswith('--') else \
            os.path.join(cfg['_root'], 'docs', '黄金案例-要点总结-review清单.md')
        with open(target, 'w', encoding='utf-8') as f:
            f.write(render_review(data))
        print('[material-status] review 清单已写入 %s（%d 份）' % (target, len(data['goldenCases'])))

    g = data['gaps']
    st, kinds = {}, {}
    for pt, tiers in data['paramTypes'].items():
        st[tiers['status']] = st.get(tiers['status'], 0) + 1
    for v in data['goldenCases'].values():
        kinds[v['summaryKind']] = kinds.get(v['summaryKind'], 0) + 1
    print('[material-status] 写入 %s' % out_path)
    print('[material-status] 参数类型 %d 类: %s' % (len(data['paramTypes']),
          ', '.join('%s=%d' % kv for kv in sorted(st.items()))))
    print('[material-status] 测试类型 %d 类: 有框架 %d / 无框架 %d %s'
          % (len(data['testTypes']),
             len(data['testTypes']) - len(g['missingFrameworks']),
             len(g['missingFrameworks']), g['missingFrameworks']))
    print('[material-status] 黄金案例 %d 个: %s' % (len(data['goldenCases']),
          ', '.join('%s=%d' % kv for kv in sorted(kinds.items()))))
    print('[material-status] 缺口: 无 Tier1 %s' % (g['noTier1'] or '无'))
    print('[material-status]       未登记案例 %s' % (g['unregisteredCases'] or '无'))
    print('[material-status]       缺要点总结 %s' % (g['missingSummaries'] or '无'))
    print('[material-status]       非标准结构总结(分支注解等) %d 个: %s'
          % (len(g['nonStandardSummaries']), g['nonStandardSummaries'] or '无'))
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
