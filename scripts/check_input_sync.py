# -*- coding: utf-8 -*-
"""
check_input_sync.py — 输入同步一致性门（流水线之前 · 有货先验的上游）

定位:
  在 Step0(sch-parse) 与 CBIT 的 dll mtime 门 **之前**, 先判「输入侧的派生文件是否与源同版本」。
  - 全部匹配 → **什么都不用改**（no-op），直接进下游流程。
  - 有不匹配 → 才重生成（本脚本只报「该重生成哪一项 + 命令」，不自己动手改产物）。

两条版本链:
  [DFT 组]  Dali_testmode.xlsx --(gen_testitems_meta.py)--> dali_tm_meta.json
                              --(gen_test_conditions.py)--> test_conditions.yaml
      ① DFT↔meta : meta._syncStamp.dftSha256 == sha256(DFT)
      ② meta↔YAML: yaml._sync.metaSha256     == sha256(meta)
  [SCH 组]  Dali-SCH.csv --(csv_schematic_adapter_v2 + sch_parse)--> SCH-Connect-Map.txt
                                                                 └-> Component-Statistic.txt
      ③ csv↔map↔statistic : validation_manifest.json.txt 的
           input.sha256 / artifacts.sch_connect_map_sha256 / artifacts.component_statistic_sha256
           == 当前实算（三项全等才算同版本）

判定状态:
  MATCH     版本一致（下游可放心沿用）
  DRIFT     源已变、派生文件落后 → 需重生成
  NO-STAMP  派生文件无版本记录（老产物）→ 需重生成以建立基线
  MISSING   文件缺失

退出码: 0 = 全部 MATCH（无需修改）; 1 = 有 DRIFT / NO-STAMP / MISSING

用法:
  python check_input_sync.py [--config <json>] [--json]
"""

import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import proj_config


def _sha(path):
    """sha256 大写（与 csv_*_v2 侧 .hexdigest().upper() 对齐）；缺失返回 None。"""
    v = proj_config.sha256_file(path)
    return v.upper() if v else None


def _read_json(path):
    if not path or not os.path.isfile(path):
        return None
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def _read_yaml_sync(path):
    """只读 YAML 顶层 _sync 块（不引 yaml 依赖，认本平台 emit 的固定缩进格式）。

    返回 (metaSha256, dftSha256)；文件或块缺失 → (None, None)。
    """
    if not path or not os.path.isfile(path):
        return None, None
    try:
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.read().splitlines()
    except Exception:
        return None, None
    sync, in_sync = {}, False
    for ln in lines:
        if ln.startswith('_sync:'):
            in_sync = True
            continue
        if in_sync:
            if ln.startswith('  ') and ':' in ln:
                k, v = ln.split(':', 1)
                sync[k.strip()] = v.strip() or None
            else:
                break
    return sync.get('metaSha256'), sync.get('dftSha256')


def _cmp(expect, actual):
    if expect is None:
        return 'NO-STAMP'
    if actual is None:
        return 'MISSING'
    return 'MATCH' if str(expect).upper() == str(actual).upper() else 'DRIFT'


