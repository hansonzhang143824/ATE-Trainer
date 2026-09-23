# -*- coding: utf-8 -*-
"""t30-summary.md 口径更正（Captain 令，`t44` 实测）：把"现闭集"改为 payload／部署态**双列**，
并修正 §4.5 的转绿条件为**两口径**；§9.2 补"ch5 已判、修订待派单"。

幂等实现：先检测标记，已应用则**不再改**（并报"已应用"）。所有数值现算，不手抄。
"""
import hashlib
import io
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
SUM = os.path.join(HERE, 't30-summary.md')
MARK = '**口径更正（t44 实测 / Captain 令）："现闭集"必须双列**'

A1 = """实测（python 明文）：`TM600_HS_RDSON` SetOn 数字集合 = `[13,57,60,61,83,85,126]` ⇒ **无 110**；"""

B1 = """实测（python 明文，**两态分开**；Captain 令按 `t44` 实测更正）：
> **口径更正（t44 实测 / Captain 令）："现闭集"必须双列** —— 此前"TM600 现 SetOn 含 `K109/K110`、无 `48/76`"
> 的说法**只对 payload 成立**。两态实测：
>
> | 态 | 对象 | TM600 SetOn 数字集合 | 判定 |
> | --- | --- | --- | --- |
> | **payload（DELIVERED）** | `implementation-payload-TM600-TM601.cpp:219` | `[13,57,60,61,83,85,109,110,126]` | **闭错腿（109/110）+ 漏闭（48/76）** |
> | **部署态（DEPLOYED＝本门禁实际输入）** | `ForCodexDebug/source/test.cpp:9081` | `[13,57,60,61,83,85,126]` | **仅漏闭**（两腿皆不闭；只闭 `K57_CAP_BST_SW` 自举电容继电器） |
>
> ⇒ 本门禁的阳性对照描述**一律以部署态为准**（下表即部署态读数）。"""

A2 = """`t29`（补 K109/K110）落盘后，`TM600_HS_RDSON: 缺失=[]` ⇒ `FAIL=0` ⇒ **门禁转绿**。
但需注意：本断言**只要求契约声明必需者**，故 `t29` 只补 `K109+K110` 即可转绿；
若日后裁定 `K109` 非必需，只需**改契约**（或加 `--tm-alias`/`--check-extra` 参数），**断言代码无需改动**。"""

B2 = """**转绿条件取决于契约口径（Captain 令：两口径并列，不得单写"转绿"）**：

| 契约口径 | 期望集合 | t29 落盘后部署态 | 判定 |
| --- | --- | --- | --- |
| **rev 24（现状，pin-18 口径）** | `[60,61,83,110]` | 缺 `110` 被补上 ⇒ `缺失=[]` | ⇒ **`FAIL=0`，门禁转 GREEN**（原预期成立） |
| **rev 25（`t42`/`t44` 判 ch5 后，`[48,76]` 口径）** | `[48,61,76]` | 部署态**仍缺 `48/76`**（payload 亦缺） | ⇒ **仍 NEW-RED**，属**第二处真缺陷**（TM600 未闭 `[48,76]`），**不是回归、也不是 t29 的错** |

- 本断言**只要求契约声明必需者**，故 `t29` 只补 `K109+K110` 在 rev 24 口径下即可转绿；
- `K109` 若日后裁定非必需，只需**改契约**（或加 `--tm-alias`/`--check-extra` 参数），**断言代码无需改动**；
- **ch5 口径的断言修订须由 Captain 另派任务**（范围仅 `scripts/verify_bst_sw_sequence.py` + 日志），
  **不得改动 `gate_baseline.json`**；且届时须给**阳性对照**（当前树缺 `[48,76]` ⇒ 必须报红）。
- 取证：`gate-logs-t33/t33_postreplace_expectation.log`（脚本 `t33_postreplace_expectation.py`，已登记进 `t28-anchors.json`）。"""

A3 = """⇒ **"到 BST 需 `[110]`"只成立于 pin-18 前提**（即 `SW12_U1REF_BST_ACM` 这台实例落在 ACM200 的
FH18/SH18 脚）。**该前提由 `t42`（schematic-expert）独立裁定。**"""

B3 = """⇒ **"到 BST 需 `[110]`"只成立于 pin-18 前提**（即 `SW12_U1REF_BST_ACM` 这台实例落在 ACM200 的
FH18/SH18 脚）。**该前提由 `t42`（schematic-expert）独立裁定。**

> **前提已判（`t42` + `t44`）：走 `ch5` ⇒ 到 BST 需 `[48,76]`。** 其最强证据为**行为层**：
> `test.cpp:7000/7087/7170/7513` 这些**已执行**调用点闭 `K48_ACM5_AMP_REF` + `K76_ACM_BST`，
> 且 `:6997/:7598/:7621` 注释把 `SW12_U1REF_BST_ACM` 与 `ACM200_FH5` 写在同一句；
> `K_BST_ACM` 复合宏被**主动降级**为意图/文档证据（**1 定义 / 0 调用点**）。
> ⇒ **本门禁的 ch5 口径修正待 Captain 派单**（见 §4.5 两口径表）；在那之前，本文件一律按**契约 rev 24** 判定。"""


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def main():
    t = io.open(SUM, encoding='utf-8-sig').read()
    print('更正前: %d B / %s' % (os.path.getsize(SUM), sha(SUM)))
    if MARK in t:
        print('✅ 已应用过（检测到标记），本次不再改动（幂等）')
        return
    for label, a, b in (('§4.1 双列表述', A1, B1), ('§4.5 转绿条件两口径', A2, B2), ('§9.2 前提已判', A3, B3)):
        n = t.count(a)
        if n != 1:
            print('ERROR: 锚点 %s 命中 %d 次（应 1）⇒ 拒绝改动' % (label, n))
            sys.exit(1)
        t = t.replace(a, b, 1)
    io.open(SUM, 'w', encoding='utf-8', newline='').write(t)
    t2 = io.open(SUM, encoding='utf-8-sig').read()
    print('更正后: %d B / %s' % (os.path.getsize(SUM), sha(SUM)))
    print('  含双列表述 =', '仅漏闭' in t2)
    print('  含两口径表 =', 'rev 25（`t42`/`t44` 判 ch5 后' in t2)
    print('  含"前提已判" =', '前提已判（`t42` + `t44`）' in t2)
    r = subprocess.run([sys.executable, os.path.join(WS, 'team', 'artifacts', 'acceptance-20260916-dali10',
                                                     'gate-logs-t28', 't28_make_anchors.py')],
                       capture_output=True, text=True, encoding='utf-8')
    print('  anchors 已刷新:', (r.stdout or '').splitlines()[0] if r.stdout else r.stderr[:200])


if __name__ == '__main__':
    main()
