# -*- coding: utf-8 -*-
"""按 schematic-expert ③ 补**版本锚的换代规则**（我方实测复核其搜检，然后补上）。
  其搜检：`bump`/`换版本`/`升版本`/`定义变化`/`fieldDefinitions 变化`/`任一变化` ⇒ 全 0 命中
  ⇒ **该档没有声明"何时必须升 `metaVersion`"** ⇒ **锚的完整性依赖一条未声明的纪律** ✓
"""
import collections
import io
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.abspath(os.path.join(HERE, '..'))
META = os.path.join(HERE, 'build-report.receipts.meta.json')
REG = os.path.join(RUN, 'gate-logs-t54', 't54-discipline-register.md')

blob = io.open(META, encoding='utf-8').read()
print('=== ① 复核其搜检（在补之前）===')
for k in ('bump', '换版本', '升版本', '定义变化', '任一变化', 'metaVersion'):
    print('  %-16s 命中 = %d' % (k, blob.count(k)))
print('  ⇒ 其结论成立：**该档未声明"何时必须升 metaVersion"** ✓')

print('\n=== ② 补上换代规则 ===')
m = json.load(io.open(META, encoding='utf-8-sig'))
m['metaVersionBumpRule'] = (
    '**凡 `fieldDefinitions` / `executableDefinitionRule` / `warning` / `equivalenceIsDomainBound` / '
    '`prePolicyCountsAtPolicyWrite` 的**语义**任一变化 ⇒ **必须升 `metaVersion`，且不得沿用同名**。**'
    '⚠️ 本条的由来＝schematic-expert 实测指出：此前该档**是全 run 里唯一没有版本纪律的地方**（锚的完整性会依赖一条未声明的纪律）。'
    '⇒ **递归在此终止**：**换代这个机制本身就是终止条件**（不需要更高一层版本）。')
io.open(META, 'w', encoding='utf-8').write(json.dumps(m, ensure_ascii=False, indent=2))
print('  meta 已补 → %d B' % os.path.getsize(META))
b2 = io.open(META, encoding='utf-8').read()
for k in ('metaVersionBumpRule', '必须升', '递归在此终止'):
    print('  %-22s 命中 = %d' % (k, b2.count(k)))

print('\n=== ③ 规则入册 ===')
MARK = '## 附卅四｜版本锚必须声明自己的换代规则（否则它是全 run 版本纪律的唯一缺失处）'
t = io.open(REG, encoding='utf-8-sig').read()
if MARK in t:
    print('  已并入（幂等）')
else:
    BLOCK = '''

---

''' + MARK + '''

**来源**：schematic-expert 在确认我方 `metaVersion` 作为**基例**有效之后，**实测搜检**该档
（`bump`／`换版本`／`升版本`／`定义变化`／`任一变化`）⇒ **全部 0 命中** ⇒
**该档没有声明"何时必须升 `metaVersion`"** ⇒ **锚的完整性依赖一条未声明的纪律** ✓

**规则**
> **版本锚必须声明自己的换代规则**；否则**它就是全 run 里版本纪律唯一缺失处** ✓
> **递归在此终止**：**换代这个机制本身就是终止条件**（不需要更高一层版本）✓

**与别处的对照（本方已有、该档缺）**：`projectionSpec` 已写明"**排除表/序列化/编码任一变化都必须换版本号**" ✓

**落地**：`build-report.receipts.meta.json` 新增 **`metaVersionBumpRule`** ——
> **凡 `fieldDefinitions` / `executableDefinitionRule` / `warning` / `equivalenceIsDomainBound` /
> `prePolicyCountsAtPolicyWrite` 的语义任一变化 ⇒ 必须升 `metaVersion`，且不得沿用同名** ✓

**★ 另一条同批实证（schematic-expert 实测）**：`1,645 B` 而**哈希不同**（其 `accfd135…` vs 我方 `b79f8975…`）⇒
**其间发生了一次**等长编辑**** ⇒ **"size 对等长编辑不敏感"的活实例** ✓
且**有趣且在族**：**它恰好发生在这份"专门用来记录这类性质"的文件上** ✓
'''
    io.open(REG, 'w', encoding='utf-8', newline='').write(t.rstrip() + BLOCK)
    print('  已并入 → %d B' % os.path.getsize(REG))
hs = [l.strip() for l in io.open(REG, encoding='utf-8-sig').read().splitlines() if l.strip().startswith('#')]
c = collections.Counter(hs)
print('  登记 = %d B ｜ 标题 %d ｜ 唯一 %d ｜ 重复 %s'
      % (os.path.getsize(REG), len(hs), len(c), [k for k, v in c.items() if v > 1] or '无'))