def check_dft_group(cfg):
    """DFT 组: xlsx → meta → yaml"""
    dft = cfg['inputs']['dft']
    meta_p = cfg['outputs']['meta']
    yaml_p = cfg['outputs'].get('test_conditions') or os.path.join(
        cfg['project_dir'], 'meta', 'test_conditions.yaml')

    dft_sha = _sha(dft)
    meta = _read_json(meta_p)
    meta_sha = _sha(meta_p)
    y_meta_sha, y_dft_sha = _read_yaml_sync(yaml_p)

    items = []

    # ① DFT ↔ meta
    if meta is None:
        st, detail = 'MISSING', 'meta 文件不存在'
    else:
        stamp = meta.get('_syncStamp') or {}
        st = _cmp(stamp.get('dftSha256'), dft_sha)
        detail = 'meta._syncStamp.dftSha256 vs sha256(DFT)'
    items.append({
        'group': 'DFT', 'link': '① DFT↔meta', 'artifact': os.path.basename(meta_p),
        'source': os.path.basename(dft), 'status': st, 'detail': detail,
    })

    # ② meta ↔ YAML
    if not os.path.isfile(yaml_p):
        st, detail = 'MISSING', 'yaml 文件不存在'
    else:
        st = _cmp(y_meta_sha, meta_sha)
        detail = 'yaml._sync.metaSha256 vs sha256(meta)'
    items.append({
        'group': 'DFT', 'link': '② meta↔YAML', 'artifact': os.path.basename(yaml_p),
        'source': os.path.basename(meta_p), 'status': st, 'detail': detail,
    })

    # ③ 三者的共同 DFT 版本（串起来看: yaml 里带的 dftSha256 也应等于当前 DFT）
    if os.path.isfile(yaml_p) and y_dft_sha:
        st = _cmp(y_dft_sha, dft_sha)
        items.append({
            'group': 'DFT', 'link': '③ YAML↔DFT', 'artifact': os.path.basename(yaml_p),
            'source': os.path.basename(dft),
            'status': st, 'detail': 'yaml._sync.dftSha256 vs sha256(DFT) (跨 meta 追溯一致性)',
        })

    return items


def check_sch_group(cfg):
    """SCH 组: csv → map + statistic（以 validation_manifest.json.txt 为版本记录）"""
    csv_p = cfg['inputs']['csv_schematic']
    map_p = cfg['intermediates']['sch_connect_map']
    stat_p = cfg['intermediates']['component_statistic']
    man_p = cfg['intermediates'].get('sch_validation_manifest') or os.path.join(
        cfg['project_dir'], 'validation_manifest.json.txt')

    man = _read_json(man_p)
    items = []

    if man is None:
        for art, src in ((map_p, csv_p), (stat_p, csv_p)):
            items.append({
                'group': 'SCH', 'link': 'csv↔产物', 'artifact': os.path.basename(art),
                'source': os.path.basename(src), 'status': 'NO-STAMP',
                'detail': 'manifest 缺失 → 无版本记录',
            })
        return items

    inp = man.get('input') or {}
    arts = man.get('artifacts') or {}

    # ③a csv: manifest 记录的输入哈希 vs 当前
    items.append({
        'group': 'SCH', 'link': '③ csv(manifest)', 'artifact': os.path.basename(man_p),
        'source': os.path.basename(csv_p),
        'status': _cmp(inp.get('sha256'), _sha(csv_p)),
        'detail': 'manifest.input.sha256 vs sha256(csv)',
    })
    # ③b/c 产物: manifest 记录的产物哈希 vs 当前
    for key, art, label in (('sch_connect_map_sha256', map_p, 'map'),
                            ('component_statistic_sha256', stat_p, 'statistic')):
        items.append({
            'group': 'SCH', 'link': '③ %s(产物)' % label, 'artifact': os.path.basename(art),
            'source': os.path.basename(csv_p),
            'status': _cmp(arts.get(key), _sha(art)),
            'detail': 'manifest.artifacts.%s vs sha256(产物)' % key,
        })

    return items


# ============================================================================
# RS-1..RS-4: run 作用域 meta 修正的**可检出性断言** (t28)
# ============================================================================
# 为什么需要这一组 (实测根因, T26-F2 / t28 任务书):
#   `scripts/gen_testitems_meta.py` 从 DFT OVERVIEW 行重新派生 meta 时, 会**逐字节还原**
#   被 t26 覆盖前的 meta —— 实测探针 `team/artifacts/<run>/t26-regen-probe/dali_tm_meta.regen.json`
#   = 146,180 B / 1c849664... == t26 改动前的现盘 meta。也就是说一次普通重生成会**静默抹掉**
#   ① TM601 powered_pins 的 VBUS 移除 ② TM600/TM601 的 mi_pins 修正 ③ 两函数 hardwareInit 的冻结
#   ATE 激励对齐; 而旧版本门只看两条**自派生**哈希链 (meta 的 DFT 戳 / yaml 的 meta 戳),
#   重生成时二者同拍刷新 ⇒ 仍然打印 `IN SYNC`、exit 0 ⇒ **门禁全绿却检不出回退**。
#   本组把"回退"变成**可检出的门禁失败** (status=RS-FAIL ⇒ exit 1)。
#
# 读法: meta 为 DLP 透明加密文件, 必须由 python (授权读者) 以 rb 读 + utf-8-sig 解码。
# 规格来源: team/artifacts/<run>/meta-excitation-override.json → recommendedGateAssertions
#   (RS-1..RS-4, 已被 rule-reviewer 确认"可直接实现")。本脚本只实现, 不改 meta/契约/生成器。

