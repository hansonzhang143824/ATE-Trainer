# -*- coding: utf-8 -*-
"""按 schematic-expert ④ 的精度修正：**权威 ≠ 独立 ≠ 中立**。
契约为**权威输入**（门禁按构造读它），但**非独立/中立基准**（它是被撰写的产物，曾出错且多次漂移）。
"""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.join(HERE, 't54_make_report.py')
t = io.open(GEN, encoding='utf-8-sig').read()
print('生成器 %d B' % os.path.getsize(GEN))

OLD = ("        'neutralBaseline': {\n"
       "            'which': '`setup-contract.json`（FROZEN）',\n"
       "            'path': 'team/artifacts/acceptance-20260916-dali10/setup-contract.json',\n"
       "            'why': '契约是**权威输入**，非任何一方的自档 ⇒ 作中立基准',\n"
       "        },")
NEW = ("""        'baselineTriad': {
            'rule': ('**权威（门禁读它） ≠ 独立（无物校验它） ≠ 中立（它是被撰写且曾出错的产物）**；'
                     '⇒ 凡依赖契约的结论，**必须钉住其修订（现算 sha256）**。'),
            'authoritative': {
                'which': '`setup-contract.json`',
                'path': 'team/artifacts/acceptance-20260916-dali10/setup-contract.json',
                'why': '对**门禁**是**权威输入**（by construction：`verify_bst_sw_sequence.py` L372 就只读它）',
            },
            'notNeutralBecause': ('它**不是**中立/独立基准：`bst2sw.closedRelayNumbers` 在 **rev 24–28 期间是错的**'
                                  '（`[110,61]`）；且本 session 内走了 **24 → 39** 十几个修订'
                                  '⇒ 拿它当"中立基准"会把"某人写的值"误当"独立事实"。'),
            'corollary': ('**唯一能独立说明"某个历史修订里到底写了什么"的，是那次修订的字节快照**'
                          '（如 `backups/t53-20260916-211719/setup-contract.json` = rev 28 / `[110,61]`）；'
                          '**其余一切关于历史修订的说法都只是自述或推断**。'),
            'pairsWith': '本条与 `gateExpectationSet.residualCaveat` 是**同一条 epistemic 边界**，两条并列留档。',
        },""")
if "'baselineTriad'" in t:
    print('已修正（幂等）')
elif OLD in t:
    t = t.replace(OLD, NEW, 1)
    io.open(GEN, 'w', encoding='utf-8', newline='').write(t)
    print('  已改为 baselineTriad → %d B' % os.path.getsize(GEN))
else:
    print('  WARN: 锚点未命中，尝试宽松定位')
    i = t.find("'neutralBaseline'")
    print('  实际片段 =', repr(t[i - 20:i + 300]) if i > 0 else '（未找到）')

import subprocess
import sys
r = subprocess.run([sys.executable, GEN], capture_output=True, text=True, encoding='utf-8')
print('  重生成末行:', (r.stdout or '').strip().splitlines()[-1][:90] if r.stdout else r.stderr[:150])
