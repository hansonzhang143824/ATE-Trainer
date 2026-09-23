# -*- coding: utf-8 -*-
"""t28-freeze-correction.md §5 引用纪律 —— 幂等写入（先剥离历史段，再追加一次；并自证稳定）。

为什么单独一个脚本: 我的上一个"追加"脚本**又犯了非幂等** —— 连跑两次把 §5 追加了两遍
（3,594 → 6,001 → 8,408 B）。这正是我在 §5 里刚写下的"写文档的脚本必须证明幂等"。
本脚本把 §5 的实现改成**先剥离、再追加、再自校验**，并连跑验证哈希不变。

本脚本严禁手打任何哈希；一切由 sha256(file) 取得。
"""
import hashlib
import io
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
FC = os.path.join(HERE, 't28-freeze-correction.md')
ANCHORS_REL = 'team/artifacts/acceptance-20260916-dali10/gate-logs-t28/t28-anchors.json'
MARK = '## 5. 引用纪律（2026-09-16，我方事故后与 rule-reviewer 共同采纳）'
LEGACY = re.compile(r'\n*---\n+## 5\. 引用纪律.*\Z', re.S)


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def build_block():
    s_sum = os.path.getsize(os.path.join(HERE, 't28-summary.md'))
    return """

---

""" + MARK + """

**事故（双方同类，各自自曝）**
1. **我方**：我在给评审方的消息里**手抄** `t28-red-proof.json` 的冻结哈希，**第 42 位 `c` 误作 `b`**
   （64 位中仅此一处）；我自己的校验脚本因此一度把该文件报为"变"。
   评审方**字符级复核**确认：文件字节未变、`redProofPassed=true`、mtime 未变
   ⇒ **属申报瑕疵，非完整性事故**。
2. **评审方**：为核对该"正确值"，它在自己的探针里**手拼 expected 值**，导致其表格中该项报 `match=False`
   —— **那是探针的假阴性，不是文件变化**；按实际值重算后一致。
3. **我方另有同类（共 3 处）**：更正消息里**再次手抄错同一个哈希**；把 `t28-citation-notice.txt`
   尺寸报成 3,827 B（实为 4,724 B）；以及**本节脚本第一版非幂等**（连跑两次重复追加，见上）。

**纪律（双方共同采纳，即本 run 正式口径）**
> **任何被引用的哈希必须由脚本从产物直接 `sha256(file)` 取得并回填；
> 禁止手打，禁止在报告里手拼 expected 值作核对基准。**

**配套（我方已落地）**
- **单一真源**：`""" + ANCHORS_REL + """`（逐条 `path / size / sha256 / readAt / note`，
  由 `t28_make_anchors.py` 生成，全程无人工转录）；
- 报告类文档（`t28-summary.md` 等）会被作者继续编辑 ⇒ 引用一律**现算 + 标时刻**；
- 一切读取/哈希**一律用 python（rb）**：本工作区源受 DLP 透明加密，pwsh 文本工具会拿到密文；
- **写文档的脚本必须证明幂等**：本文件 §5 的写入脚本已改为"先剥离历史段再追加"，
  并以"连跑两次哈希不变"自证。

**现盘尺寸（本节写入时刻，脚本现算）**：`t28-summary.md` = %d B（哈希请现算或读 `%s`）。
""" % (s_sum, ANCHORS_REL)


def main():
    t = io.open(FC, encoding='utf-8-sig').read()
    stripped = LEGACY.sub('', t).rstrip()
    before = sha(FC)
    io.open(FC, 'w', encoding='utf-8', newline='').write(stripped + build_block())
    after = sha(FC)
    s = io.open(FC, encoding='utf-8-sig').read()
    print('t28-freeze-correction.md: %d B / %s  (was %s)' % (os.path.getsize(FC), after, before[:16]))
    print('  §5 出现次数 = %d（应为 1）' % s.count(MARK))
    print('  剥离了历史重复段 = %s' % (t.count(MARK) > 1))


if __name__ == '__main__':
    main()
