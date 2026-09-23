# -*- coding: utf-8 -*-
"""🔴 关键发现（我自测出、并据此修）：**`projectionSpec v1` 不完整** ——
报告里含 `receipts`（仅 `at/lineCount` 变），故 `reproducibleBodySha256` **并不真的稳定**：
每跑一次生成器 ⇒ 追加一条 receipt ⇒ 报告字节变 ⇒ **整文件 sha 变** ⇒ 而我实测
`reproducibleBodySha256` **未变**（说明它此刻"看起来稳"），但**history 行的 sha256 确实在变**。

⇒ 正确修法：**projectionSpec v2 = 排除 `generatedAt` + `receipts`**（值会变且与"内容"无关的整块），
   并把 `version` 升为 **2**（按我们自己的纪律：排除表一变就必须换版本号）。
"""
import ast
import hashlib
import io
import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.join(HERE, 't54_make_report.py')
REPORT = os.path.abspath(os.path.join(HERE, '..', 'build-report.json'))
REC = os.path.join(HERE, 'build-report.receipt.json')

src = io.open(GEN, encoding='utf-8-sig').read()
ast.parse(src)
print('前置：语法 OK（%d B）' % len(src.encode('utf-8')))
print('现盘报告里是否有 receipts 顶层键 =', 'receipts' in json.load(io.open(REPORT, encoding='utf-8-sig')))

# 1) body 投影改为同时排除 generatedAt 与 receipts（用 json 重序列化更稳）
OLD_BODY = ("    'reproducibleBodySha256': _hl.sha256(\n"
            "        __import__('re').sub(r'^\\s*\"generatedAt\": \".*?\",\\s*$', '',\n"
            "                            _b.decode('utf-8-sig'), flags=__import__('re').M).strip().encode('utf-8')\n"
            "    ).hexdigest(),")
NEW_BODY = ("    'reproducibleBodySha256': _hl.sha256(\n"
            "        _json.dumps(\n"
            "            {k: v for k, v in _json.loads(_b.decode('utf-8-sig')).items()\n"
            "             if k not in ('generatedAt', 'receipts')},\n"
            "            ensure_ascii=False, sort_keys=True).encode('utf-8')\n"
            "    ).hexdigest(),")
if 'k not in (\'generatedAt\', \'receipts\')' in src:
    print('  body 投影已 v2（幂等）')
elif OLD_BODY in src:
    src = src.replace(OLD_BODY, NEW_BODY, 1)
    print('  已改 body 投影为 v2')
else:
    print('  WARN: body 锚点未命中')

# 2) projectionSpec / reproducibleNote 升版
OLD_PS = "        'exclude': ['generatedAt'],\n        'version': 1,"
NEW_PS = "        'exclude': ['generatedAt', 'receipts'],\n        'version': 2,"
if NEW_PS in src:
    print('  projectionSpec 已 v2（幂等）')
elif OLD_PS in src:
    src = src.replace(OLD_PS, NEW_PS, 1)
    print('  已改 projectionSpec 为 v2')
else:
    print('  WARN: projectionSpec 锚点未命中')

OLD_NOTE = "'reproducibleNote': '剔除 generatedAt 后的 body 哈希 ⇒ 跨秒可复现判据'"
NEW_NOTE = ("'reproducibleNote': ('剔除 `generatedAt` 与 **`receipts`**（后者含变化中的 at/lineCount）后的 body 哈希；'\n"
            "                        '**projectionSpec v2** ⇒ 跨次生成应稳定（v1 只排 generatedAt ⇒ 不稳定，已废弃）')")
if 'projectionSpec v2' in src:
    print('  reproducibleNote 已升版（幂等）')
elif OLD_NOTE in src:
    src = src.replace(OLD_NOTE, NEW_NOTE, 1)
    print('  已改 reproducibleNote')
else:
    print('  WARN: note 锚点未命中')

ast.parse(src)
io.open(GEN, 'w', encoding='utf-8', newline='').write(src)
print('  生成器 → %d B' % os.path.getsize(GEN))

print('\n=== 自证：跨秒跑两次，body 哈希应**稳定** ===')
sigs = []
for i in (1, 2):
    subprocess.run([sys.executable, GEN], capture_output=True, text=True, encoding='utf-8')
    r = json.load(io.open(REC, encoding='utf-8-sig'))
    sigs.append((r['size'], r['sha256'][:16], r['reproducibleBodySha256'][:16],
                 r['projectionSpec']['version'], r['projectionSpec']['exclude']))
    time.sleep(1.3)
print('  run1: size=%s file=%s body=%s v=%s exclude=%s' % sigs[0])
print('  run2: size=%s file=%s body=%s v=%s exclude=%s' % sigs[1])
print('  整文件 sha 相同 =', sigs[0][1] == sigs[1][1], '（预期 False：报告含 receipts/generatedAt）')
print('  **body 哈希相同 = %s**' % (sigs[0][2] == sigs[1][2]), '（预期 True：v2 已排除 receipts）')
