# -*- coding: utf-8 -*-
# check_testitems_meta.py — TestItemMeta 校验器 (收尾证据检验, 只报红不产出)
#
# 职责: 覆盖完整性门。依赖 gen_testitems_meta.py 已生成 meta json (证据)。
#   --require-all          正向门: 每个 test.cpp 函数必须在 meta json 中有记录 (缺 meta → FAIL)
#   --require-scope <批次>  反向门: 范围内 OVERVIEW isCodeGen=Y 项必须已写入 test.cpp (漏写 → FAIL)
#                           + 范围内 test.cpp 函数必须有 meta (缺 meta → FAIL)
# 判定: 任一 FAIL → exit 1; 全部 PASS → exit 0
#
# 路径约定: 默认读 project_config.json (--config 可覆盖), --* 参数可单独覆盖。
#
# 用法:
#   python check_testitems_meta.py --require-all
#   python check_testitems_meta.py --require-scope 403-425
#   默认: --src=derived.test_cpp --meta=outputs.meta --xlsx=inputs.dft
#   python check_testitems_meta.py ... --require-all --require-scope 403-425
#
# 关系: gen_testitems_meta.py (生成 meta) → 本脚本 (收尾校验)。先 gen 后 check。

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
    """OVERVIEW → {Item: row}"""
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


# Trim 函数名 → OVERVIEW Item 编号 (与 gen_testitems_meta.py 一致)
TRIM_ITEM_MAP = {
    'Trim_IZTC_RES':   '133',
    'Trim_BG_RES_DIV': '135',
    'Trim_VBG':        '139',
}


def load_testcpp_fns(src):
    """test.cpp -> {Item编号: 函数名}"""
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


def parse_scope(s):
    """'--require-scope' 参数解析: '403,406,408-425' → {'403','406','408',...}
    支持逗号分隔 + 'a-b' 范围; 'TM' 前缀自动剥离"""
    out = set()
    for part in s.split(','):
        part = part.strip().lstrip('TM')
        if '-' in part:
            a, b = part.split('-', 1)
            a, b = int(a), int(b)
            if b < a:
                raise ValueError(f'scope 范围错误: {a}-{b}')
            out.update(str(i) for i in range(a, b + 1))
        elif part:
            out.add(part)
    return out


def load_meta(meta_path):
    """meta json → {dftItem} (dftItem = 'TM133' 带前缀)"""
    with open(meta_path, encoding='utf-8') as f:
        data = json.load(f)
    return {fn['dftItem'] for fn in data.get('functions', []) if fn.get('dftItem')}


def main():
    cfg = proj_config.load(proj_config.config_from_argv(sys.argv))
    ap = argparse.ArgumentParser(description='TestItemMeta 校验器 (收尾证据检验)')
    ap.add_argument('--config', default=None, help='project_config.json (默认 workspace 根)')
    ap.add_argument('--xlsx', default=cfg['inputs']['dft'], help='OVERVIEW 源 xlsx (--require-scope 时必填)')
    ap.add_argument('--src', default=cfg['derived']['test_cpp'], help='test.cpp 路径 (函数名单)')
    ap.add_argument('--meta', default=cfg['outputs']['meta'], help='已生成的 meta json 路径')
    ap.add_argument('--require-all', action='store_true',
                    help='正向门: 每个 test.cpp 函数必须有 meta')
    ap.add_argument('--require-scope', default=None,
                    help='反向门: 范围内 OVERVIEW isCodeGen=Y 项必须已写入 test.cpp')
    args = ap.parse_args()

    if not args.require_all and not args.require_scope:
        ap.error('至少指定 --require-all 或 --require-scope')
    if args.require_scope and not args.xlsx:
        ap.error('--require-scope 需要 --xlsx')

    if not os.path.exists(args.meta):
        print(f'*** FAIL: meta 文件不存在 {args.meta} — 先跑 gen_testitems_meta.py 生成')
        sys.exit(1)
    meta_items = load_meta(args.meta)
    fns = load_testcpp_fns(args.src)

    errors = 0

    if args.require_all:
        missing = sorted(((item, name) for item, name in fns.items()
                          if 'TM' + item not in meta_items),
                         key=lambda t: [int(p) for p in t[0].split('_')])
        if missing:
            print('*** FAIL (--require-all) *** test.cpp 函数缺 meta 记录:')
            for item, name in missing:
                print(f'  - {item} {name}: 无 meta → 补 OVERVIEW 后重跑 gen_testitems_meta.py')
            errors += 1
        else:
            print(f'[ok] --require-all: meta 全覆盖 {len(fns)}/{len(fns)} 函数 PASS')

    if args.require_scope:
        scope = parse_scope(args.require_scope)
        ov = load_overview(args.xlsx)
        scope_items = set()
        for item in sorted(scope, key=lambda x: [int(p) for p in x.split('_')]):
            row = ov.get('TM' + item)
            if row and str(row.get('isCodeGen', '')).strip() == 'Y':
                scope_items.add(item)
        not_written = sorted(scope_items - set(fns),
                             key=lambda x: [int(p) for p in x.split('_')])
        if not_written:
            print('*** FAIL (--require-scope) *** OVERVIEW isCodeGen=Y 但 test.cpp 未写入:')
            for item in not_written:
                name = ov.get('TM' + item, {}).get('Name', '')
                print(f'  - TM{item} {name}: OVERVIEW 标记应生成, test.cpp 无 DUT_API 函数')
            errors += 1
        written = sorted(set(fns) & scope, key=lambda x: [int(p) for p in x.split('_')])
        no_meta = [item for item in written if 'TM' + item not in meta_items]
        if no_meta:
            print(f'*** FAIL (--require-scope) *** 批次内函数缺 meta: {no_meta}')
            errors += 1
        if not not_written and not no_meta:
            print(f'[ok] --require-scope: 批次 isCodeGen=Y 项 {len(scope_items)} 全写入 '
                  f'+ {len(written)} 个函数全有 meta PASS')

    if errors:
        print(f'\n*** FAIL (check_testitems_meta) *** {errors} 项门禁不通过')
        sys.exit(1)
    print('\nCHECK-TESTITEMS-META PASSED')


if __name__ == '__main__':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    main()
