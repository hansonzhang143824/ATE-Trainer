# -*- coding: utf-8 -*-
"""依实际措辞更正"relay-trace 不受影响"→"欠严（under-strict）"（幂等，逐文件精确定位）。"""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.abspath(os.path.join(HERE, '..'))

CORE = ('**部分/欠严（under-strict）**：`cap_defs` 只收录 Cap 家族（多值宏 = 0）⇒ '
        '**Cap 别名↔规范名映射这条路不受影响**（我原判这条成立）；'
        '但 `n = defines[r]` 在 **L401 `if n in on_set` / L403 `if n in nc_set`** 被**当数字使用**，'
        '而 `r` 来自 `parse_setons()`（**原样取 SetOn 实参、不做宏展开**）⇒ '
        '当 SetOn 写**多值宏名**时**只校验其首值那一个继电器**'
        '（例 `K_FPVIH_TO_PGND_A=154,155` ⇒ 只校验 154；`K_FPVIH_TO_BST_A=46,48,76` ⇒ 只校验 46）。'
        '⇒ 故它**不是假通过**，但**不能作为"多值宏逐条校验"的证据**。')

targets = [
    (os.path.join(RUN, 'gate-logs-t54', 't54-gate-failopen-forms.md'),
     '| **是否影响本 run 判据** | **否** ——', '| **是否影响本 run 判据** | ' + CORE + ' 原判词（保留留痕）：「**否** ——'),
    (os.path.join(RUN, 'gate-logs-t54', 't54_verify_failopen.py'),
     "'我复核 ✓（且证明 relay-trace 判据只消费 Cap 家族=单值宏 ⇒ 其 PASS 不受影响）'),",
     "'我复核 ✓（Cap 映射路径不受影响；**但 L401/L403 对多值宏只校验首值 ⇒ 欠严**，非「不受影响」）'),"),
    (os.path.join(RUN, 'gate-logs-t54', 't54-failopen-verify.log'),
     '复核：我复核 ✓（且证明 relay-trace 判据只消费 Cap 家族=单值宏 ⇒ 其 PASS 不受影响）',
     '复核：我复核 ✓（Cap 映射路径不受影响；**但 L401/L403 对多值宏只校验首值 ⇒ 欠严**，已更正原"不受影响"表述）'),
]

for path, old, new in targets:
    if not os.path.isfile(path):
        print('  MISSING %s' % os.path.basename(path))
        continue
    t = io.open(path, encoding='utf-8-sig', errors='replace').read()
    if new[:24] in t:
        print('  已更正（幂等） %s' % os.path.basename(path))
        continue
    if old not in t:
        print('  未命中 %s' % os.path.basename(path))
        continue
    io.open(path, 'w', encoding='utf-8', newline='').write(t.replace(old, new, 1))
    print('  已更正 %-34s %d B' % (os.path.basename(path), os.path.getsize(path)))

print('\n=== 抽查 fail-open 记录现文 ===')
p = os.path.join(RUN, 'gate-logs-t54', 't54-gate-failopen-forms.md')
if os.path.isfile(p):
    for i, l in enumerate(io.open(p, encoding='utf-8-sig').read().splitlines(), 1):
        if '是否影响本 run 判据' in l:
            print('  L%-4d %s' % (i, l.strip()[:200]))
