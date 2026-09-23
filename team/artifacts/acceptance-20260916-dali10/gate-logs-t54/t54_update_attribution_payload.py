# -*- coding: utf-8 -*-
"""更新 t33-revision-attribution.md：payload 版本前进（39,457 → 43,806）+ postReplace 改单口径 GREEN。幂等。"""
import hashlib
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ATTR = os.path.abspath(os.path.join(HERE, '..', 'gate-logs-t33', 't33-revision-attribution.md'))
MARK = '### 1.1 payload 版本前进（2026-09-16 晚）'


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


t = io.open(ATTR, encoding='utf-8-sig').read()
print('BEFORE: %d B' % os.path.getsize(ATTR))
if MARK in t:
    print('已更新（幂等）: %d B' % os.path.getsize(ATTR))
    raise SystemExit(0)

ADD = '''

''' + MARK + '''

| 角色 | 对象 | 现刻现算 | 状态 |
| --- | --- | --- | --- |
| DEPLOYED | `D:/PROJECT6-DALI/ForCodexDebug/source/test.cpp` | 469,714 B / `15c7d2b8…` | **未落盘**（TM600 = `{13,57,60,61,83,85,126}` ⇒ 缺 `[48,76]`） |
| DELIVERED（**现盘**） | `implementation-payload-TM600-TM601.cpp` | **43,806 B / `66abc088…`** | **已合规**（TM600 SetOn `L264` = `{13,48,57,60,61,76,83,85,126}` ⊇ 期望） |
| ~~旧交付件~~ | 同文件的历史版本 | ~~39,457 B / `2d0984d9…`~~、~~38,147 B / `272667f3…`~~ | **已被取代**，仅供溯源 |

⚠️ 本文 §1 与 §2 里以 **`39,457 / 2d0984d9…` 为"现盘/DELIVERED"** 的表述，一律改读为"**旧版、已被取代**"；
**现盘交付件是 `43,806 B / `66abc088…``**（引用前请现算）。

### 1.2 `postReplaceExpectation` 更正为**单口径 GREEN**（rule-reviewer 指出，我现算确认）

**原因**：我原先写的两口径表是拿**旧 payload（39,457）**算的 —— 那版**只闭 `[110,61]`、不含 `[48,76]`**，
故在 ch5 口径下必然仍红。**现盘 payload 已闭 `[48,60,61,76]`** ⇒ 两口径下都不缺：

| 契约口径 | 部署态（缺） | 旧 payload 39,457 | **现盘 payload 43,806** |
| --- | --- | --- | --- |
| rev 24（`[110,61]`） | 缺 `110` | 不缺 → 换版 GREEN | 不缺 → **GREEN** |
| rev 25/30+（`[48,76]`+`[60,61]`） | 缺 `48/76` | **缺 `48/76` → 仍红** | 不缺 → **GREEN** |

⇒ **`postReplaceExpectation` = "换版到现盘 payload ⇒ `bst-sw` 转 GREEN（单口径，其余 11 门不变）"**。

### 1.3 三口径归因（保留"真缺陷"但不合并）

| 对象 | 判定 | 性质 |
| --- | --- | --- |
| **部署态（现役 t23）** | `[13,57,60,61,83,85,126]` ⇒ **缺 `48/76`** | **真缺陷 + 活危害**：TM600 在驱动 ch5 仪器而 `K48` 未闭 ⇒ 源被改道至 `SW1_F`/`SW2_F` |
| ~~旧 payload 39,457~~ | 闭 `109/110`、缺 `48/76` | **闭错 + 缺闭**（历史） |
| **现盘 payload 43,806** | `{13,48,57,60,61,76,83,85,126}` ⊇ 期望 | **已合规**（落盘后预期 GREEN） |

⇒ **三口径不得合并记账**；"第二处真缺陷"只存在于**部署态**，**不属现盘 payload**。
'''

io.open(ATTR, 'w', encoding='utf-8', newline='').write(t.rstrip() + ADD)
t2 = io.open(ATTR, encoding='utf-8-sig').read()
print('AFTER : %d B / %s' % (os.path.getsize(ATTR), sha(ATTR)))
for k in (MARK, '单口径 GREEN', '三口径归因', '旧版、已被取代'):
    print('  含 %-20s %s' % (k, k in t2))
