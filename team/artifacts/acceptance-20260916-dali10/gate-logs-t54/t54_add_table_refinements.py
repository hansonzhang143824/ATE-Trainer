# -*- coding: utf-8 -*-
"""并入 rule-reviewer ① 的两点表格补充（幂等）：
  (i) 第 (vi) 行注明"与附五主条同源、此处按『信号 vs 对象』角度重列"（避免读成重复）；
  (ii) 第 (iii) 行加一句："**自己打印的信号也不能替代检查本身**"（本表唯一"信号由被检对象自己打印"的情形）。
并采纳其把表的定位写成 **R2 第 (vi) 正文**、以及配套优先级"结构判据 > 哨兵常量 > 外部收据"。
"""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REG = os.path.abspath(os.path.join(HERE, '..', 'gate-logs-t54', 't54-discipline-register.md'))
MARK = '### 附七·补充（rule-reviewer 提，已采纳）'


def sha(p):
    import hashlib
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


t = io.open(REG, encoding='utf-8-sig').read()
print('登记 %d B ; 已并入 = %s' % (os.path.getsize(REG), MARK in t))
if MARK in t:
    print('已并入（幂等）')
    raise SystemExit(0)

BLOCK = '''

''' + MARK + '''

**(i) 第 (vi) 行与附五主条的关系（避免读成重复）**
> 附七表第 **(vi)** 行（`size` 相同 ⇒ 断言"同一版本/同一内容"）**与 §附五主条同源**；
> 此处按 **"信号 vs 对象"** 的角度**重列** ——
> 附五看的是**记录粒度**（size 只声称字节长度），附七看的是**信号是否指向对象本身**（size 不指向内容）。
> ⇒ **同一实例、两个视角；不是两处重复。**

**(ii) 第 (iii) 行是表里最有价值的一行 —— 且它是唯一"信号由被检对象自己打印"的情形**
> `targets=0` 时 `[scan]` 行**照印**（门禁：**日志有字样 ≠ 检查发生过**）
> ⇒ **加一句判据**：**自己打印的信号也不能替代检查本身。**
> （**与门禁完整性缺口同源**：门禁的 `exit 0` 是它**自己**给的信号，而"断言是否真的跑过"必须另有证据。）

**(iii) 本表的定位与配套（采纳其写法）**
> 本表作为 **R2 第 (vi) 的正文**（而非举例）—— 因其**可枚举、可对号、可追加**。
> **存在的判定请用（优先级）：结构判据 > 哨兵常量 > 外部收据**；
> **禁止用同名文字 / 键名 / 字段存在 作为存在性证据。**
> ⇒ 三件修法**都已在本 run 落地**（哨兵常量 `RECEIPT_WRITER_V1`；结构判据 `json.loads` 后测 key/路径；
> 外部收据 + 双哈希）⇒ **该纪律不是"建议"，而是已有三种实施形态。**
'''
io.open(REG, 'w', encoding='utf-8', newline='').write(t.rstrip() + BLOCK)
t2 = io.open(REG, encoding='utf-8-sig').read()
print('已并入: %d B / %s' % (os.path.getsize(REG), sha(REG)))
for k in (MARK, '同一实例、两个视角', '自己打印的信号也不能替代检查本身', '结构判据 > 哨兵常量 > 外部收据'):
    print('  含 %-30s %s' % (k, k in t2))
