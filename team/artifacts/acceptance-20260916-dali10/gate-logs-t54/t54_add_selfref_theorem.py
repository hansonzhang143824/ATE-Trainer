# -*- coding: utf-8 -*-
"""并入 schematic-expert ③④ 的两条（幂等）：
 ③ **结构性理由**：一个字段**无法记录"它所在文件的现身份"** ⇒ 自指字段只有两条合法出路：
     **(i) 指向过去**（`*_atWrite` / `prevLineSha256`）；**(ii) 被版本钉住**（`metaVersion` 作基例）。
     ⇒ **"本文件当前身份"在原理上不可能存在**（除非有**外部载体**，即收据那种外部重算方案）。
 ④ **跨产物收敛**：名字承载限定（L-b）—— 与 `ate-implementer` 的 `artifactSha256IsHistorical` 独立收敛。
"""
import collections
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.abspath(os.path.join(HERE, '..'))
REG = os.path.join(RUN, 'gate-logs-t54', 't54-discipline-register.md')
MARK = '## 附廿三｜自指字段只能"指向过去"或"被版本钉住"；限定写进名字（L-b）'


def sha(p):
    import hashlib
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


t = io.open(REG, encoding='utf-8-sig').read()
print('登记 %d B ; 已并入 = %s' % (os.path.getsize(REG), MARK in t))
if MARK in t:
    print('已并入（幂等）')
    raise SystemExit(0)

BLOCK = '''

---

''' + MARK + '''

**来源**：schematic-expert 由我方 `metaIdentity` 的**实测漂移**（记录 1,115 B / 现值 1,241 B，**差 126 B**）
推出**结构性理由**；并观察到与 `ate-implementer` 的**独立收敛**。

**规则一｜自指字段的两条合法出路（结构性，非惯例）**
```
**一个字段无法记录"它所在文件的现身份"** —— 因为把该哈希写进去，文件本身随即改变
  ⇒ 故自指字段只有两条出路：
     (i) **指向过去**：记录"上一代 / 写入时刻"的身份（`metaSha256_atWrite`、链条的 `prevLineSha256`）✓
     (ii) **被版本钉住**：`metaVersion` 作为**基例**，定义按版本引用 ✓
⇒ **"本文件当前身份"这种字段在原理上不可能存在**
   —— **除非另有外部载体**（即本项目 `receipt.json` 那种**外部重算**方案）✓
```
**本 run 实证**：`metaIdentity.note` 已自陈"**身份字段为上一次生成时现算**"＋"引用请按**版本号 + 当次现算身份**" ✓
**⇒ 用法规则（双方确认）**：
> **引用定义档时：按 `metaVersion` 定位，并在使用处现算该档身份**；
> **`metaSha256_atWrite` 只能当"在 `metaAt` 那一刻确曾生成过某一版"的历史证据，不得当作现身份** ✓

**规则二｜限定写进名字（L-b：名字承载限定）**
```
我方用 `metaSha256_atWrite` / `metaSize_atWrite`（限定在名字里）；
`ate-implementer` 用 `artifactSha256IsHistorical`（限定在名字里）⇒ **独立收敛到同一形态** ✓
⇒ 在"只引字段名 / 路径"的引用纪律下，**名字承载限定是最强的位置** ⇒ 写成**标准做法**：
   **需要限定一个值时，优先把限定写进字段名；语义一旦稳定就不再改名**（改名按"只增不翻"）✓
⇒ **代价（须同时记下）**：**改名会让他方的按名引用悬空**（`mirrorSize → mirrorSizeAtMirrorTime` 即一例）✓
```
'''
io.open(REG, 'w', encoding='utf-8', newline='').write(t.rstrip() + BLOCK)
t2 = io.open(REG, encoding='utf-8-sig').read()
print('已并入: %d B / %s' % (os.path.getsize(REG), sha(REG)))
hs = [l.strip() for l in t2.splitlines() if l.strip().startswith('#')]
c = collections.Counter(hs)
print('  标题 = %d ; 唯一 = %d ; 重复 = %s' % (len(hs), len(c), [k for k, v in c.items() if v > 1] or '无'))
for k in (MARK, '指向过去', '被版本钉住', '名字承载限定', '外部载体'):
    print('  含 %-14s %s' % (k, k in t2))
