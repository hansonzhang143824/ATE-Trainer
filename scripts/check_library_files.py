# -*- coding: utf-8 -*-
"""
check_library_files.py — 工程完整性门 (Step0 之前必跑, 2026-08-29 用户部署)

检查用户提供的项目工程里 Library Function 文件是否齐全:
  .h : inireader / BoardCheck / tempchar / treg / Test_Method / spec / FMEA
  .cpp: inireader / BoardCheck / tempchar / treg / Test_Method / spec / FMEA / test / sub
任一缺失 → 反馈「缺失 Library Function」并列出具体文件, 退出码 1。
检查 .treg 文件(vs_src_dir 内或上一级) → 缺失 → 反馈「缺失 setup 函数(.treg)」, 退出码 1。
全部存在 → PASS, 退出码 0。

用法: python check_library_files.py [--config <project_config.json>]
"""
import argparse
import glob
import os
import sys

import proj_config

# Library Function 清单 (vs_src_dir 下, 大小写不敏感匹配)
LIBRARY_FILES = [
    'inireader.h', 'BoardCheck.h', 'tempchar.h', 'treg.h', 'Test_Method.h', 'spec.h', 'FMEA.h',
    'inireader.cpp', 'BoardCheck.cpp', 'tempchar.cpp', 'treg.cpp', 'Test_Method.cpp',
    'spec.cpp', 'FMEA.cpp', 'test.cpp', 'sub.cpp',
]


def find_file(directory, name):
    """大小写不敏感找文件 → 实际文件名 / None"""
    target = name.lower()
    try:
        for f in os.listdir(directory):
            if f.lower() == target and os.path.isfile(os.path.join(directory, f)):
                return f
    except OSError:
        pass
    return None


def main():
    cfg = proj_config.load(proj_config.config_from_argv(sys.argv))
    ap = argparse.ArgumentParser(description='工程完整性门: Library Function + .treg 存在性检查')
    ap.add_argument('--config', default=None, help='project_config.json 路径')
    args = ap.parse_args()

    vs = cfg['inputs'].get('vs_src_dir', '')
    src_dir = vs if os.path.isabs(vs) else os.path.join(cfg['_root'], vs)
    if not os.path.isdir(src_dir):
        print('*** FAIL *** 工程源目录不存在: %s' % src_dir)
        sys.exit(1)

    print('-- 工程完整性门: %s' % src_dir)

    # ---- Library Function 16 文件 ----
    missing = []
    for name in LIBRARY_FILES:
        actual = find_file(src_dir, name)
        if actual:
            print('  [OK]  %s' % actual)
        else:
            missing.append(name)
            print('  [MISS] %s' % name)

    # ---- .treg (source 内或上一级, 任意名 *.treg — 换项目名字可变) ----
    treg_hits = glob.glob(os.path.join(src_dir, '*.treg')) + \
                glob.glob(os.path.join(os.path.dirname(src_dir), '*.treg'))
    if treg_hits:
        for h in treg_hits:
            print('  [OK]  %s' % os.path.basename(h))
        treg_ok = True
    else:
        treg_ok = False

    # ---- 结论 ----
    if missing:
        print('*** FAIL *** 缺失 Library Function (%d 个): %s' % (len(missing), ', '.join(missing)))
        sys.exit(1)
    if not treg_ok:
        print('*** FAIL *** 缺失 setup 函数 (.treg 文件不存在于 %s 或其上一级)' % src_dir)
        sys.exit(1)
    print('-- PASS: Library Function %d/%d + .treg 全部就位, 可进入 Step0' % (len(LIBRARY_FILES), len(LIBRARY_FILES)))
    sys.exit(0)


if __name__ == '__main__':
    main()
