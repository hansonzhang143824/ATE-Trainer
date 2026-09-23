# -*- coding: utf-8 -*-
"""按 schematic-expert ③ 落地两条（幂等）：
  (a) **一般形式**：任何被引用的值必须携带"它的定义"（域/单位/投影/词表/引用判定皆为其特例）
      ⇒ **"定义档"（如 receipts.meta.json）是一般解**，而非散落 N 处注记。
  (b) **⚠️ 递归**：**定义档自身也会漂** ⇒ 它必须**带版本**，且定义要**按版本引用**；
      **递归只能以"被钉定的版本号"终止**（否则它成为下一个"未声明框架"）。
  ⇒ 据此给 `receipts.meta.json` 加 `metaVersion` + 自证（其自身身份）。
"""
import collections
import hashlib
import io
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.abspath(os.path.join(HERE, '..'))
META = os.path.join(HERE, 'build-report.receipts.meta.json')
GEN = os.path.join(HERE, 't54_make_report.py')
REG = os.path.join(RUN, 'gate-logs-t54', 't54-discipline-register.md')

print('=== (a)(b) 记录规则 ===')
MARK = '## 附十七｜任何被引用的值必须携带其定义；定义档自身也须带版本（递归终止）'
t = io.open(REG, encoding='utf-8-sig').read()
if MARK in t:
    print('  已并入（幂等）')
else:
    BLOCK = '''

---

''' + MARK + '''

**来源**：schematic-expert 指出我方 `receipts.meta.json`（`fieldDefinitions` + 陷阱警告）是
**散落各处的规则的一般形式**，并随即指出其**递归风险**。

**规则一｜任何被引用的值必须携带"它的定义"**
> 域 / 单位 / 投影 / 词表 / 引用判定 —— **皆为其特例**。
⇒ **"定义档"是一般解**（一个档，而不是散落在 N 处注记）。

**本 run 的各处实例（同一条规则的不同对象）**
| 对象 | 定义载体 |
| --- | --- |
| 报告 | `projectionSpec`（**哈希的投影**） |
| 账本 | `countUnitNote`（**计数的单位**） |
| 核对器 | **作用域 + 降级/权威词表 + 引用判定**（**判据的定义**） |
| 账本条 | `fieldDefinitions` + **真实踩坑实例警告**（**字段的定义**） |

**规则二｜⚠️ 递归：定义档自身也会漂**
> **定义档必须带版本，且定义要按版本引用**；**递归只能以"被钉定的版本号"终止** ——
> 否则**它自己成为下一个"未声明框架"**（与"投影必须带版本""指针不得硬记度量"同源）。

**落地**：`build-report.receipts.meta.json` 新增 **`metaVersion`** 与**自身身份字段**
（`metaSha256` / `metaSize` / `metaAt`，**生成时现算**）⇒ 引用定义档时**按版本 + 现算身份**。
'''
    io.open(REG, 'w', encoding='utf-8', newline='').write(t.rstrip() + BLOCK)
    print('  已并入 → %d B' % os.path.getsize(REG))

print('\n=== (b) 给 receipts.meta.json 加版本与自身身份 ===')
meta = json.load(io.open(META, encoding='utf-8-sig'))
b = open(META, 'rb').read()
meta['metaVersion'] = 1
meta['metaIdentity'] = {
    'note': ('本档自身也会漂 ⇒ 必须**带版本**且**定义按版本引用**（递归只能以钉定的版本号终止）。'
             '下列身份字段为**上一次生成时现算**；引用本档请按版本号 + 当次现算身份。'),
    'metaSha256_atWrite': hashlib.sha256(b).hexdigest(),
    'metaSize_atWrite': len(b),
    'metaAt': __import__('datetime').datetime.now().astimezone().isoformat(timespec='seconds'),
}
io.open(META, 'w', encoding='utf-8').write(json.dumps(meta, ensure_ascii=False, indent=2))
print('  已写 → %d B' % os.path.getsize(META))
m2 = json.load(io.open(META, encoding='utf-8-sig'))
print('  metaVersion =', m2['metaVersion'])
print('  含 metaIdentity =', 'metaIdentity' in m2)

