# -*- coding: utf-8 -*-
"""并入 rule-reviewer ② 提纯的纪律（幂等）：
**存在性/状态检查必须指向"对象本身"，不得指向"与该对象同时出现的信号"**（实例族六项，双方各出一例）。
"""
import hashlib
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REG = os.path.abspath(os.path.join(HERE, '..', 'gate-logs-t54', 't54-discipline-register.md'))
MARK = '## 附七｜存在性/状态检查必须指向"对象本身"，不得指向"同时出现的信号"'


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


t = io.open(REG, encoding='utf-8-sig').read()
print('登记 %d B ; 已并入 = %s' % (os.path.getsize(REG), MARK in t))
if MARK in t:
    print('已并入（幂等）')
    raise SystemExit(0)

BLOCK = '''

---

''' + MARK + '''

**来源**：rule-reviewer 把**我方一次失误**与**其自己一次失误**提纯为同一条纪律，并**双方共同认领**。

**共同形式**
> **存在性/状态检查必须指向"对象本身"，不得指向"与该对象同时出现的信号"。**

**实例族（六项，双方各出一例标 ★）**
| # | 信号（被误用） | 它**实际**证明了什么 | 被误用来断言 |
| --- | --- | --- | --- |
| (i) ★我方 | **同名文字出现**（`'build-report.receipt.json' in 文本`） | 只是"文本里提到该名" | "**该文件已存在**" → 误判、跳过生成 |
| (ii) ★其方 | **`preservedPeerKeys` 键名出现** | 只是"键名被保留" | "**键内条目被保全**" → 先错一次、更正时再过简一次 |
| (iii) | **`targets=0` 时 `[scan]` 行照印** | 只是"日志有该字样" | "**检查发生过**" |
| (iv) | **`revision` 字段在位** | 只是"有个自述标签" | "**内容一致**" |
| (v) | **`mtime` 存在** | 只是"有个修改时刻" | "**先后正确**" |
| (vi) | **`size` 相同** | 只是"字节数相同" | "**同一版本/同一内容**" |

**修法（本 run 已落地的三件）**
1. **哨兵常量**（我方：`RECEIPT_WRITER_V1`）替掉"字符串包含"；
2. **结构判据**（`json.loads` 后测 key / 路径 / 字段）；
3. **外部收据**（活档自陈"我是活的"，身份交外部收据）＋ **双哈希**（区分"内容变了"与"只是行尾变了"）。

**★ "双方各自独立踩过同一条"是本 run 的常态，也是该纪律必要的证据**
⇒ rule-reviewer 提议将其并入 R2 的第 (vi) 项，并在其中注明**由两侧各出一例** ✓（我方同意）。

**验证它的正是"改后必须复验"**（见 §附四）：
抓住我方该处失误的是 `t54_postchange_verification.py` 重跑（**25 项全过 / 总判定 PASS**）与
`validate_team_artifact.py`（**PASS / exit 0**）⇒ **该纪律本轮第二次证明有效**
（第一次＝拦下 rule-reviewer 的 `t58` 二阶漂移）。
'''
io.open(REG, 'w', encoding='utf-8', newline='').write(t.rstrip() + BLOCK)
t2 = io.open(REG, encoding='utf-8-sig').read()
print('已并入: %d B / %s' % (os.path.getsize(REG), sha(REG)))
for k in (MARK, '同时出现的信号', '哨兵常量', '双方各自独立踩过同一条'):
    print('  含 %-22s %s' % (k, k in t2))
