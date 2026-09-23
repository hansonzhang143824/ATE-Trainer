# -*- coding: utf-8 -*-
"""修：把"外部哈希收据"逻辑真正追加到生成器末尾（上次因字符串已存在于声明文本而被误判跳过）。"""
import io
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.join(HERE, 't54_make_report.py')
SENTINEL = 'RECEIPT_WRITER_V1'
t = io.open(GEN, encoding='utf-8-sig').read()
print('生成器 %d B ; 已含收据写入器 = %s' % (os.path.getsize(GEN), SENTINEL in t))
if SENTINEL not in t:
    TAIL = '''

# ==== RECEIPT_WRITER_V1：外部哈希收据（报告为活档，自引用哈希会过期）====
import datetime as _dt
import hashlib as _hl
import json as _json
_rep_p = os.path.join(RUN, 'build-report.json')
_b = open(_rep_p, 'rb').read()
_rec = {
    'subject': 'team/artifacts/acceptance-20260916-dali10/build-report.json',
    'at': _dt.datetime.now().astimezone().isoformat(timespec='seconds'),
    'size': len(_b),
    'sha256': _hl.sha256(_b).hexdigest(),
    'sha256_lf_normalized': _hl.sha256(_b.replace(b"\\r\\n", b"\\n")).hexdigest(),
    'topLevelEntries': len(_json.loads(_b.decode('utf-8-sig'))),
    'isFrozen': False,
    'note': '报告为**活档**；本收据每次生成后重算。引用某一版身份请用本文件，勿用报告内的自算哈希。',
}
_rec_p = os.path.join(RUN, 'gate-logs-t54', 'build-report.receipt.json')
open(_rec_p, 'w', encoding='utf-8').write(_json.dumps(_rec, ensure_ascii=False, indent=2))
print('RECEIPT %s (%d B)' % (_rec_p, os.path.getsize(_rec_p)))
'''
    io.open(GEN, 'a', encoding='utf-8', newline='').write(TAIL)
    print('  已追加 → %d B' % os.path.getsize(GEN))

for i in (1, 2):
    r = subprocess.run([sys.executable, GEN], capture_output=True, text=True, encoding='utf-8')
    tail = (r.stdout or '').strip().splitlines()
    print('  run%d 末行: %s' % (i, tail[-1][:100] if tail else (r.stderr or '')[:120]))

REC = os.path.join(HERE, 'build-report.receipt.json')
print('\n=== 收据核对 ===')
print('  存在 =', os.path.isfile(REC))
if os.path.isfile(REC):
    import hashlib
    import json
    rec = json.load(io.open(REC, encoding='utf-8-sig'))
    rep = os.path.abspath(os.path.join(HERE, '..', 'build-report.json'))
    b = open(rep, 'rb').read()
    print('  收据 size=%d ; 现盘 size=%d ; 一致=%s' % (rec['size'], len(b), rec['size'] == len(b)))
    print('  收据 sha256 一致 =', rec['sha256'] == hashlib.sha256(b).hexdigest())
    print('  isFrozen =', rec.get('isFrozen'))
    print('  topLevelEntries =', rec['topLevelEntries'])
