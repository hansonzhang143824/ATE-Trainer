# -*- coding: utf-8 -*-
"""按 setup-architect 转达的 `mirrorRecordIdentitySpec`（schematic-expert 提出）落地：
镜像记录须能回答"**镜像的是哪一份**" ⇒ 新增 **`mirroredContentSha256`**（**指称一个修订、不会过期**）。

理由（其四点实证，误差**变号** −2,775 → +42,516 → +54,861 → +61,730）：
**在 append-only 目标上，`size` 记录连"至少/至多"都推断不出 ⇒ 不能作任何比较基准**；
而**内容哈希无此问题**（它指称一个修订）。

边界：**只在"因别的原因写入该档时"顺带加**（少写一次＝少一次漂移）—— 本次即一次合并写入。
"""
import ast
import collections
import hashlib
import io
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.abspath(os.path.join(HERE, '..'))
T28 = os.path.abspath(os.path.join(HERE, '..', 'gate-logs-t28'))
GEN = os.path.join(T28, 't28_make_anchors.py')
LIVE = os.path.join(T28, 't28-anchors.json')
REG = os.path.join(RUN, 'gate-logs-t54', 't54-discipline-register.md')

src = io.open(GEN, encoding='utf-8-sig').read()
ast.parse(src)
print('前置：生成器语法 OK（%d B）' % len(src.encode('utf-8')))

OLD = ("                    merged['setupArchitectFreezeAnchors']['mirrorSizeAtMirrorTime'] = os.path.getsize(os.path.join(HERE, f))")
NEW = ("                    merged['setupArchitectFreezeAnchors']['mirrorSizeAtMirrorTime'] = os.path.getsize(os.path.join(HERE, f))\n"
       "                    # ⭐ 镜像记录须能回答『镜像的是哪一份』—— size **不能识别内容**（本 run 有『同尺寸三哈希』实证）；\n"
       "                    #    `mirroredContentSha256` **指称一个修订、不会因后续追加而过期**（size 会：误差甚至变号）\n"
       "                    merged['setupArchitectFreezeAnchors']['mirroredContentSha256'] = (\n"
       "                        __import__('hashlib').sha256(open(os.path.join(HERE, f), 'rb').read()).hexdigest())")
if 'mirroredContentSha256' in src:
    print('  已含（幂等）')
elif OLD in src:
    out = src.replace(OLD, NEW, 1)
    ast.parse(out)
    io.open(GEN, 'w', encoding='utf-8', newline='').write(out)
    print('  已加 mirroredContentSha256 → %d B' % os.path.getsize(GEN))
else:
    print('  WARN: 锚点未命中 (mirrorSizeAtMirrorTime 行)')

ast.parse(io.open(GEN, encoding='utf-8-sig').read())
print('后置：语法 OK')

r = subprocess.run([sys.executable, GEN], capture_output=True, text=True, encoding='utf-8')
print('顺带写入 exit=%d ; %s' % (r.returncode, (r.stdout or '').strip().splitlines()[0][:70] if r.stdout else r.stderr[:120]))
B = json.loads(open(LIVE, 'rb').read().decode('utf-8-sig'))
saa = (B.get('preservedPeerNamespaces') or {}).get('setupArchitectFreezeAnchors') or {}
print('\n=== 自证 ===')
print('  子键 =', list(saa.keys()))
print('  mirroredContentSha256 =', (saa.get('mirroredContentSha256') or '')[:32], '…')
print('  mirrorSizeAtMirrorTime =', saa.get('mirrorSizeAtMirrorTime'), '| mirrorAt =', saa.get('mirrorAt'))
print('  旧键 mirrorSize 已移除 =', 'mirrorSize' not in saa)
mir = os.path.join(T28, 'setupArchitect-freeze-snapshots.json')
print('  镜像现盘 = %d B ｜ **记录的内容哈希 == 现盘 = %s**'
      % (os.path.getsize(mir),
         saa.get('mirroredContentSha256') == hashlib.sha256(open(mir, 'rb').read()).hexdigest()))
print('  （size 记录 175,358 vs 现盘 %d ⇒ **误差符号不定、不能作比较基准** → 故补内容哈希）'
      % os.path.getsize(mir))

print('\n=== 规则入册 ===')
MARK = '## 附二十｜镜像记录须能回答"镜像的是哪一份"（内容哈希，非 size）'
t = io.open(REG, encoding='utf-8-sig').read()
if MARK in t:
    print('  已并入（幂等）')
else:
    BLOCK = '''

---

''' + MARK + '''

**来源**：setup-architect 转达 schematic-expert 的增修建议（规范名 `mirrorRecordIdentitySpec`，其侧 `knownSpecsRegister` 第 5 项）。

**问题**：镜像记录用 `(size, at)` **回答不了"镜像的是哪一份"** ——
**size 不能识别内容**（本 run 已有"**同尺寸三哈希**"实证）。

**四点实证（误差**变号**）**
```
同一记录值对目标的四次测量 ⇒ 误差：**−2,775 → +42,516 → +54,861 → +61,730**
⇒ 误差**变号** ⇒ 在 **append-only** 目标上，`size` 记录**连"至少/至多"都推断不出**
⇒ **非精度问题，而是不能作任何比较基准** ✓
而 **内容哈希没有这个问题**（它**指称一个修订**，不会因后续追加而"过期"）✓
```

**规则**
> 镜像记录须含 **`mirroredContentSha256`**（镜像时刻被镜像内容的哈希）——
> **回答"镜像的是哪一份"，命名一个修订、永不过期**。

**判据（同族）**：**指路信息（路径/owner/权限/版本要求）可硬记；被指对象的度量不得硬记，除非自陈为快照。**

**落地边界**：**只在"因别的原因写入该档时"顺带加**（少写一次＝少一次漂移）。
'''
    io.open(REG, 'w', encoding='utf-8', newline='').write(t.rstrip() + BLOCK)
    print('  已并入 → %d B' % os.path.getsize(REG))

hs = [l.strip() for l in io.open(REG, encoding='utf-8-sig').read().splitlines() if l.strip().startswith('#')]
c = collections.Counter(hs)
print('  登记 = %d B ｜ 标题 %d ｜ 唯一 %d ｜ 重复 %s'
      % (os.path.getsize(REG), len(hs), len(c), [k for k, v in c.items() if v > 1] or '无'))