RS_STATUS = 'RS-FAIL'        # 新增断言失败的专用状态 (计入 NEW-RED 分类)


def _read_json_rb(path):
    """rb 读 + utf-8-sig —— DLP 透明加密下必须这样读 (pwsh/普通文本读只会拿到 TSZ 密文)。"""
    if not path or not os.path.isfile(path):
        return None
    with open(path, 'rb') as f:
        raw = f.read()
    try:
        return json.loads(raw.decode('utf-8-sig'))
    except (ValueError, UnicodeDecodeError):
        return None


def _num(v):
    """数值规范化: 4.2 -> '4.2'; 15.0 -> '15'; 使字面量比较不受 int/float 影响。"""
    try:
        f = float(v)
    except (TypeError, ValueError):
        return str(v)
    return str(int(f)) if f == int(f) else repr(f)


def _vset_map(fn):
    """{pin_lower: [value_str, ...]} —— 只取 hardwareInit 里的 vset 命令。"""
    out = {}
    for h in (fn.get('hardwareInit') or []):
        if str(h.get('cmd', '')).lower() == 'vset' and h.get('pin') is not None:
            out.setdefault(str(h['pin']).lower(), []).append(_num(h.get('value')))
    return out


def _caps_upper(ca, key):
    return {str(x).upper() for x in ((ca or {}).get(key) or [])}


# RS-3 期望值 = 冻结 ATE 激励 (setup-contract tmDeltas.ateStimulus，经 BD-08 裁定)
RS_ATE_VSET = {
    'TM600_HS_RDSON': {'vbat': '4.2', 'pmid': '15', 'bst_sw': '5', 'vdrv': '5'},
    'TM601_LS_RDSON': {'vbat': '4.2', 'pmid': '9', 'vdrv': '5'},
}


