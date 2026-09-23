# -*- coding: utf-8 -*-
"""t30 期望集合的**推导来源**逐条定位（只读取证 + 生成加注块）。

Captain 要求加注三件事：(a) 期望集合推导来源逐条 locator；(b) 明写"以 pin-18 为前提，t42 裁定"；
(c) ACCEPT 只覆盖"盲区已关闭"，不覆盖该前提正确性。另加注"两个盲区成因"。

本脚本**只读**被审脚本与契约；把结果**程序化**写成加注块并追加到 t30-summary.md（幂等）。
严禁手打任何哈希。
"""
import hashlib
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
SUM = os.path.join(HERE, 't30-summary.md')
SRC = os.path.join(WS, 'scripts', 'verify_bst_sw_sequence.py')
CONTRACT = os.path.join(WS, 'team', 'artifacts', 'acceptance-20260916-dali10', 'setup-contract.json')
PINCH = 'D:/PROJECT6-DALI/ForCodexDebug/source/Pin_Channel_define.h'


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


print('=== (a) 期望集合的推导链：从源码逐条定位 ===')
src = io.open(SRC, encoding='utf-8-sig').read()
lines = src.splitlines()
for pat, why in ((r'def expected_for_tm', '期望集合构造函数'),
                 (r"d\.get\('aliasesUsed'\)", "第一源：tmDeltas.<TM>.aliasesUsed 声明的别名"),
                 (r'if base in users', "第二源：<TM> 以 token 出现在别名 usedByTm 中"),
                 (r"exp\.setdefault\(n, 'aliasResolution\[%s\]", 'setdefault 记录来源标签'),
                 (r"DEFAULT_TM_SCOPE", '作用范围默认值'),
                 (r'DEFAULT_SCOPE_ARGS|--tm-scope', '作用范围参数化')):
    for i, ln in enumerate(lines, 1):
        if re.search(pat, ln):
            print('  L%-4d %-46s ← %s' % (i, ln.strip()[:46], why))
            break

print('\n=== 契约侧实际取值（形成 [110] 的那一步）===')
c = json.loads(open(CONTRACT, 'rb').read().decode('utf-8-sig'))
al = [e for e in c['aliasResolution'] if e.get('alias') == 'bst2sw'][0]
print('  aliasResolution[bst2sw].resolution.closedRelayNumbers =', al['resolution']['closedRelayNumbers'])
print('  aliasResolution[bst2sw].usedByTm =', json.dumps(al.get('usedByTm'), ensure_ascii=False))
print('  tmDeltas.TM600.aliasesUsed =', json.dumps(c['tmDeltas']['TM600'].get('aliasesUsed'), ensure_ascii=False))
print('  ⇒ 命中路径: usedByTm 的字面串 "TM600 (BST must lead PMID)" 经 \\b(TM\\d+)\\b 抽出 TM600 ⇒ base=TM600 命中')
print('     ⇒ 期望集合含 110（因 closedRelayNumbers=[110,61] 且 61 已在 SetOn 中）')
print('  ⚠️ 附加风险（我必须如实登记）：第二源是**从 usedByTm 的散文描述里用正则抽 TM 号**，')
print('     即期望集合部分依赖**人类可读文本**；若该描述被改写（如 "TM600x"）会静默改变期望集合。')
print('     当前源码提取方式见上方 L 行；建议后续把 base-TM 归属改为结构化字段（属契约侧，非本任务）。')

print('\n=== pin-18 前提的证据 ===')
t = io.open(PINCH, encoding='utf-8-sig', errors='replace').read()
for m in re.finditer(r'^.*SW12_U1REF_BST_ACM.*$', t, re.M):
    print('  Pin_Channel_define.h:', m.group(0).strip()[:120])
print('  契约 ACM200 侧条目 pinRouteTable.BST["列6: ACM200 → PIN (Share继电器)"] =',
      c['tmDeltas']['TM600']['pinRouteTable']['BST'].get('列6: ACM200 → PIN (Share继电器)', {}).get('needsClosed'))