print('\n=== 并让生成器持续维护（写入器升级）===')
src = io.open(GEN, encoding='utf-8-sig').read()
if 'RECEIPT_META_V1' in src:
    print('  生成器已含（幂等）')
else:
    TAIL = '''

# ==== RECEIPT_META_V1：定义档（带版本 + 自身身份）====
# schematic-expert ③：定义档自身也会漂 ⇒ 必须带版本，且定义按版本引用（递归以钉定版本号终止）
_meta_p = os.path.join(RUN, 'gate-logs-t54', 'build-report.receipts.meta.json')
try:
    _m = io.open(_meta_p, encoding='utf-8-sig').read() if os.path.isfile(_meta_p) else None
    _mj = _json.loads(_m) if _m else {}
except Exception:
    _mj = {}
_mj.setdefault('ledger', 'build-report.receipts.jsonl')
_mj['metaVersion'] = _mj.get('metaVersion', 1)
_mj['fieldDefinitions'] = _mj.get('fieldDefinitions') or {
    'prevLineSha256': '上一行原始行字节的 sha256（链用的就是它）',
    'ledger_self_sha256': '本行语义摘要的 sha256（不是链用的那个）',
    'live_sha256': '当次生成时刻的整文件字节哈希',
    'live_lf_sha256': '同上，但行尾归一化（LF）后',
    'reproducibleBodySha256': '剔除 projectionSpec.exclude 后的 body 哈希（幂等/内容判定用）',
}
_mj['warning'] = ('prevLineSha256（链）与 ledger_self_sha256（语义摘要）不是同一个东西；'
                  '用错定义会得到看起来可信的错结论（本 run 实测）')
_mj['metaIdentity'] = {'note': ('本档自身也会漂 ⇒ 带版本 + 定义按版本引用；'
                                '身份字段为上一次生成时现算；引用请按版本号 + 当次现算身份'),
                       'metaAt': _dt.datetime.now().astimezone().isoformat(timespec='seconds')}
open(_meta_p, 'w', encoding='utf-8').write(_json.dumps(_mj, ensure_ascii=False, indent=2))
_b2 = open(_meta_p, 'rb').read()
_mj['metaIdentity']['metaSha256_atWrite'] = _hl.sha256(_b2).hexdigest()
_mj['metaIdentity']['metaSize_atWrite'] = len(_b2)
open(_meta_p, 'w', encoding='utf-8').write(_json.dumps(_mj, ensure_ascii=False, indent=2))
print('RECEIPT-META v%s (%d B)' % (_mj['metaVersion'], os.path.getsize(_meta_p)))
'''
    io.open(GEN, 'a', encoding='utf-8', newline='').write(TAIL)
    print('  已追加定义档维护逻辑 → %d B' % os.path.getsize(GEN))

import ast
ast.parse(io.open(GEN, encoding='utf-8-sig').read())
print('  语法 OK')
for i in (1, 2):
    r = subprocess.run([sys.executable, GEN], capture_output=True, text=True, encoding='utf-8')
    tl = [x for x in (r.stdout or '').strip().splitlines() if 'RECEIPT' in x]
    print('  run%d: %s' % (i, ' | '.join(tl)[:90]))

m3 = json.load(io.open(META, encoding='utf-8-sig'))
print('\n  最终：metaVersion = %s ｜ 键 = %s' % (m3['metaVersion'], list(m3.keys())))
hs = [l.strip() for l in io.open(REG, encoding='utf-8-sig').read().splitlines() if l.strip().startswith('#')]
c = collections.Counter(hs)
print('  登记 %d B ｜ 标题 %d ｜ 唯一 %d ｜ 重复 %s'
      % (os.path.getsize(REG), len(hs), len(c), [k for k, v in c.items() if v > 1] or '无'))
