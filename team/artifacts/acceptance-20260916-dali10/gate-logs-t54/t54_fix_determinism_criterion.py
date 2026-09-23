# -*- coding: utf-8 -*-
"""修正我方的"幂等/可复现"判据：报告含 `generatedAt`（每次生成都变）⇒ **同秒内一致**只是巧合，
**跨秒必然不同字节**。正确判据＝**剔除 `generatedAt` 后的 body 哈希**（与 anchors 的
`anchorsObservedAt` 同一手法）。

落地：
  ① 收据加 `reproducibleBodySha256`（剔除 generatedAt 后重算）；
  ② `t54_postchange_verification.py` 的 C 组改为比较 **body 哈希**（跨秒仍应一致）；
  ③ 本脚本自证：两次生成（中间跨秒）⇒ 整文件哈希不同、**body 哈希相同**。
"""
import hashlib
import io
import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.abspath(os.path.join(HERE, '..'))
GEN = os.path.join(HERE, 't54_make_report.py')
P = os.path.join(RUN, 'build-report.json')
REC = os.path.join(HERE, 'build-report.receipt.json')
VER = os.path.join(HERE, 't54_postchange_verification.py')
TS_LINE = re.compile(r'^\s*"generatedAt": ".*?",\s*$', re.M)


def body_sha(b):
    t = TS_LINE.sub('', b.decode('utf-8-sig')).strip()
    return hashlib.sha256(t.encode('utf-8')).hexdigest()


print('=== ① 收据加 reproducibleBodySha256（生成器侧）===')
gt = io.open(GEN, encoding='utf-8-sig').read()
if 'reproducibleBodySha256' in gt:
    print('  生成器已含（幂等）')
else:
    OLD = "    'topLevelEntries': len(_json.loads(_b.decode('utf-8-sig'))),"
    NEW = (OLD + "\n    'reproducibleBodySha256': _hl.sha256(\n"
                  "        __import__('re').sub(r'^\\s*\"generatedAt\": \".*?\",\\s*$', '',\n"
                  "                            _b.decode('utf-8-sig'), flags=__import__('re').M).strip().encode('utf-8')\n"
                  "    ).hexdigest(),\n    'reproducibleNote': '剔除 generatedAt 后的 body 哈希 ⇒ 跨秒可复现判据'")
    if OLD in gt:
        io.open(GEN, 'w', encoding='utf-8', newline='').write(gt.replace(OLD, NEW, 1))
        print('  已加入 → %d B' % os.path.getsize(GEN))
    else:
        print('  WARN: 收据锚点未命中')

print('\n=== ② 自证：跨秒 generation ⇒ 整文件不同、body 相同 ===')
sigs = []
for i in (1, 2):
    subprocess.run([sys.executable, GEN], capture_output=True, text=True, encoding='utf-8')
    b = open(P, 'rb').read()
    sigs.append((len(b), hashlib.sha256(b).hexdigest(), body_sha(b)))
    time.sleep(1.2)          # 强制跨秒
print('  run1: %d B  file=%s  body=%s' % (sigs[0][0], sigs[0][1][:20], sigs[0][2][:20]))
print('  run2: %d B  file=%s  body=%s' % (sigs[1][0], sigs[1][1][:20], sigs[1][2][:20]))
print('  size 相同 =', sigs[0][0] == sigs[1][0])
print('  整文件哈希相同 =', sigs[0][1] == sigs[1][1])
print('  **body 哈希相同** =', sigs[0][2] == sigs[1][2], '⇒ 这才是正确的可复现判据')

print('\n=== ③ 改验证脚本 C 组为 body 哈希 ===')
vt = io.open(VER, encoding='utf-8-sig').read()
if 'body_sha' in vt:
    print('  已改（幂等）')
else:
    OLD = ("for i in (1, 2):\n"
           "    rr = subprocess.run([sys.executable, GEN], capture_output=True, text=True, encoding='utf-8')\n"
           "    if rr.returncode != 0:\n"
           "        chk('生成器 run%d 成功' % i, False, (rr.stderr or '')[:80])\n"
           "    b = open(rep, 'rb').read()\n"
           "    d = json.loads(b.decode('utf-8-sig'))\n"
           "    sigs.append((len(b), len(d.get('gateFailOpenForms', {}).get('forms', []))))\n"
           "chk('连跑两次 size 一致', sigs[0][0] == sigs[1][0], '%s' % (sigs,))")
    NEW = ("import re as _re\n"
           "_TS = _re.compile(r'^\\s*\"generatedAt\": \".*?\",\\s*$', _re.M)\n\n\n"
           "def _body_sha(bb):\n"
           "    return hashlib.sha256(_TS.sub('', bb.decode('utf-8-sig')).strip().encode('utf-8')).hexdigest()\n\n\n"
           "for i in (1, 2):\n"
           "    rr = subprocess.run([sys.executable, GEN], capture_output=True, text=True, encoding='utf-8')\n"
           "    if rr.returncode != 0:\n"
           "        chk('生成器 run%d 成功' % i, False, (rr.stderr or '')[:80])\n"
           "    b = open(rep, 'rb').read()\n"
           "    d = json.loads(b.decode('utf-8-sig'))\n"
           "    sigs.append((len(b), _body_sha(b), len(d.get('gateFailOpenForms', {}).get('forms', []))))\n"
           "chk('连跑两次 size 一致', sigs[0][0] == sigs[1][0], '%s' % (sigs[0][0],))\n"
           "chk('连跑两次 **body** 哈希一致（跨秒可复现）', sigs[0][1] == sigs[1][1],\n"
           "    'file=%s body=%s' % (sigs[0][1][:12], sigs[0][1][:12]))")
    if OLD in vt:
        io.open(VER, 'w', encoding='utf-8', newline='').write(vt.replace(OLD, NEW, 1))
        print('  已改 → %d B' % os.path.getsize(VER))
    else:
        print('  WARN: 验证脚本锚点未命中，将人工核对')

print('\n=== ④ 复验 ===')
r = subprocess.run([sys.executable, VER], capture_output=True, text=True, encoding='utf-8')
out = (r.stdout or '').strip().splitlines()
for l in out:
    if 'body' in l or 'size 一致' in l or '总判定' in l or 'FAIL 项' in l:
        print('  ' + l.strip())
