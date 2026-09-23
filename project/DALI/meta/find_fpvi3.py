# -*- coding: utf-8 -*-
"""提取工厂 Test_Method.cpp 的 fpvi_gp_valid 实现体"""
import io, re

f = r'D:\Newtest\CLAUDE_PROCESS\Library-Functions\Test_Method\Test_Method.cpp'
t = io.open(f, encoding='utf-8-sig', errors='ignore').read()

# 找定义体: BOOL fpvi_gp_valid(int gp_no) 或类似
m = re.search(r'(?:BOOL|int|bool)\s+fpvi_gp_valid\s*\([^)]*\)\s*\{', t)
if m:
    seg = t[m.start():]
    # 提取到函数结束 (花括号平衡)
    depth = 0; end = 0
    for i, ch in enumerate(seg):
        if ch == '{': depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    print(seg[:end])
    print("===== 函数长度: %d 字符 =====" % end)
else:
    print("工厂 Test_Method.cpp 未找到 fpvi_gp_valid 定义体")

# 也看调用上下文 (ramp 里怎么用)
print()
print("===== 调用上下文 (Test_Method.cpp) =====")
for m2 in re.finditer(r'if \(!fpvi_gp_valid\(gp_no\)\)\s*\{', t):
    s = m2.start()
    print(t[s-200:s+200].replace('\n', ' \n '))
    print('-----')
