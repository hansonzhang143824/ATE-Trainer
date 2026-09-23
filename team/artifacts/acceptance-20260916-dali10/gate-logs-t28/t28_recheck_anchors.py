# -*- coding: utf-8 -*-
"""回应 rule-reviewer：逐条现算复核其 ①③ 与"我随后是否又动过 t28-summary.md"。

他用 mtime 20:03:18 测得 t28-summary.md = 17,690 B —— 但我在 20:0x 之后为 §8 又写入过一次（幂等定稿）。
故须现算：若尺寸/哈希已变，需向他说清"变了什么、为何、是否仍在冻结口径内"。
"""
import hashlib
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))


def info(label, rel, expect_size=None, expect_sha=None):
    p = rel if os.path.isabs(rel) else os.path.join(WS, rel)
    d = open(p, 'rb').read()
    h = hashlib.sha256(d).hexdigest()
    flag = ''
    if expect_size is not None:
        flag = '  ← 与对方实测%s' % ('一致' if (len(d) == expect_size and (expect_sha is None or h == expect_sha)) else '**不一致**')
    print('  %-30s %8d B  %s  mtime=%s%s'
          % (label, len(d), h, __import__('datetime').datetime.fromtimestamp(
              os.path.getmtime(p)).strftime('%H:%M:%S'), flag))
    return len(d), h


print('=== ① 对方引用的六项 + t28-summary（全部现算）===')
info('t28-summary.md', 'team/artifacts/acceptance-20260916-dali10/gate-logs-t28/t28-summary.md', 17690)
info('t28-red-proof.json', 'team/artifacts/acceptance-20260916-dali10/gate-logs-t28/t28-red-proof.json', 5351)
info('redproof-after-fix.log', 'team/artifacts/acceptance-20260916-dali10/gate-logs-t28/redproof-after-fix.log', 6377)
info('redproof-before-fix.log', 'team/artifacts/acceptance-20260916-dali10/gate-logs-t28/redproof-before-fix.log', 1317)
print('  --- 关键一行：对方用"命令机械取得"的正确值 ---')
s, h = info('check_input_sync.py', 'scripts/check_input_sync.py', 17455)
ok = (h == 'e804c459b2d3088e72d455eb9e1b7893119cea47ad0a640735b6f5db42d784d1')
print('      sha256 与对方机械取得值逐位一致 = %s ; 长度=%d' % (ok, len(h)))
info('gate_baseline.json', 'scripts/gate_baseline.json', 28)
info('build-report.json', 'team/artifacts/acceptance-20260916-dali10/build-report.json', 13075)

print('\n=== ② t28-freeze-correction.md 是否已含对方建议的纪律原句 ===')
p = os.path.join(WS, 'team/artifacts/acceptance-20260916-dali10/gate-logs-t28/t28-freeze-correction.md')
t = io.open(p, encoding='utf-8-sig').read()
for key in ('任何被引用的哈希必须由脚本从产物直接 `sha256(file)` 取得并回填',
            '禁止手打，禁止在报告里手拼 expected 值作核对基准'):
    print('  含 "%s" = %s' % (key[:34], key in t))

print('\n=== ③ 我随后改过哪些文件（报告类 vs 被审对象）===')
for rel in ('team/artifacts/acceptance-20260916-dali10/gate-logs-t30/t30-summary.md',
            'team/artifacts/acceptance-20260916-dali10/gate-logs-t33/t33-revision-attribution.md',
            'team/artifacts/acceptance-20260916-dali10/gate-logs-t33/t33-transition-plan.md'):
    info(os.path.basename(rel), rel)
