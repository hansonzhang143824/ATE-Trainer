# -*- coding: utf-8 -*-
"""查找 fpvi_gp_valid 的实现 (定义体)"""
import io, os, re

def find_impl(files):
    for f in files:
        try:
            t = io.open(f, encoding='utf-8-sig', errors='ignore').read()
        except Exception:
            continue
        for m in re.finditer(r'^.*fpvi_gp_valid\s*\([^;]*\)\s*\n?\s*\{', t, re.M):
            start = m.start()
            # 提取定义体 (找到函数名行到方法结束)
            seg = t[start:start + 1500]
            return f, seg.split('\n')[0].strip()[:130], seg
    return None

print("=== DALI sub.cpp 是否有 fpvi_gp_valid 定义体 ===")
r = find_impl([r'D:\PROJECT6-DALI\devel\source\sub.cpp'])
if r:
    print("  找到: %s" % r[0]); print("  ", r[1])
else:
    print("  [缺失] DALI sub.cpp 无 fpvi_gp_valid 实现")

print()
print("=== 工厂 D:\\Newtest\\CLAUDE_PROCESS\\Library-Functions\\test_method 相关文件 ===")
for f in [r'D:\Newtest\CLAUDE_PROCESS\Library-Functions\Test_Method\sub.cpp', r'D:\Newtest\CLAUDE_PROCESS\Library-Functions\Test_Method\sub.h', r'D:\Newtest\CLAUDE_PROCESS\Library-Functions\Test_Method\Test_Method.cpp']:
    if not os.path.exists(f):
        print("  不存在:", f); continue
    try:
        t = io.open(f, encoding='utf-8-sig', errors='ignore').read()
    except Exception:
        print("  读失败:", f); continue
    impl = re.search(r'fpvi_gp_valid\s*\([^;]*\)\s*\n?\s*\{', t)
    decl = re.search(r'fpvi_gp_valid\s*\([^;]*\)\s*;', t)
    print("  %s: 实现=%s 声明=%s" % (os.path.basename(f), bool(impl), bool(decl)))

print()
print("=== 工厂 fpvi_gp_valid 实现体 (从 sub.cpp 提取) ===")
try:
    t = io.open(r'D:\Newtest\CLAUDE_PROCESS\Library-Functions\Test_Method\sub.cpp', encoding='utf-8-sig', errors='ignore').read()
    m = re.search(r'(?:BOOL|int|bool)\s+fpvi_gp_valid\s*\([^)]*\)\s*\{', t)
    if m:
        print(t[m.start():m.start() + 1200])
    else:
        print("  工厂 sub.cpp 无实现体 (可能在其他文件)")
except Exception as e:
    print("  错误:", e)
