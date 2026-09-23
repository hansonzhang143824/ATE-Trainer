# -*- coding: utf-8 -*-
"""t28 patcher — 在 check_input_sync.py 中实现 RS-1..RS-4 断言（保留 BOM/LF，逐字节安全）。

用法: python t28_apply.py [--verify-only]
"""
import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
TARGET = os.path.join(WS, 'scripts', 'check_input_sync.py')

# ---------- 1) import: 增加 re ----------
IMP_OLD = 'import json\nimport os\nimport sys\n'
IMP_NEW = 'import json\nimport os\nimport re\nimport sys\n'

# ---------- 2) 在 main() 之前插入 RS 检查组 ----------
ANCHOR = 'def main():\n'
RS_BLOCK = '''# ============================================================================
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


# RS-3 期望值 = 冻结 ATE 激励 (setup-contract tmDeltas.ateStimulus / DFT.csv L90-100 经 BD-08 裁定)
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


'''

# ---------- 3) main(): 收集 RS 项 ----------
MAIN_OLD = "    items = check_dft_group(cfg) + check_sch_group(cfg)\n"
MAIN_NEW = "    items = check_dft_group(cfg) + check_sch_group(cfg) + check_meta_override_rs(cfg)\n"

# ---------- 4) main(): 文本渲染的 status mark ----------
MARK_OLD = "        mark = {'MATCH': 'OK  ', 'DRIFT': 'DRIFT', 'NO-STAMP': 'NOSTM', 'MISSING': 'MISS '}[i['status']]\n"
MARK_NEW = "        mark = {'MATCH': 'OK  ', 'DRIFT': 'DRIFT', 'NO-STAMP': 'NOSTM',\n                'MISSING': 'MISS ', RS_STATUS: 'RS-FAIL'}.get(i['status'], i['status'])\n"

# ---------- 5) main(): 失败摘要区分 RS-FAIL (明确"新增红") ----------
BAD_OLD = """    print('INPUT SYNC: **OUT OF SYNC** — %d 项需处理:' % len(bad))
    for i in bad:
        print('  - [%s] %s / %s  (%s)' % (i['status'], i['group'], i['artifact'], i['detail']))
    groups = sorted({i['group'] for i in bad})
"""
BAD_NEW = """    print('INPUT SYNC: **OUT OF SYNC** — %d 项需处理:' % len(bad))
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
"""
GROUPS_OLD = """    if 'DFT' in groups:
        print('  # DFT 组 (先 meta 后 YAML, 顺序不可反)')
        print('  python scripts/gen_testitems_meta.py')
        print('  python scripts/gen_test_conditions.py')
"""
GROUPS_NEW = """    if 'DFT' in groups:
        print('  # DFT 组 (先 meta 后 YAML, 顺序不可反)')
        print('  python scripts/gen_testitems_meta.py')
        print('  python scripts/gen_test_conditions.py')
    if 'RS' in groups:
        print('  # RS 组: 重生成之后**必须重放本次 run 作用域 meta 修正** (顺序不可反)')
        print('  #   1) python scripts/gen_testitems_meta.py && python scripts/gen_test_conditions.py')
        print('  #   2) 按 team/artifacts/<run>/meta-excitation-override.json 重新施加覆盖, 并复跑本门')
        print('  #   3) 覆盖与回退的判据: 该产物的 recommendedGateAssertions (RS-1..RS-4)')
"""

PAIRS = [('import', IMP_OLD, IMP_NEW),
         ('rs-block', ANCHOR, RS_BLOCK + ANCHOR),
         ('main-collect', MAIN_OLD, MAIN_NEW),
         ('mark', MARK_OLD, MARK_NEW),
         ('bad-summary', BAD_OLD, BAD_NEW),
         ('regen-cmds', GROUPS_OLD, GROUPS_NEW)]


def main():
    raw = open(TARGET, 'rb').read()
    bom = raw[:3] == b'\xef\xbb\xbf'
    t = raw.decode('utf-8-sig')
    if '--verify-only' in sys.argv:
        for name, old, _new in PAIRS:
            print('  %-14s 命中 %d 次' % (name, t.count(old)))
        return
    for name, old, new in PAIRS:
        n = t.count(old)
        if n != 1:
            raise SystemExit('ERROR: %s 命中 %d 次 (应 1)' % (name, n))
        t = t.replace(old, new)
    out = t.encode('utf-8')
    if bom:
        out = b'\xef\xbb\xbf' + out
    with open(TARGET, 'wb') as f:
        f.write(out)
    print('PATCHED %s\n  before=%s (%d B)\n  after =%s (%d B)\n  bom=%s lf=%d crlf=%d'
          % (TARGET, hashlib.sha256(raw).hexdigest(), len(raw), hashlib.sha256(out).hexdigest(),
             len(out), bom, out.count(b'\n') - out.count(b'\r\n'), out.count(b'\r\n')))


if __name__ == '__main__':
    main()
