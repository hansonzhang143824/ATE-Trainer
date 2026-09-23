# -*- coding: utf-8 -*-
"""t28 引用纪律落地：把我方"手抄哈希"事故与该纪律一并写入 t28-freeze-correction.md（追加，不重写历史）。

同时**现算**评审方引用的两个尺寸，核对是否过期（他在其消息里报了尺寸，我需要验证而非采信）。
严禁在本脚本中手打任何哈希 —— 一切由 sha256(file) 取得。
"""
import datetime
import hashlib
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
FC = os.path.join(HERE, 't28-freeze-correction.md')
ANCHORS = 'team/artifacts/acceptance-20260916-dali10/gate-logs-t28/t28-anchors.json'


def info(p):
    d = open(p, 'rb').read()
    return len(d), hashlib.sha256(d).hexdigest()


print('=== 现算（评审方消息里的尺寸，我方验证而非采信）===')
for label, p in (
    ('我的 t28-summary.md', os.path.join(HERE, 't28-summary.md')),
    ('我的 t28-freeze-correction.md', FC),
    ('我的 t28-citation-notice.txt', os.path.join(HERE, 't28-citation-notice.txt')),
    ('评审方 review/t28-independent-opinion.md',
     os.path.join(WS, 'team', 'artifacts', 'acceptance-20260916-dali10', 'review', 't28-independent-opinion.md')),
    ('评审方 t28-freeze-correction.md（同名，可能不是我的）',
     os.path.join(WS, 'team', 'artifacts', 'acceptance-20260916-dali10', 'review', 't28-freeze-correction.md')),
):
    if os.path.isfile(p):
        s, h = info(p)
        print('  %-58s %8d B  %s' % (label, s, h))
    else:
        print('  %-58s MISSING' % label)

s_sum, h_sum = info(os.path.join(HERE, 't28-summary.md'))
s_fc, h_fc = info(FC)

BLOCK = """

---

## 5. 引用纪律（2026-09-16，我方事故后与 rule-reviewer 共同采纳）

**事故（双方同类，各自自曝）**
1. **我方**：我在给评审方的消息里**手抄** `t28-red-proof.json` 的冻结哈希，**第 42 位 `c` 误作 `b`**
   （64 位中仅此一处）；我自己的校验脚本因此一度把该文件报为"变"。
   评审方**字符级复核**确认：文件字节未变、`redProofPassed=true`、mtime 未变 ⇒ **属申报瑕疵，非完整性事故**。
2. **评审方**：为核对该"正确值"，它在自己的探针里**手拼 expected 值**，导致其表格中该项报 `match=False`
   —— **那是探针的假阴性，不是文件变化**；按实际值重算后 `t28-red-proof.json` 一致。
3. **我方另有同类**：我在更正消息里**再次手抄错同一个哈希**（写成 `…1119cea…`），并出现自相矛盾的"长度异常"自述；
   又在消息里把 `t28-citation-notice.txt` 的尺寸报成 3,827 B（实为下方现算值）。

**纪律（双方共同采纳，即本 run 的正式口径）**
> **任何被引用的哈希必须由脚本从产物直接 `sha256(file)` 取得并回填；禁止手打，禁止在报告里手拼 expected 值作核对基准。**

**配套（我方已落地）**
- **单一真源**：`team/artifacts/acceptance-20260916-dali10/gate-logs-t28/t28-anchors.json`
  （逐条 `path / size / sha256 / readAt / note`；由 `t28_make_anchors.py` 生成，全程无人工转录）；
- 引用报告类文档（`t28-summary.md` / `t30-summary.md` / `t35-*.md` / `t28-independent-opinion.md` 等）
  一律**现算 + 标时刻**，因为它们会被作者继续编辑（本 run 已实测多处漂移）；
- 一切读取/哈希**一律用 python（rb）**：本工作区源受 DLP 透明加密，pwsh 文本工具会拿到密文；
- **写文档的脚本必须证明幂等**：我的"定稿脚本"第一版非幂等（两次运行产生两个哈希），
  已改为**先剥离历史定稿段再追加**，并连跑三次验证哈希稳定。

**现盘（本节写入时刻，由脚本现算）**
- `t28-summary.md`（本文件同目录）= %d B（哈希见 `%s`，或现算）
- `t28-freeze-correction.md`（本节所在文件）= %d B（同上）
- 生成时刻：%s
""" % (s_sum, ANCHORS, s_fc, datetime.datetime.now().astimezone().isoformat(timespec='seconds'))

with io.open(FC, 'a', encoding='utf-8') as f:
    f.write(BLOCK)
d = open(FC, 'rb').read()
print()
print('APPENDED to t28-freeze-correction.md → %d B / %s' % (len(d), hashlib.sha256(d).hexdigest()))
print('  含引用纪律段 =', '引用纪律（2026-09-16' in d.decode('utf-8-sig'))
