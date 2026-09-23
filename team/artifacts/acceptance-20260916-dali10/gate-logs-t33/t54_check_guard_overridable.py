# -*- coding: utf-8 -*-
"""查证 guard 的目标路径来源与 CLI 参数（决定 t54 能否对"候选 payload"出绿）。"""
import io
import re

SRC = 'scripts/verify_bst_sw_sequence.py'
src = io.open(SRC, encoding='utf-8-sig').read()

print('=== 参数列表 ===')
print('  ', sorted(set(re.findall(r"'(--[a-z][a-z-]+)'", src))))
print('  含 --test-cpp :', '--test-cpp' in src)
print('  含 --src      :', '--src' in src)

print('\n=== test.cpp / test_cpp 相关行 ===')
for i, l in enumerate(src.splitlines(), 1):
    if 'test.cpp' in l or 'test_cpp' in l or 'derived' in l:
        print('  L%-4d %s' % (i, l.strip()[:150]))

print('\n=== target 是怎么取到的（看 main 附近）===')
i = src.find('def main')
print(src[i:i + 1200])
