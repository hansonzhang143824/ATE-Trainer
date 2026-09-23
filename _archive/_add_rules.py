# -*- coding: utf-8 -*-
"""注册两条 ACM 硬件事实规则到 rules-registry.md draft 区（DLP 字节模式）"""
import io

P = '.claude/knowledge/standards/rules-registry.md'
raw = open(P, 'rb').read()
text = raw.decode('utf-8')

new_rows = (
    "| R-ACM-01 | global (功能规则) | **ACM 无法同时测压测流**（其余源表均可）: ACM 单板 24 通道，硬件手册概述明确\"无法同时测压测流\"，必须分步测（先测电压再测电流或反之） | 所有项目 (ACM 卡) | check-agent (人工; ACM 未用本项目) | 2026-08-30 | 硬件手册 Rev2.13 p78-80 |\n"
    "| R-ACM-02 | global (功能规则) | **ACM 大小电流量程切换先断输出继电器**: 大电流量程(±500mA/±200mA/±20mA)与小电流量程(±2mA/±200μA/±20μA/±5μA)间切换时，硬件会先断开输出继电器→切量程→再接通；编程侧避免依赖切换瞬间的输出连续 | 所有项目 (ACM 卡) | check-agent (人工) | 2026-08-30 | 硬件手册 Rev2.13 p78-80 |"
)

old_empty = "| _(空)_ | | | | |"
assert old_empty in text, "draft 空行未找到"
text = text.replace(old_empty, new_rows, 1)

out = text.encode('utf-8')
open(P, 'wb').write(out)
print("OK written, size", len(raw), "->", len(out))