def check_meta_override_rs(cfg):
    """RS-1..RS-4 断言 → items[] (status: MATCH / RS-FAIL / MISSING)。"""
    meta_p = cfg['outputs']['meta']
    yaml_p = cfg['outputs'].get('test_conditions') or os.path.join(
        cfg['project_dir'], 'meta', 'test_conditions.yaml')
    meta = _read_json_rb(meta_p)
    fns = {f.get('functionName'): f for f in ((meta or {}).get('functions') or [])}
    where = 'meta-excitation-override.json:recommendedGateAssertions'
    items = []

    def add(link, status, detail, verdict):
        items.append({'group': 'RS', 'link': link, 'artifact': os.path.basename(meta_p),
                      'source': 't26 run-scope override', 'status': status,
                      'detail': detail, 'ruleRef': where, 'actual': verdict})

    if meta is None:
        add('RS-1..RS-4(前置)', 'MISSING', 'meta 缺失或无法解析 → RS 断言无法执行', None)
        return items

    # ---- RS-1: TM601 powered_pins 不得含 VBUS ----
    tm601 = fns.get('TM601_LS_RDSON')
    if tm601 is None:
        add('RS-1 VBUS 移除', 'MISSING', 'meta 缺少 TM601_LS_RDSON → 断言无法执行', None)
    else:
        pp = _caps_upper(tm601.get('capAuthority'), 'powered_pins')
        add('RS-1 VBUS 移除', 'MATCH' if 'VBUS' not in pp else RS_STATUS,
            "TM601_LS_RDSON.capAuthority.powered_pins 不含 'VBUS'"
            + ('' if 'VBUS' not in pp else ' —— 实际出现了 VBUS: %s。原因: OVERVIEW 派生层 vset[vbus] 回归 (BD-08 已排除该仿真域轨)'
               % sorted(pp)),
            sorted(pp))

    # ---- RS-2: TM600 mi_pins 含 SW; TM601 mi_pins 含 PMID_SW 与 SW ----
    tm600 = fns.get('TM600_HS_RDSON')
    need = [(tm600, 'TM600_HS_RDSON', {'SW'}), (tm601, 'TM601_LS_RDSON', {'PMID_SW', 'SW'})]
    bad = []
    actuals = {}
    for fn, name, want in need:
        if fn is None:
            bad.append('%s 缺失' % name)
            continue
        mi = _caps_upper(fn.get('capAuthority'), 'mi_pins')
        actuals[name] = sorted(mi)
        miss = sorted(want - mi)
        if miss:
            bad.append('%s.mi_pins 缺 %s (实际 %s)' % (name, miss, sorted(mi)))
    add('RS-2 mi_pins 修正', 'MATCH' if not bad else RS_STATUS,
        "TM600_HS_RDSON.mi_pins 含 'SW' 且 TM601_LS_RDSON.mi_pins 含 'PMID_SW' 与 'SW'"
        + ('' if not bad else ' —— ' + '; '.join(bad) + '。原因: 生成器从 Check 列派生时漏掉被测电流 pin; '
           '缺失会让 FR-001 反向检查重新对被测电流节点提出稳压电容要求 (K57/K5 假阳性回归)'),
        actuals)

    # ---- RS-3: hardwareInit 的 vset 集合 == 冻结 ATE, 且不含 vbus ----
    vbad = []
    vactual = {}
    for name, want in RS_ATE_VSET.items():
        fn = fns.get(name)
        if fn is None:
            vbad.append('%s 缺失' % name)
            continue
        vs = _vset_map(fn)
        vactual[name] = {k: v[0] if len(v) == 1 else v for k, v in sorted(vs.items())}
        got = {k: (v[0] if len(v) == 1 else None) for k, v in vs.items()}
        if 'vbus' in vs:
            vbad.append('%s.hardwareInit 含 vset[vbus]=%s (仿真域轨, 冻结 ATE 不含)' % (name, vs['vbus']))
        if sorted(got) != sorted(want):
            extra = sorted(set(got) - set(want))
            miss = sorted(set(want) - set(got))
            vbad.append('%s vset 轨道集合不符: 期望 %s, 实际 %s%s%s'
                        % (name, sorted(want), sorted(got),
                           (' 多余=%s' % extra) if extra else '',
                           (' 缺失=%s' % miss) if miss else ''))
        else:
            for k in sorted(want):
                if got.get(k) != want[k]:
                    vbad.append('%s vset[%s]=%s, 期望 %s' % (name, k, got.get(k), want[k]))
    add('RS-3 ATE 激励对齐', 'MATCH' if not vbad else RS_STATUS,
        'TM600 vset == vbat 4.2 / pmid 15 / bst_sw 5 / vdrv 5; TM601 vset == vbat 4.2 / pmid 9 / vdrv 5; 两者均不含 vbus'
        + ('' if not vbad else ' —— ' + '; '.join(vbad) + '。原因: 重生成会退回 OVERVIEW 仿真域值 (3.5/5), '
           '与 setup-contract 冻结 ATE 冲突'),
        vactual)

    # ---- RS-4: yaml._sync.metaSha256 == sha256(meta) ----
    y_meta_sha, _y_dft = _read_yaml_sync(yaml_p)
    meta_sha = _sha(meta_p)
    st = _cmp(y_meta_sha, meta_sha)
    add('RS-4 yaml↔meta 戳', 'MATCH' if st == 'MATCH' else RS_STATUS,
        'test_conditions.yaml _sync.metaSha256 == sha256(dali_tm_meta.json) (%s)' % st,
        {'yaml': (y_meta_sha or '')[:16], 'meta': (meta_sha or '')[:16]})

    return items