BLOCK = """

---

## 9. 加注：期望集合的前提依赖（Captain 裁定 2026-09-16）

### 9.1 (a) 期望集合的推导来源（逐条 locator）

| 步骤 | locator | 内容 |
| --- | --- | --- |
| 1 | 契约 `aliasResolution[bst2sw].usedByTm` | 字面串 `"TM600 (BST must lead PMID)"` ⇒ 经 `\\b(TM\\d+)\\b` 抽出 base=`TM600` |
| 2 | 契约 `aliasResolution[bst2sw].resolution.closedRelayNumbers` | `[110, 61]` ⇒ 本函数期望集合 {60,61,83,110}（另含 `pmid2sw` 的 83/60/61） |
| 3 | 契约 `aliasResolution[bst2sw].resolution.relayChain` | `[{K110_ACM18_BST, 'SetOn (ACM200 S5_FH18 -> BST)'}, {K61_ACM8_SW, 'SetOn (ACM200 S5_FH8 -> SW)'}]` |
| 4 | 契约 `tmDeltas.TM600.aliasesUsed` | `['pmid2sw']` —— **漏登记 `bst2sw`**，故本断言改以 `usedByTm` 为主索引 |
| 5 | 被审脚本 | `expected_for_tm()` 的两处 `setdefault` 即上述两源；作用范围 `DEFAULT_TM_SCOPE` / `--tm-scope` |
| 6 | 阳性对照 | 部署态 TM600 SetOn 无 110 ⇒ `缺失=[110]` ⇒ `FAIL=1` ⇒ `bst-sw` NEW-RED |

**⚠️ 我方如实登记的附加风险**：第 1 步是**从 `usedByTm` 的散文描述里用正则抽 TM 号** ——
即期望集合**部分依赖人类可读文本**；若该描述被改写（如写成 `TM600x`），期望集合会**静默变化**。
根治应把"别名→TM 归属"改为**结构化字段**（属契约侧，非 t30 inScope）。

### 9.2 (b) 前提依赖：本期望集合**以 pin-18 为前提**

- 宏 `Pin_Channel_define.h`: `_PIN_CHANNEL_DEFINE_SW12_U1REF_BST_ACM_ = "S5_5,S6_5,…"` ⇒ **通道 `_5`**；
- 而契约 ACM200 侧条目 `tmDeltas.TM600.pinRouteTable.BST["列6: ACM200 → PIN (Share继电器)"]`
  的 `needsClosed = [48, 76]`；`StdAfx.h` 亦分列两条通路：`K_BST_ACM = 48,76`（ACM200[] → BST）
  与 `K_FPVIL_TO_BST_B = 109,110`（**FPVIe[L]** → BST）。
⇒ **"到 BST 需 `[110]`"只成立于 pin-18 前提**（即 `SW12_U1REF_BST_ACM` 这台实例落在 ACM200 的
FH18/SH18 脚）。**该前提由 `t42`（schematic-expert）独立裁定。**
⇒ **若 `t42` 判 pin 5**：期望集合应改为 `[48,76]`，或**按路线拆分**（ACM 侧按 pin 5 口径、FPVIe 侧保持）
——Captain 已声明届时另派任务，**且届时不得改动 `gate_baseline.json`**。

### 9.3 (c) ACCEPT 的覆盖边界（不得过度解读）

> **本门禁的 ACCEPT 只覆盖"盲区已关闭"（即：契约声明必需的闭合集不再被门禁无视、
> 缺失必走致命通道、阳性对照成立、只增不改），不覆盖"pin 归属前提"的正确性。**
> 前提正确性属 `t42` 的裁定范围；**不得把本 ACCEPT 读作"前提已裁定"**。
> 这与 **B-6**（"由契约派生的断言，其覆盖上限＝契约登记的完整性"）互为镜像：
> 断言既不能覆盖**错登记**，也不能把**未消歧登记**固化为既成事实。

### 9.4 加注：`t30` 前门禁的**两个**盲区成因（入档）

1. **不读契约**：`verify_bst_sw_sequence.py` 原先 `setup-contract` / `aliasResolution` /
   `needsClosed` / `relaySet` / `K109` / `K110` 命中数**均为 0**；
2. **目标集不含 TM600**：其 `targets` 由 meta `powered_pins` 拓扑指纹派生 =
   `TM607/608/609/640`（ZCD 家族）⇒ **TM600 不在其中**；
   ⇒ **只加"读契约"而不改作用域，阳性对照仍是 `FAIL=0`**（我方实测，见 §2 第 3 行）。
   最终以 **`--tm-scope` 显式参数化**（默认 `TM600_HS_RDSON,TM601_LS_RDSON`）。

**边界**：以上均为静态连通性/登记层面的结论；**无机台实测**；**编译闭环 ≠ 电性签核**。
"""

MARK = '## 9. 加注：期望集合的前提依赖（Captain 裁定 2026-09-16）'
LEGACY = re.compile(r'\n*---\n+## 9\. 加注：期望集合的前提依赖.*\Z', re.S)
t0 = io.open(SUM, encoding='utf-8-sig').read()
io.open(SUM, 'w', encoding='utf-8', newline='').write(LEGACY.sub('', t0).rstrip() + BLOCK)
s = io.open(SUM, encoding='utf-8-sig').read()
print('\n=== 加注写入 t30-summary.md ===')
print('  %d B / %s' % (os.path.getsize(SUM), sha(SUM)))
print('  §9 出现次数 = %d（应为 1）' % s.count(MARK))
print('  含 pin-18 前提声明 = %s' % ('只成立于 pin-18 前提' in s))
print('  含 ACCEPT 边界声明 = %s' % ('不覆盖"pin 归属前提"的正确性' in s))
print('  含两个盲区成因 = %s' % ('两个**盲区成因' in s or '两个' in s and 'ZCD 家族' in s))
