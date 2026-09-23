# -*- coding: utf-8 -*-
"""按 setup-architect 转达的 reviewer 规范**补全**对照实验（我方已按 (i)(ii)(iii) 执行过一次）：
缺项：① 生成器版本（mtime/hash）；② 可选的"更强变体"（只放 **1 条**第三方前缀条目 ⇒ 必须存活）。

安全：全程在离线副本；结束时**还原活档**并自证无污染。
"""
import datetime
import hashlib
import io
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
T28 = os.path.abspath(os.path.join(HERE, '..', 'gate-logs-t28'))
LIVE = os.path.join(T28, 't28-anchors.json')
GEN = os.path.join(T28, 't28_make_anchors.py')
LOG = os.path.join(HERE, 't54-reviewer-experiment-union-variant.log')
PROBE = 'qaProbeAnchors'


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


lines = []


def say(s):
    print(s)
    lines.append(s)


say('=== 规范补全：生成器版本 + 可选"更强变体"（只放 1 条）===')
say('at = %s' % datetime.datetime.now().astimezone().isoformat(timespec='seconds'))
say('')
say('--- 生成器版本（reviewer 要求回报）---')
say('  path  = gate-logs-t28/t28_make_anchors.py')
say('  size  = %d B' % os.path.getsize(GEN))
say('  sha256= %s' % sha(GEN))
say('  mtime = %s' % datetime.datetime.fromtimestamp(os.path.getmtime(GEN)).isoformat(timespec='seconds'))
say('--- 离线副本（共享活档）---')
say('  size  = %d B' % os.path.getsize(LIVE))
say('  sha256= %s（副本起点，注入前）' % sha(LIVE)[:32] + '…')

bak = LIVE + '.variantbak'
shutil.copy2(LIVE, bak)
try:
    A = json.loads(open(LIVE, 'rb').read().decode('utf-8-sig'))
    pp = A.setdefault('preservedPeerNamespaces', {})
    sa_before = len((pp.get('setupArchitectFreezeAnchors') or {}).get('anchors') or {})
    # 更强变体：**只放 1 条**第三方前缀条目
    pp[PROBE] = {'anchors': {'VARIANT-ONLY-1.json': {'sentinel': True}}}
    io.open(LIVE, 'w', encoding='utf-8').write(json.dumps(A, ensure_ascii=False, indent=2))
    say('')
    say('--- 注入（1 条，第三方前缀 %s）---' % PROBE)
    say('  注入前：%s.anchors = 1 条（本行注入）｜ setupArchitectFreezeAnchors.anchors = %d 条' % (PROBE, sa_before))
    say('  副本注入后 size = %d B' % os.path.getsize(LIVE))

    r = subprocess.run([sys.executable, GEN], capture_output=True, text=True, encoding='utf-8')
    say('')
    say('--- 跑生成器 ---')
    say('  exit=%d' % r.returncode)
    for l in (r.stdout or '').strip().splitlines()[:2]:
        say('  ' + l.strip())

    B = json.loads(open(LIVE, 'rb').read().decode('utf-8-sig'))
    pp2 = B.get('preservedPeerNamespaces') or {}
    got = len((pp2.get(PROBE) or {}).get('anchors') or {})
    sa_after = len((pp2.get('setupArchitectFreezeAnchors') or {}).get('anchors') or {})
    say('')
    say('--- 跑后现算 ---')
    say('  %s.anchors = %d 条 ⇒ **1 条存活 = %s**' % (PROBE, got, got == 1))
    say('  setupArchitectFreezeAnchors.anchors = %d 条 ⇒ 仍在 = %s' % (sa_after, sa_after == sa_before))
    say('  副本跑后 size = %d B' % os.path.getsize(LIVE))
    say('')
    say('--- 判据（照 reviewer 与你的措辞）---')
    say('  本变体证明的是 **(ii) 不丢当前内容**（第三方前缀同样走并集累积路径）。')
    say('  ⚠️ **不得**引作 **(iii) 恢复历史** 的证据 —— 那 8 条已无字节、**原理上不可测**。')
    say('  ⚠️ 本变体**不构成**与"旧版压成单键"的直接对照（无旧版生成器可运行）⇒ 该对照**未执行**。')
finally:
    shutil.copy2(bak, LIVE)
    os.remove(bak)
    V = json.loads(open(LIVE, 'rb').read().decode('utf-8-sig'))
    say('')
    say('--- 已还原活档 ---')
    say('  size = %d B ｜ entries = %d ｜ 含 VARIANT/probe = %s ｜ 他方条数 = %d'
        % (os.path.getsize(LIVE), len(V['anchors']),
           ('VARIANT' in json.dumps(V, ensure_ascii=False) or PROBE in json.dumps(V, ensure_ascii=False)),
           len((V.get('preservedPeerNamespaces') or {}).get('setupArchitectFreezeAnchors', {}).get('anchors') or {})))

io.open(LOG, 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
print('\nWROTE %s (%d B)' % (LOG, os.path.getsize(LOG)))
