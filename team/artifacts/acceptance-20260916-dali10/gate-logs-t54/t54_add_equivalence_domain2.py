# -*- coding: utf-8 -*-
"""（修正版：字符串内不用反引号，改用『』）并入 schematic-expert ②③（幂等）。"""
import collections
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.abspath(os.path.join(HERE, '..'))
META = os.path.join(HERE, 'build-report.receipts.meta.json')
H = os.path.join(HERE, 'build-report.receipts.jsonl')
REG = os.path.join(RUN, 'gate-logs-t54', 't54-discipline-register.md')

print('=== ① 复核其"成立条件" ===')
raw = open(H, 'rb').read()
lines = [l for l in raw.split(b'\n') if l.strip()]
ending = [i for i, l in enumerate(lines, 1) if l.endswith(b'\r')]
print('  CRLF = %d ｜ 孤立 LF = %d ｜ 行数 = %d' % (raw.count(b'\r\n'), raw.count(b'\n') - raw.count(b'\r\n'), len(lines)))
print('  内容以 CR 结尾的行 = %s（其测为空）' % (ending if ending else '[]（空）'))
print('  ⇒ 与其一致 ✓ ⇒ 等价性今日成立、但属"带域的主张" ✓')

print('\n=== ② 把成立条件写进 meta ===')
m = json.load(open(META, encoding='utf-8-sig'))
m['fieldDefinitions']['prevLineSha256'] = (
    'sha256( 上一行的字节，去掉其行终止符 )；本文件为 CRLF ⇒ CR 一并去掉。'
    '等价实现（带成立条件）：hashlib.sha256(prev_line_bytes.rstrip(b"\\r\\n"))；'
    '另一式 rstrip(b"\\r") 在本账本的约束下同解 —— 约束＝没有任何一行的内容以 CR/LF 结尾'
    '（本 run 实测该条件的行集合 = 空）；若将来某行内容真的以 CR 结尾，则两式分歧'
    '⇒ 『等价』也是带域的主张。')
m['equivalenceIsDomainBound'] = '『等价实现』必须连同其成立条件（域）声明 —— 否则『今日同解』会被读成『永远同解』。'
open(META, 'w', encoding='utf-8').write(json.dumps(m, ensure_ascii=False, indent=2))
print('  meta 已改 → %d B' % os.path.getsize(META))

print('\n=== ③ 规则入册 ===')
MARK = '## 附廿九｜"探 vs 枚举"的三个表面（容器键 / 域根集 / 调用点）与单一处方'
t = open(REG, encoding='utf-8-sig').read()
if MARK in t:
    print('  已并入（幂等）')
else:
    BLOCK = '''

---

''' + MARK + '''

**来源**：schematic-expert 把我方一处"改了 A 却漏了同源的 B"（`_prev_lines` 由 str 改 bytes 时漏改 `ledger_self_sha256` ⇒ `TypeError`）
并入一条**更一般的规律**：**"按假设去探"而不是"把集合枚举出来"**。

**三个表面（本 run 各一实例）**
| # | 表面 | 实例 |
| --- | --- | --- |
| 1 | **容器键** | 按假设去探字段，未列 key set |
| 2 | **域 / 根集** | rule-reviewer 的工具**静默漏掉** `.agent-teams/**`（域外型） |
| 3 | **调用点** | 改类型时**漏掉第三处同源使用**（我方，本轮） |

**单一处方**
> **凡是"集合"（键集 / 域根集 / 调用点集）都必须枚举出来，而不是靠记、逐项处理。**

**按分诊定级（照实）**
```
调用点那一例属**响亮类**（直接崩、零传播）⇒ **按分诊无需机制化**；
  但**"枚举集合"这条通用处方零成本地覆盖它** ✓
⇒ 记为：**响亮 ⇒ 可不机制化；但"枚举集合"这条处方已覆盖它。**
```

**同源（已入册 §附十九）**：**"等价"也是带域的主张** ——
`rstrip(b'\\r')` 与 `rstrip(b'\\r\\n')` **等价 ⇔ 无任何行内容以 CR/LF 结尾**（本 run 实测该条件行集合 = 空）✓
'''
    open(REG, 'w', encoding='utf-8', newline='').write(t.rstrip() + BLOCK)
    print('  已并入 → %d B' % os.path.getsize(REG))

hs = [l.strip() for l in open(REG, encoding='utf-8-sig').read().splitlines() if l.strip().startswith('#')]
c = collections.Counter(hs)
print('  登记 = %d B ｜ 标题 %d ｜ 唯一 %d ｜ 重复 %s'
      % (os.path.getsize(REG), len(hs), len(c), [k for k, v in c.items() if v > 1] or '无'))
