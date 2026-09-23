# -*- coding: utf-8 -*-
"""在生成器里为 form1 的 guardrail 补"欠严"注记（幂等，防再被重写丢掉）。"""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.join(HERE, 't54_make_report.py')
t = io.open(GEN, encoding='utf-8-sig').read()

OLD = "'guardrail': '先测展开器再信展开；判\"宏闭了哪些 K\"用 StdAfx.h 原文逐字展开'},"
NEW = ("'guardrail': '先测展开器再信展开；判\"宏闭了哪些 K\"用 StdAfx.h 原文逐字展开。"
       "另：该门的成员性检查（L401/L403）对多值宏只覆盖首值 ⇒ **欠严（under-strict）**，"
       "不得作为\"多值宏逐条校验\"的证据。'},")

if "'guardrail'" not in t:
    print('ERROR: 未找到 guardrail 锚点')
elif '欠严（under-strict）' in t and NEW[:40] in t:
    print('已补（幂等）: %d B' % os.path.getsize(GEN))
elif OLD in t:
    io.open(GEN, 'w', encoding='utf-8', newline='').write(t.replace(OLD, NEW, 1))
    print('已补: %d B' % os.path.getsize(GEN))
else:
    # 打印实际内容以便定位
    i = t.find("'guardrail'")
    print('锚点不匹配，实际内容 =', repr(t[i:i + 260]))
