# -*- coding: utf-8 -*-
"""复核 Captain 的部署态实测（④）+ 按裁定更新 t33 两份记录（幂等）。

复核：部署态 TM600 段 `SW12_U1REF_BST_ACM` 引用数 / `.Set` 调用数 / FV 值序列 /
      `K48`/`K76`/`K109`/`K110` 命中；TM601 段 `.Set` 调用数。
更新：
  A) t33-transition-plan.md —— 按裁定 (i) 合并批：落盘后 bst-sw **期望 GREEN**，取消"落盘后仍红"例外
  B) t33-revision-attribution.md —— 归属表新增"部署态活危害"一行（归属对象仍 compiledRevision=15c7d2b8…）
"""
import hashlib
import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(WS, 'scripts'))
import proj_config  # noqa: E402
from gen_path_defines import read_enc  # noqa: E402
import verify_relay_trace as V  # noqa: E402

cfg = proj_config.load(os.path.join(WS, 'project_config.json'))
t, _e = read_enc(cfg['derived']['test_cpp'])
blocks = dict(V.fn_blocks(t))

print('=== 复核 Captain ④ 的部署态实测 ===')
for fn in ('TM600_HS_RDSON', 'TM601_LS_RDSON'):
    b = blocks[fn]
    refs = b.count('SW12_U1REF_BST_ACM')
    sets = len(re.findall(r'SW12_U1REF_BST_ACM\.Set\(', b))
    fvs = re.findall(r'SW12_U1REF_BST_ACM\.Set\(FV,\s*([-\d.]+)', b)
    counts = {k: len(re.findall(r'\bK%s\b' % k, b)) for k in ('48', '76', '109', '110')}
    print('  %-16s 引用=%-3d .Set=%-3d FV序列=%s  K48/K76/K109/K110=%s'
          % (fn, refs, sets, fvs, [counts[k] for k in ('48', '76', '109', '110')]))

plan = os.path.join(HERE, 't33-transition-plan.md')attr = os.path.join(HERE, 't33-revision-attribution.md')
MARK_P = '（裁定 (i) 合并批）'
MARK_A = '部署态**活危害**'


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


# ---- A) 更新 transition plan ----
tp = io.open(plan, encoding='utf-8-sig').read()
if MARK_P in tp:
    print('\n[A] transition-plan 已更新过（幂等）')
else:
    anchor = '## 分支 A：t42 判**pin 18**（`[110,61]` 成立，契约 rev 24 无需改）'
    add = ('## 裁定：**单一合并批**（Captain 2026-09-16）' + MARK_P + '\n\n'
           'Captain 裁定选 **(i) 合并为同一批落盘**：**`rev 25`（契约消歧 + 结构化别名归属）与 payload 改动同一批**，\n'
           '**在 `t43`（`K109/K110` 去留裁定）之前不落盘**；批处理完成后**只重跑一次门禁**。\n\n'
           '**据此更新的落盘后期望**：批处理完成后 **`bst-sw` 期望为 GREEN**\n'
           '（修正后契约期望集 `[48,61,76]`，payload 的 TM600 将闭 `K48`+`K76`(+`K61`)）⇒\n'
           '**不再存在"落盘后仍红"的例外路径**；其余 11 门不变；`cbit` 仍为基线豁免。\n'
           '⇒ 本节下方的**分支 B/C 仅作为历史备选保留**，不再是预计路径。\n\n'
           '---\n\n')
    if anchor not in tp:
        print('  ERROR: transition-plan 锚点未命中，跳过该文件')
    else:
        io.open(plan, 'w', encoding='utf-8', newline='').write(tp.replace(anchor, add + anchor, 1))
        print('\n[A] transition-plan 已更新: %d B → %d B / %s' % (len(tp.encode()), os.path.getsize(plan), sha(plan)[:16]))

# ---- B) 更新 revision attribution ----
ta = io.open(attr, encoding='utf-8-sig').read()
if MARK_A in ta:
    print('[B] revision-attribution 已更新过（幂等）')
else:
    anchor2 = '## 3. 待落盘后一次性加入 `build-report.json` 的字段（清单）'
    add2 = ('''## 2.1 部署态"活危害"（Captain 独立实测，我复核确认；归属对象仍为 `compiledRevision = 15c7d2b8…`）

| 观测（部署态 `test.cpp` `15c7d2b8…`） | 值 |
| --- | --- |
| TM600 段 `SW12_U1REF_BST_ACM` 引用 | 11 |
| TM600 段 `SW12_U1REF_BST_ACM.Set(` 调用 | 10（`FV 0/5/10/15/20` 与回落 `15/10/5`，全部 `ACM200_RELAY_ON`） |
| TM600 段 `K48` / `K76` / `K109` / `K110` 命中 | **0 / 0 / 0 / 0** |
| TM601 段 `SW12_U1REF_BST_ACM.Set(` 调用 | 3 |

⇒ **这不是"少一个闭合"，而是部署态**活危害**（Captain 实测、我复核确认）**：TM600 段**正在驱动 ch5 源**（`.Set(FV,…)` 且 `ACM200_RELAY_ON`）**而 `K48` 未闭**；
按 `t44`/`t45` 的改道机制，源被送往 `SW1_F/SW2_F`（**既非 BST，也非 PB0**）。
⇒ **本行归属仍为 `compiledRevision = 15c7d2b8…`**（既非构建过程、也非未部署的 payload）；
**批处理落盘后该危害应随之消除**（payload 的 TM600 将闭 `K48`+`K76`）。
（复核脚本+日志：`gate-logs-t33/t45_verify_captain_deployed.py` / `t45-captain-deployed-verify.log`）

---

''')
    if anchor2 not in ta:
        print('  ERROR: revision-attribution 锚点未命中，跳过该文件')
    else:
        io.open(attr, 'w', encoding='utf-8', newline='').write(ta.replace(anchor2, add2 + anchor2, 1))
        print('[B] revision-attribution 已更新: %d B → %d B / %s' % (len(ta.encode()), os.path.getsize(attr), sha(attr)[:16]))
