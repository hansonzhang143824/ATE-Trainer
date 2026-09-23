# -*- coding: utf-8 -*-
"""抽检 t30-summary.md 更正后的关键表述是否到位（只读）。"""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(HERE, 't30-summary.md')
t = io.open(P, encoding='utf-8-sig').read()
checks = [
    ('双列表述(payload/部署态)', '仅漏闭'),
    ('部署态实际集合', '`[13,57,60,61,83,85,126]`'),
    ('payload 实际集合', '`[13,57,60,61,83,85,109,110,126]`'),
    ('两口径转绿表 rev24', 'rev 24（现状，pin-18 口径）'),
    ('两口径转绿表 rev25', 'rev 25（`t42`/`t44` 判 ch5 后'),
    ('第二处真缺陷定性', '第二处真缺陷'),
    ('不得动基线', '不得改动 `gate_baseline.json`'),
    ('前提已判 ch5', '前提已判（`t42` + `t44`）'),
    ('行为层最强证据', '已执行'),
    ('降级复合宏', '1 定义 / 0 调用点'),
    ('ACCEPT 边界保留', '不覆盖"pin 归属前提"的正确性'),
    ('引脚标注保留(不改)', 'K110.4(NC)'),
]
print('抽检 t30-summary.md（%d B）：' % os.path.getsize(P))
for label, key in checks:
    print('  %-28s %s' % (label, '✓' if key in t else '✗ 缺失'))
