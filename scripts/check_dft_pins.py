# -*- coding: utf-8 -*-
"""
check_dft_pins.py — DFT pin 交叉校验（Step1 新增门，2026-08-27 用户拍板）

架构（Step0/Step1 交换后）:
  Step0 原理图解析 → SCH-Connect-Map + Component-Statistic（全局产物，有货先验）
  Step1 DFT 解析   → meta/YAML + 本脚本交叉校验：DFT 引用的 pin 必须能落到原理图
                     词汇（三源三层），三源都未命中 → 收集问题清单 → 问用户。

三层判定（三源合并，命中任一即放行）:
  L1 DUT pad/源表对象 : ∈ SCH-Connect-Map 全部大写 token（物理 pad + 源表对象 + 继电器）
  L2 测试 pad 角色    : ∈ {ATEST0, ATEST1, DTEST0}（DFT 标准测试 pad 角色名，
                        agent 按黄金解析到物理 pad/源表，如 DTEST0→nQON 读 DTEST0 逻辑电平）
  L3 路径/组合节点抽象: ∈ {BST_SW, PGND_SW, PMID_SW}（DFT 组合节点名，relay 层解析为
                        物理 pad 组合 + 继电器；原理图里 BST/SW、PGND/SW、PMID/SW 是分离 pad）
  L2/L3 出现新角色名 → agent 按黄金补（误报方向安全：宁多问，不漏错）

收集的 DFT pin: hardwareInit 的 vset/iset pin + params 的 checkPin/pin。

用法: python check_dft_pins.py [--meta <json>] [--map <txt>] [--json] [--dump-vocab]
  --json       输出 JSON 报告（供下游/agent）
  --dump-vocab 打印三源词汇表规模后退出
  退出码: 0 = 全部命中（通过）; 1 = 存在未命中（问题清单，需问用户）
"""
import json
import io
import os
from schematic_projection import read_schematic_text
import json
import re
import sys

_BASE = os.path.dirname(os.path.abspath(__file__))
_DEF_META = os.path.join(_BASE, 'Project', 'DALI', 'meta', 'dali_tm_meta.json')
_DEF_MAP = os.path.join(_BASE, json.load(open(os.path.join(_BASE, 'project_config.json'), encoding='utf-8-sig'))['intermediates']['sch_connect_map'])

# L2 测试 pad 角色（DFT 侧标准 pad，agent 按黄金补物理 pad/源表映射；新增需附黄金证据）
TEST_PAD_ROLES = ('ATEST0', 'ATEST1', 'DTEST0')

# L3 路径/组合节点抽象（DFT 组合节点，relay 层解析为物理 pad 组合；新增同理需附证据）
PATH_ABSTRACT_ROLES = ('BST_SW', 'PGND_SW', 'PMID_SW')


def read_enc(path):
    """rb 读(DLP 白名单解密) + 编码回退解码。"""
    with open(path, 'rb') as f:
        raw = f.read()
    for enc in ('utf-8-sig', 'utf-8', 'gbk', 'latin-1'):
        try:
            return raw.decode(enc)
        except (UnicodeDecodeError, ValueError):
            continue
    return raw.decode('utf-8', errors='replace')


def build_l1_vocab(map_text):
    """L1: SCH-Connect-Map 全部大写 token（物理 pad + 源表对象 + 继电器名，宽松超集）。
    另取每个 token 的下划线词干（pad→channel 后缀惯例: INT_PA0 词干 = INT pad）；
    拼写错误不会命中（如 VBA 不是任何 token 词干）。"""
    toks = set(re.findall(r'\b[A-Z][A-Z0-9_]+\b', map_text))
    stems = {t.split('_')[0] for t in toks if '_' in t}
    return toks, stems


def collect_dft_pins(meta):
    """逐 TM 收集 DFT pin → {pin: {tm, via}}；via 标注来源类别（vset/iset/checkPin/pin）。"""
    pins = {}
    for fn in meta['functions']:
        name = fn['functionName']
        def add(p, via):
            if not p:
                return
            p = str(p).strip().upper()
            rec = pins.setdefault(p, {'tms': [], 'via': set()})
            rec['tms'].append(name)
            rec['via'].add(via)
        for c in fn.get('hardwareInit', []):
            if c.get('cmd') in ('vset', 'iset'):
                add(c.get('pin'), c.get('cmd'))
        for pr in fn.get('params', []):
            add(pr.get('checkPin'), 'checkPin')
            add(pr.get('pin'), 'pin')
    return pins


def resolve(pin, l1, l1_stems, l2, l3):
    """三层判定：返回 (level, ok)。"""
    if pin in l1:
        return 'L1(原理图)', True
    if pin in l1_stems:
        return 'L1b(原理图带后缀)', True
    if pin in l2:
        return 'L2(测试pad角色)', True
    if pin in l3:
        return 'L3(组合节点抽象)', True
    return 'UNRESOLVED', False


def main(argv):
    out_json = False
    dump_vocab = False
    meta_path = _DEF_META
    map_path = _DEF_MAP
    for i, a in enumerate(argv):
        if a == '--json':
            out_json = True
        elif a == '--dump-vocab':
            dump_vocab = True
        elif a == '--meta' and i + 1 < len(argv):
            meta_path = argv[i + 1]
        elif a == '--map' and i + 1 < len(argv):
            map_path = argv[i + 1]

    l1, l1_stems = build_l1_vocab(read_enc(map_path))
    l2 = set(TEST_PAD_ROLES)
    l3 = set(PATH_ABSTRACT_ROLES)
    if dump_vocab:
        print('L1(SCH-Connect-Map token)=%d  L1b(带后缀词干)=%d  L2(测试pad角色)=%s  L3(组合节点)=%s'
              % (len(l1), len(l1_stems), ','.join(sorted(l2)), ','.join(sorted(l3))))
        return 0

    meta = json.loads(read_enc(meta_path))
    pins = collect_dft_pins(meta)

    rows = []
    unresolved = []
    for pin, rec in sorted(pins.items()):
        lv, ok = resolve(pin, l1, l1_stems, l2, l3)
        rows.append({'pin': pin, 'level': lv, 'ok': ok, 'tms': rec['tms'], 'via': sorted(rec['via'])})
        if not ok:
            unresolved.append(rows[-1])

    if out_json:
        print(json.dumps({'total_tms': len(meta['functions']),
                          'total_pins': len(pins),
                          'unresolved': unresolved}, ensure_ascii=False, indent=2))
    else:
        print('DFT pin 交叉校验: %d TM, %d 唯一 pin' % (len(meta['functions']), len(pins)))
        print('  命中: %d | 未命中: %d' % (len(rows) - len(unresolved), len(unresolved)))
        for r in rows:
            flag = 'OK ' if r['ok'] else '?? '
            print('  %s %-10s %-12s (via %s)' % (flag, r['pin'], r['level'], ','.join(r['via'])))
        if unresolved:
            print('\n[未命中] 需问用户（可能: DFT 拼写错误 / 原理图漏 pad / 新角色名 agent 补）:')
            for r in unresolved:
                print('  %s <- %s' % (r['pin'], ','.join(r['tms'][:6])))

    return 1 if unresolved else 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