def main():
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except AttributeError:
        pass
    args = sys.argv[1:]
    as_json = '--json' in args
    cfg = proj_config.load(proj_config.config_from_argv(args))

    items = check_dft_group(cfg) + check_sch_group(cfg) + check_meta_override_rs(cfg)

    bad = [i for i in items if i['status'] != 'MATCH']
    in_sync = not bad

    if as_json:
        print(json.dumps({'inSync': in_sync, 'items': items}, ensure_ascii=False, indent=2))
        return 0 if in_sync else 1

    print('=' * 72)
    print('INPUT SYNC — 输入同步一致性门 (流水线之前)')
    print('=' * 72)
    cur = None
    for i in items:
        if i['group'] != cur:
            cur = i['group']
            print('\n[%s 组]  %s → 派生产物' % (cur, i['source']))
        mark = {'MATCH': 'OK  ', 'DRIFT': 'DRIFT', 'NO-STAMP': 'NOSTM',
                'MISSING': 'MISS ', RS_STATUS: 'RS-FAIL'}.get(i['status'], i['status'])
        print('  [%s] %-16s %-28s  %s' % (mark, i['link'], i['artifact'], i['detail']))

    print('\n' + '-' * 72)
    if in_sync:
        print('INPUT SYNC: **IN SYNC** — 输入与派生文件全部同版本, 无需修改任何产物。')
        print('            (可直接进 Step0/CBIT-Definition/生成循环; 跳过一切重生成)')
        print('-' * 72)
        return 0

    print('INPUT SYNC: **OUT OF SYNC** — %d 项需处理:' % len(bad))
    for i in bad:
        print('  - [%s] %s / %s  (%s)' % (i['status'], i['group'], i['artifact'], i['detail']))
    rs_bad = [i for i in bad if i['status'] == RS_STATUS]
    if rs_bad:
        print()
        print('*** NEW-RED: meta 的 run 作用域修正已被抹除 (%d 项) ***' % len(rs_bad))
        for i in rs_bad:
            print('  - [%s] %s' % (i['link'], i['detail']))
            print('      规则来源: %s' % i.get('ruleRef'))
            print('      实测值  : %s' % json.dumps(i.get('actual'), ensure_ascii=False))
        print('  ⇒ 这是"重生成静默抹除"被检出的现象, **不是**可忽略的漂移。')
        print('     处置: 不要改基线/不要放宽断言 —— 重新施加 run 作用域 meta 修正')
        print('     (见 team/artifacts/<run>/meta-excitation-override.json), 再复跑本门。')
    groups = sorted({i['group'] for i in bad})
    print('\n重生成命令:')
    if 'DFT' in groups:
        print('  # DFT 组 (先 meta 后 YAML, 顺序不可反)')
        print('  python scripts/gen_testitems_meta.py')
        print('  python scripts/gen_test_conditions.py')
    if 'RS' in groups:
        print('  # RS 组: 重生成之后**必须重放本次 run 作用域 meta 修正** (顺序不可反)')
        print('  #   1) python scripts/gen_testitems_meta.py && python scripts/gen_test_conditions.py')
        print('  #   2) 按 team/artifacts/<run>/meta-excitation-override.json 重新施加覆盖, 并复跑本门')
        print('  #   3) 覆盖与回退的判据: 该产物的 recommendedGateAssertions (RS-1..RS-4)')
    if 'SCH' in groups:
        print('  # SCH 组 (csv → 合成EDIF → map/statistic + manifest)')
        print('  python scripts/schematic_parse/scripts/run_hardware_parse.py')
    print('重新生成后复跑本门: python scripts/check_input_sync.py')
    print('-' * 72)
    return 1


if __name__ == '__main__':
    raise SystemExit(main())
