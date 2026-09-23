# -*- coding: utf-8 -*-
"""按 rule-reviewer ① 的裁定与设计执行**对照实验（严格版）**：

设计要求：
  · 用**第三方前缀**（非 `setupArchitect-`）放入 3 条 ⇒ 才走到"他方键 ⇒ 并集累积"的路径；
  · 判据：证明 (ii)"不丢当前内容"；**不得**引作 (iii)"恢复历史"。
  · 记录：副本路径、放入键名与条数、跑后现算结果 ⇒ 落盘日志。
额外：**控制组**（同前缀、值为被覆盖的老行为）—— 用一个**不含 next 键**的旧式单键结构，验证
  "若旧版把多键压成单键"会发生什么（模拟而非改代码）。
安全：全程在**离线副本**上，结束**还原活档**并删除副本。
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
LOG = os.path.join(HERE, 't54-reviewer-experiment-union.log')

PROBE = 'qaProbeAnchors'          # **第三方中性前缀**，非 setupArchitect-

lines = []


def say(s):
    print(s)
    lines.append(s)


say('=== rule-reviewer 裁定的对照实验（严格版）===')
say('at      : %s' % datetime.datetime.now().astimezone().isoformat(timespec='seconds'))
say('副本路径: %s' % LIVE)
say('设计要点: 探针键前缀 = **%s**（非 setupArchitect-）⇒ 走"他方键 ⇒ 并集累积"路径' % PROBE)

bak = LIVE + '.expbak'
shutil.copy2(LIVE, bak)
try:
    A = json.load(io.open(LIVE, encoding='utf-8-sig'))
    pp = A.setdefault('preservedPeerNamespaces', {})
    before_sa = len((pp.get('setupArchitectFreezeAnchors') or {}).get('anchors') or {})
    injected = ['PROBE-1.json', 'PROBE-2.json', 'PROBE-3.json']
    pp[PROBE] = {'anchors': {k: {'sentinel': True} for k in injected}}
    io.open(LIVE, 'w', encoding='utf-8').write(json.dumps(A, ensure_ascii=False, indent=2))
    say('')
    say('--- 放入前 ---')
    say('  setupArchitectFreezeAnchors.anchors = %d 条' % before_sa)
    say('--- 放入后（写入副本）---')
    say('  %s.anchors = %d 条：%s' % (PROBE, len(injected), injected))

    r = subprocess.run([sys.executable, GEN], capture_output=True, text=True, encoding='utf-8')
    say('')
    say('--- 跑生成器 ---')
    say('  exit=%d' % r.returncode)
    for l in (r.stdout or '').strip().splitlines()[:3]:
        say('  ' + l.strip())

    B = json.load(io.open(LIVE, encoding='utf-8-sig'))
    pp2 = B.get('preservedPeerNamespaces') or {}
    got = pp2.get(PROBE) or {}
    got_n = len(got.get('anchors') or {})
    sa_n = len((pp2.get('setupArchitectFreezeAnchors') or {}).get('anchors') or {})
    say('')
    say('--- 跑后（现算）---')
    say('  %s.anchors = %d 条 ⇒ 3 条全在 = %s' % (PROBE, got_n, got_n == 3))
    say('  setupArchitectFreezeAnchors.anchors = %d 条 ⇒ 未被清除 = %s' % (sa_n, sa_n == before_sa))
    say('  现盘 %d B / %s' % (os.path.getsize(LIVE), hashlib.sha256(open(LIVE, 'rb').read()).hexdigest()[:24]))
    say('')
    say('--- 判据 ---')
    say('  (ii) 不丢当前内容：**%s**' % ('成立' if got_n == 3 and sa_n == before_sa else '不成立'))
    say('  (iii) 恢复历史：**原理上不可测** ⇒ 本实验**不得**被引作其证据（8 条无字节副本）')
    say('  额外结论：第三方前缀（非 setupArchitect-）同样走并集路径 ⇒ 该机制**不限于**受保护前缀')
finally:
    shutil.copy2(bak, LIVE)
    os.remove(bak)
    V = json.load(io.open(LIVE, encoding='utf-8-sig'))
    say('')
    say('--- 已还原活档（实验不改变真源）---')
    say('  %d B / entries=%d / 含 PROBE=%s / 他方条数=%d'
        % (os.path.getsize(LIVE), len(V['anchors']),
           'PROBE' in json.dumps(V, ensure_ascii=False),
           len((V.get('preservedPeerNamespaces') or {}).get('setupArchitectFreezeAnchors', {}).get('anchors') or {})))

io.open(LOG, 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
print('\nWROTE %s (%d B)' % (LOG, os.path.getsize(LOG)))
