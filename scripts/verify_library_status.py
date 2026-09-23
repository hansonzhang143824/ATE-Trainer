# -*- coding: utf-8 -*-
"""verify_library_status.py — 阻止含 TODO/恒成功桩函数的共享库进入正式 VS 工程。

桩检测 (stub_methods) 与生产工程引用 (vs_src_dir 下源码) 两层联动:
  - 生产工程 #include "sub_func.h" 或引用 Sub_Func 且共享库含 TODO/恒成功桩 → FAIL (列出桩方法)
  - 共享库含桩但未进生产 → 仅报告 (开发脚手架, 正常)

修自 codex 版两处缺陷 (Stage 5, 2026-08-23):
  1. 去 project_manifest 依赖 → 本地 production_sources 枚举 vs_src_dir (CLAUDE 无该模块)
  2. stub_methods 结果从「只 print」改为「驱动 FAIL 诊断」: 生产引用时桩方法名进入 errors

规则源: Library-Functions/sub_func 为跨项目子函数库脚手架, 未经实现不得进生产。
用法: python verify_library_status.py [--config <json>]
"""

from __future__ import print_function

import argparse
import os
import re
import sys

import proj_config


def read_enc(path):
    with open(path, 'rb') as stream:
        raw = stream.read()
    for encoding in ('utf-8-sig', 'utf-8', 'gbk', 'latin-1'):
        try:
            return raw.decode(encoding)
        except (UnicodeDecodeError, ValueError):
            pass
    return raw.decode('utf-8', errors='replace')


def stub_methods(path):
    text = read_enc(path)
    methods = []
    pattern = re.compile(r'(?:BOOL|double)\s+Sub_Func::(\w+)\s*\([^)]*\)\s*\{(.*?)\}', re.S)
    for match in pattern.finditer(text):
        body = match.group(2)
        if 'TODO' in body or re.search(r'^\s*return\s+(?:TRUE|FALSE|\w+)\s*;\s*$', body, re.S):
            methods.append(match.group(1))
    return sorted(set(methods))


_SRC_EXT = {'.h', '.hpp', '.cpp', '.c'}
_SKIP_DIRS = {'backup', 'release', 'debug', '.git', '.vs', 'obj', 'bin'}


def production_sources(cfg):
    """枚举生产工程源码: vs_src_dir 下 .h/.hpp/.cpp/.c, 跳过 .bak 与构建/备份目录。"""
    vs_dir = cfg['inputs'].get('vs_src_dir', '')
    if not vs_dir or not os.path.isdir(vs_dir):
        return []
    out = []
    for root, dirs, files in os.walk(vs_dir):
        dirs[:] = [d for d in dirs if d.lower() not in _SKIP_DIRS]
        for name in files:
            if '.bak' in name.lower():
                continue
            if os.path.splitext(name)[1].lower() not in _SRC_EXT:
                continue
            out.append(os.path.join(root, name))
    return sorted(out)


def verify(cfg):
    root = cfg['_root']
    stub_cpp = os.path.join(root, 'Library-Functions', 'sub_func', 'sub_func.cpp')
    stubs = stub_methods(stub_cpp) if os.path.isfile(stub_cpp) else []
    errors = []
    referencing = []
    scanned = 0
    for path in production_sources(cfg):
        if not os.path.isfile(path):
            continue
        scanned += 1
        text = read_enc(path)
        if re.search(r'#\s*include\s*[<"]sub_func\.h[>"]', text, re.I) or re.search(r'\bSub_Func\b', text):
            referencing.append(path)
    if referencing:
        stub_desc = ', '.join(stubs) if stubs else '(无 TODO 桩)'
        errors.append('正式工程引用未发布 sub_func 库 [桩方法: %s]: %s'
                      % (stub_desc, ', '.join(referencing)))
    return stubs, scanned, errors


def main(argv=None):
    parser = argparse.ArgumentParser(description='检查未发布/TODO 共享函数是否进入正式工程')
    parser.add_argument('--config', default=None)
    args = parser.parse_args(argv)
    cfg = proj_config.load(args.config)
    stubs, scanned, errors = verify(cfg)
    print('[library] TODO/stub methods (%d): %s' % (len(stubs), ', '.join(stubs) if stubs else '<none>'))
    print('[library] production source files scanned: %d' % scanned)
    if errors:
        print('*** FAIL ***')
        for error in errors:
            print('  - ' + error)
        return 1
    print('LIBRARY STATUS PASSED (stub library is not in production project)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
