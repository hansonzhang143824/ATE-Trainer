# -*- coding: utf-8 -*-
"""落实 rule-reviewer ③ 的**双哈希**建议：以 JSON/文本作身份依据处，除 `sha256(bytes)` 外
另记 `sha256(LF-normalized)`（`b.replace(b"\r\n", b"\n")`）。

落地三处：
  ① 快照账本：后续行加 `live_lf_sha256`（**既有行不改**，回头改会破坏"只增不改"）；
  ② 账本头文件：加 `hashPolicy`；
  ③ 纪律登记：加"双哈希"条，并把 CRLF 差异的**归属**写准（我账本最早记录为 11,931，
     故"11,854 是同一文件的更早瞬间"属**推断**而非实测 —— 该更早态**无字节副本**）。
"""
import datetime
import hashlib
import io
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.abspath(os.path.join(HERE, '..'))
J = os.path.join(HERE, 't28-anchors.snapshots.jsonl')
META = os.path.join(HERE, 't28-anchors.snapshots.meta.json')
LIVE = os.path.join(HERE, 't28-anchors.json')
REG = os.path.join(RUN, 'gate-logs-t54', 't54-discipline-register.md')
TS_LINE = re.compile(r'^\s*"anchorsObservedAt": ".*",\s*$', re.M)


def sha_b(b):
    return hashlib.sha256(b).hexdigest()


def lf(b):
    return b.replace(b'\r\n', b'\n')


print('=== ① 账本：头部加 hashPolicy，并追加一条带双哈希的行 ===')
meta = json.load(io.open(META, encoding='utf-8-sig'))
meta['hashPolicy'] = ('同一内容跨换行策略可比：除 `sha256(bytes)` 外另记 `sha256(LF-normalized)`'
                      '（`bytes.replace(b"\\r\\n", b"\\n")`）。换行是**序列化产物、不是内容**；'
                      '实算哈希保留"字节级不同"，归一化哈希判定"同一内容"。两者并列。')
io.open(META, 'w', encoding='utf-8').write(json.dumps(meta, ensure_ascii=False, indent=2))
print('  meta 已加 hashPolicy → %d B' % os.path.getsize(META))

lines = io.open(J, encoding='utf-8').read().strip().splitlines()
b = open(LIVE, 'rb').read()
body = TS_LINE.sub('', io.open(LIVE, encoding='utf-8-sig').read()).strip().encode('utf-8')
rec = {
    'at': datetime.datetime.now().astimezone().isoformat(timespec='seconds'),
    'reason': 'dual-hash-enabled (rule-reviewer LF-normalized suggestion)',
    'live_size': len(b),
    'live_sha256': sha_b(b),
    'live_lf_sha256': sha_b(lf(b)),
    'live_body_sha256': sha_b(body),
    'entries': len(json.loads(io.open(LIVE, encoding='utf-8-sig').read())['anchors']),
    'preservedPeerKeys': list((json.loads(io.open(LIVE, encoding='utf-8-sig').read())
                               .get('preservedPeerNamespaces') or {}).keys()),
    'lineCount': len(lines) + 1,
    'prevLineSha256': sha_b(lines[-1].encode('utf-8')),
}
io.open(J, 'a', encoding='utf-8').write(json.dumps(rec, ensure_ascii=False) + '\n')
print('  已追加双哈希行 → 账本 %d 行' % len(io.open(J, encoding='utf-8').read().strip().splitlines()))
print('    live_sha256 = %s…' % rec['live_sha256'][:24])
print('    live_lf_sha256 = %s…' % rec['live_lf_sha256'][:24])

print('\n=== ② 纪律登记：加"双哈希"条 + 把 CRLF 归属写准 ===')
MARK = '### 纪律 2·补：双哈希（bytes 与 LF-normalized 并列）'
t = io.open(REG, encoding='utf-8-sig').read()
if MARK in t:
    print('  已并入（幂等）')
else:
    BLOCK = '''

''' + MARK + '''

> **凡以 JSON/文本作为"身份"依据处，除 `sha256(bytes)` 外，另记 `sha256(LF-normalized)`**（`b.replace(b"\\r\\n", b"\\n")`）。
> **判据**：**换行是序列化产物、不是内容** ⇒ 归一化哈希使"同一内容"**跨换行策略可比**；
> 实算哈希仍保留"字节级不同"的信息。**两者并列 = 既可判"同一内容"，也可判"同一字节"。**

**实测示例（本 run）**
| 对象 | `sha256(bytes)` | `sha256(LF-normalized)` |
| --- | --- | --- |
| `gate-logs-t28/t28-anchors.json`（CRLF=247 / lone LF=0） | `38ba37b2…` | `ce256e6e…`（**不同** ⇒ 换行策略参与字节） |
| `gate-logs-t33/t33-postreplace-expectation-live.log`（全程 LF） | `c6080f50…` | `c6080f50…`（**相同** ⇒ 无 CRLF） |

**归因写准（我方自查）**：`setup-architect` 早前测该文件为 **11,854 B / CRLF 245**、我测 **11,931 B / CRLF 247**。
- ✅ **可确证**：两者 **entries 均为 32**，且现盘为 247 CRLF / 0 lone LF ⇒ 差异**只可能来自"内容或换行其一"**；
- ⚠️ **属推断（非实测）**："**11,854 是同一文件的更早瞬间**" —— 我账本最早记录已是 **11,931**，
  那个更早态**无字节副本** ⇒ **不可复核**（又一次纪律 3 的实例）。
⇒ 采用双哈希后，此类"同内容/同字节"之争**可当场判定**，无需再推断。
'''
    io.open(REG, 'w', encoding='utf-8', newline='').write(t.rstrip() + BLOCK)
    t2 = io.open(REG, encoding='utf-8-sig').read()
    print('  已并入: %d B' % os.path.getsize(REG))
    for k in (MARK, 'LF-normalized', '换行是序列化产物', '属推断（非实测）'):
        print('    含 %-22s %s' % (k, k in t2))
