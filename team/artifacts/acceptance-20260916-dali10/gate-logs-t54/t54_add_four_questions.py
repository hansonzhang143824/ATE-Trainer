# -*- coding: utf-8 -*-
"""回应 setup-architect ③：其把 `baselineTriad` 复述为"契约＝既权威**又中立**"。
我方核对后认为该复述**需要一处修正**：**"中立"应再拆为两问**（归属中立 / 内容经第三方复算），
契约满足前者、不满足后者（它是被撰写且**曾出错**的产物）。

落地：在登记中把三元组**细化为四问**（幂等）。
"""
import hashlib
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REG = os.path.abspath(os.path.join(HERE, '..', 'gate-logs-t54', 't54-discipline-register.md'))
MARK = '### 附五·三元组细化为四问（回应 setup-architect 的"契约＝既权威又中立"）'


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


t = io.open(REG, encoding='utf-8-sig').read()
print('登记 %d B ; 已并入 = %s' % (os.path.getsize(REG), MARK in t))
if MARK in t:
    print('已并入（幂等）')
    raise SystemExit(0)

BLOCK = '''

''' + MARK + '''

**分歧**：setup-architect 在其档内把 `baselineTriad` 复述为"**契约 = 既权威又中立**（门禁消费它；不属任何一方私有）"。
我方核对后认为：**该复述把"中立"当成了一个属性，但它其实是两个问题**。

**细化（四问）**
| # | 问题 | 契约 | 我方报告 | 其 anchors 档 |
| --- | --- | --- | --- | --- |
| 1 | **权威**？（门禁按构造读它） | **是** | 否 | 否 |
| 2 | **归属中立**？（不属任何一方私有） | **是** | 否（我的产物） | 否（其产物） |
| 3 | **对我方的独立性**？（非我所出） | 是（但其内容由**另一成员**撰写） | 否 | 是 |
| 4 | **内容经第三方独立复算**？ | **否** | 否 | 否 |

⇒ **契约满足 1+2，不满足 4**：它是**被撰写的产物**，且 `bst2sw.closedRelayNumbers` 在 **rev 24–28 期间是错的**
（`[110,61]`）⇒ **"归属中立" ≠ "内容已验证"**。
**⇒ 结论（我方表述）**：**契约＝既权威、且归属中立；但仍属"被撰写且曾出错的产物" ⇒ 不是"独立基准"。**

**为何这条区分重要**：若把"归属中立"当成"内容可信"的代名词，就会把**"某人写的值"误当"独立事实"**
—— 这正是我们那条 `size`/`revision`/`preservedPeerKeys` 同族错误的另一种形态（**属性被混为一谈**）。
**⇒ 引用契约时仍须：钉住其修订（现算 sha256）+ 对关键字段做**同级别**的证据核对**（如"该字段曾错"须由字节快照证明）。

**双方一致的部分（不变）**：
- 契约**不是**任何一方的私有档案 ⇒ **可作中立的**权威输入**（此点我方同意其表述）**；
- 我方报告对**其方**独立、但**对我方不独立**；
- 其 anchors 档对 reviewer **既不独立也不中立** ⇒ **reviewer 拒用它作基准是对的**。
'''
io.open(REG, 'w', encoding='utf-8', newline='').write(t.rstrip() + BLOCK)
t2 = io.open(REG, encoding='utf-8-sig').read()
print('已并入: %d B / %s' % (os.path.getsize(REG), sha(REG)))
for k in (MARK, '四问', '归属中立', '但它其实是两个问题'):
    print('  含 %-20s %s' % (k, k in t2))
