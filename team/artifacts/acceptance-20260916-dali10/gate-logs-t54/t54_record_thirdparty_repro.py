# -*- coding: utf-8 -*-
"""按 setup-architect ③ 加 **stdout UTF-8 安全**（防第三方在 GBK locale 抓日志时解码中断）；
并把其**第三方独立复现**记入报告的实验字段。
"""
import ast
import io
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
T28 = os.path.abspath(os.path.join(HERE, '..', 'gate-logs-t28'))
GEN_A = os.path.join(T28, 't28_make_anchors.py')
GEN_R = os.path.join(HERE, 't54_make_report.py')

print('=== ① anchors 生成器：stdout UTF-8 安全 ===')
src = io.open(GEN_A, encoding='utf-8-sig').read()
ast.parse(src)
if 'reconfigure' in src:
    print('  已含（幂等）')
else:
    # 在首个 import 之后插入
    lines = src.splitlines(keepends=True)
    ins = 0
    for i, l in enumerate(lines):
        if l.startswith('import ') or l.startswith('from '):
            ins = i + 1
    lines.insert(ins, ("# 防第三方在 GBK locale 抓日志时解码中断（setup-architect ③）\n"
                       "try:\n"
                       "    sys.stdout.reconfigure(encoding='utf-8', errors='replace')\n"
                       "    sys.stderr.reconfigure(encoding='utf-8', errors='replace')\n"
                       "except Exception:\n"
                       "    pass\n"))
    out = ''.join(lines)
    ast.parse(out)
    io.open(GEN_A, 'w', encoding='utf-8', newline='').write(out)
    print('  已加入 reconfigure → %d B' % os.path.getsize(GEN_A))
ast.parse(io.open(GEN_A, encoding='utf-8-sig').read())
print('  语法 OK')

print('\n=== ② 报告：记入其"第三方独立复现" ===')
src2 = io.open(GEN_R, encoding='utf-8-sig').read()
ast.parse(src2)
if 'thirdPartyReproduction' in src2:
    print('  已含（幂等）')
else:
    ANCHOR = "        'restored': '实验后**已还原活档**（含 PROBE 检查 = False ⇒ 真源未被污染）。',"
    NEW = ('''        'thirdPartyReproduction': {
            'by': 'setup-architect（**在自己的离线副本上**独立复现，非只核日志）',
            'method': ('将其复制我方生成器到 scratch，**只改 2 行**（WS 工作区根 / 输出路径，均标 '
                       'PATCHED FOR OFFLINE PROBE），**并集逻辑一字未动**；'
                       '在离线副本上注入 3 条第三方前缀条目后跑一次并现算。'),
            'result': {'probeEntries': '3 → 3', 'peerEntries': '1 → 1',
                       'namespacesKept': ['qaProbeAnchors', 'setupArchitectFreezeAnchors']},
            'conclusion': ('**(ii)「不丢当前内容」＝第三方可复现**（我方实验 + 其方复现 ⇒ 同一结论两次独立成立）。'
                           '⚠️ **(iii) 仍不可测**（旧 8 条无字节）⇒ **双方都不得**把 (ii) 引作恢复历史。'),
            'note': ('其提示的改进已落地：我方生成器**现已支持 `--in`/`--out` 双重重定向** '
                     '⇒ 第三方将来可**零改动**复跑（无需复制+改 2 行）。'),
        },
''' + ANCHOR)
    if ANCHOR in src2:
        out2 = src2.replace(ANCHOR, NEW, 1)
        ast.parse(out2)
        io.open(GEN_R, 'w', encoding='utf-8', newline='').write(out2)
        print('  已记入 thirdPartyReproduction → %d B' % os.path.getsize(GEN_R))
    else:
        print('  WARN: 锚点未命中')
ast.parse(io.open(GEN_R, encoding='utf-8-sig').read())
print('  语法 OK')

for i in (1, 2):
    r = subprocess.run([sys.executable, GEN_R], capture_output=True, text=True, encoding='utf-8')
    tl = (r.stdout or '').strip().splitlines()
    print('  run%d 末行: %s' % (i, tl[-1][:60] if tl else (r.stderr or '')[:120]))

A = json.load(io.open(os.path.abspath(os.path.join(HERE, '..', 'build-report.json')), encoding='utf-8-sig'))
print('\n=== 自证 ===')
print('  报告含 thirdPartyReproduction =', 'thirdPartyReproduction' in A['unionPreservationExperiment'])
print('  报告 %d B ; verdict=%s' % (len(open(os.path.abspath(os.path.join(HERE, '..', 'build-report.json')), 'rb').read()), A['verdict']))

print('\n=== ③ 用 --in/--out 验证"零改动复跑"（不触碰活档）===')
LIVE = os.path.join(T28, 't28-anchors.json')
inp, outp = LIVE + '.z-in', LIVE + '.z-out'
open(inp, 'wb').write(open(LIVE, 'rb').read())
J = json.loads(open(inp, 'rb').read().decode('utf-8-sig'))
J.setdefault('preservedPeerNamespaces', {})['qaProbeAnchors'] = {'anchors': {f'Z-{i}.json': {'s': True} for i in (1, 2, 3)}}
open(inp, 'w', encoding='utf-8').write(json.dumps(J, ensure_ascii=False, indent=2))
before = __import__('hashlib').sha256(open(LIVE, 'rb').read()).hexdigest()
r = subprocess.run([sys.executable, GEN_A, '--in', inp, '--out', outp],
                   capture_output=True, text=True, encoding='utf-8')
print('  exit=%d ; stderr 长度=%d（应为 0 ⇒ UTF-8 安全生效）' % (r.returncode, len(r.stderr or '')))
K = json.loads(open(outp, 'rb').read().decode('utf-8-sig'))
pp = K.get('preservedPeerNamespaces') or {}
print('  qaProbeAnchors =', len((pp.get('qaProbeAnchors') or {}).get('anchors') or {}), '条（应 3）')
print('  setupArchitectFreezeAnchors 在 =', bool(pp.get('setupArchitectFreezeAnchors')))
after = __import__('hashlib').sha256(open(LIVE, 'rb').read()).hexdigest()
assert before == after
print('  活档 sha 前后一致 ✓（%s）' % after[:20])
for p in (inp, outp):
    os.remove(p)
