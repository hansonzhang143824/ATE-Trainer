# -*- coding: utf-8 -*-
"""生成 t28/t30 稳定锚点清单（单一真源，供引用方直接读取，杜绝手抄哈希）。

输出: t28-anchors.json —— 每条含 path / size / sha256 / readAt / note(DELIVERED 或 DEPLOYED 等语义)。
"""
import datetime
import hashlib
import io
import json
import os
import re
import sys
# 防第三方在 GBK locale 抓日志时解码中断（setup-architect ③）
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
RUN = os.path.join(WS, 'team', 'artifacts', 'acceptance-20260916-dali10')

ENTRIES = [
    ('t28 被审脚本', 'scripts/check_input_sync.py', 'RS-1..RS-4 断言；t28 ACCEPT 锚点'),
    ('t28 红证证据', 'team/artifacts/acceptance-20260916-dali10/gate-logs-t28/t28-red-proof.json', 'redProofPassed=true'),
    ('t28 红态日志(AFTER)', 'team/artifacts/acceptance-20260916-dali10/gate-logs-t28/redproof-after-fix.log', '47 行；含 6 条 RS-FAIL 相关行'),
    ('t28 绿态日志(BEFORE)', 'team/artifacts/acceptance-20260916-dali10/gate-logs-t28/redproof-before-fix.log', '修复前 IN SYNC/exit 0'),
    ('t28 绿门日志', 'team/artifacts/acceptance-20260916-dali10/gate-logs-t28/input-sync-green.log', '当前树 IN SYNC/exit 0'),
    ('t28 报告', 'team/artifacts/acceptance-20260916-dali10/gate-logs-t28/t28-summary.md', '**报告类文档：会随更正漂移 ⇒ 引用请现算**'),
    ('t30 被审脚本', 'scripts/verify_bst_sw_sequence.py', '契约闭合断言；t30 ACCEPT 锚点'),
    ('t30 阳性对照日志', 'team/artifacts/acceptance-20260916-dali10/gate-logs-t30/bst-sw-positive-control.log', 'TM600 缺失=[110]/TM601=[]/exit 1'),
    ('t30 报告', 'team/artifacts/acceptance-20260916-dali10/gate-logs-t30/t30-summary.md',
     '**路径确认：位于 gate-logs-t30/**（深树扫描可核）；§9 = (a)推导 locator/(b)pin-18 前提/(c)ACCEPT 边界 + 双盲区成因；**报告类 ⇒ 引用请现算**'),
    ('t30 报告定位记录', 'team/artifacts/acceptance-20260916-dali10/gate-logs-t30/t30-summary-locate.json',
     '脚本现算的 path/size/sha256/mtime + 与真源交叉比对 + 口径更正落地检查（供引用方直接读取）'),
    ('门禁基线(未改)', 'scripts/gate_baseline.json', '28 B；cbit 为 KNOWN-RED 依据'),
    ('门禁外壳', 'scripts/run_gates.ps1', 'L119 正则待修(另开小任务)'),
    ('relay-trace 门', 'scripts/verify_relay_trace.py', 't25 修复'),
    ('t33 报告', 'team/artifacts/acceptance-20260916-dali10/build-report.json', 'verdict=blocked；分两段：gate 运行 exit=1'),
    ('契约(冻结 rev 24)', 'team/artifacts/acceptance-20260916-dali10/setup-contract.json', '只读权威'),
    ('DEPLOYED test.cpp', 'D:/PROJECT6-DALI/ForCodexDebug/source/test.cpp',
     '编译输入（未落盘）；**缺 BST 侧 48/76**（真因·活危害）。⚠️ 旧注"缺 K109/K110"已撤：109/110 本不该闭，0 命中是对的'),
    ('生产树 devel test.cpp', 'D:/PROJECT6-DALI/devel/source/test.cpp', '只读；零写入证据'),
    # ---- t42（ACM200 引脚归属判定）取证：Captain 要求登记本真源，避免下次引用漂移 ----
    ('t42 取证脚本(我提供)', 'team/artifacts/acceptance-20260916-dali10/gate-logs-t33/t42_acm_pin_attribution_evidence.py',
     'ACM 引脚归属取证；只读、零写入'),
    ('t42 取证日志(我提供)', 'team/artifacts/acceptance-20260916-dali10/gate-logs-t33/t42-acm-pin-attribution.log',
     '两套候选依据 + 判别点；**报告类 ⇒ 引用请现算**'),
    ('t42 结论复核(宏+网表)', 'team/artifacts/acceptance-20260916-dali10/gate-logs-t33/t42-conclusion-verify.log',
     '复核 schematic-expert 的 [48,76] 判定；**报告类 ⇒ 引用请现算**'),
    ('t42 控制组复核 v2', 'team/artifacts/acceptance-20260916-dali10/gate-logs-t33/t42-controlgroup-verify.log',
     '修正列口径(Designator→MemberName)后的 5 组控制组 + ch5/ch18 决定性分离；**报告类 ⇒ 引用请现算**'),
    ('t33 落盘后预期(两口径)', 'team/artifacts/acceptance-20260916-dali10/gate-logs-t33/t33-postreplace-expectation.log',
     '落盘后 bst-sw 是否转绿取决于契约口径；**报告类 ⇒ 引用请现算**'),
    ('t44 行为证据交叉验证', 'team/artifacts/acceptance-20260916-dali10/gate-logs-t33/t44-crosscheck-behavioral.log',
     '应 schematic-expert 之请复核 §1 行为证据 + §4 归因区分；**报告类 ⇒ 引用请现算**；'
     '⚠️ 其"C) 调用点计数"一节的 K48/K76=8 实为**总提及**，作废 ⇒ 见下一条'),
    ('t44 计数更正记录', 'team/artifacts/acceptance-20260916-dali10/gate-logs-t33/t44-count-correction.md',
     '**引用 K48/K76 计数时以本文件为准**：调用点各 4（总提及 8）；6 函数先例；节点汇聚不变式（FACT/INFERENCE 分开）'),
    ('t44 调用点重算日志', 'team/artifacts/acceptance-20260916-dali10/gate-logs-t33/t44-recount-callsites.log',
     '逐 token 的 SetOn 操作数 vs 注释 vs 总提及 + K110/K76 同网实测'),
    ('t42 权威端子表', 'knowledge/hardware/relays.md', 'G6K-2G-Y DPDT 端子定义（L18-31）'),
    ('t42 网表', 'project/DALI/Dali-SCH.csv', '端子级连通性来源'),
    ('t42 引脚宏', 'D:/PROJECT6-DALI/ForCodexDebug/source/Pin_Channel_define.h',
     '`_PIN_CHANNEL_DEFINE_SW12_U1REF_BST_ACM_ = "S5_5,…"`'),
    # ---- t33 相关文档（本轮新增，均为报告类 ⇒ 引用请现算）----
    ('t33 过渡清单', 'team/artifacts/acceptance-20260916-dali10/gate-logs-t33/t33-transition-plan.md',
     '**报告类 ⇒ 引用请现算**；含 t42 三分支'),
    ('t33 修订归属规则', 'team/artifacts/acceptance-20260916-dali10/gate-logs-t33/t33-revision-attribution.md',
     '**报告类 ⇒ 引用请现算**'),
    ('t33 K110 机制(三轮更正)', 'team/artifacts/acceptance-20260916-dali10/gate-logs-t33/t33-k110-mechanism.md',
     '**报告类 ⇒ 引用请现算**'),
    ('t28 冻结/引用纪律记录', 'team/artifacts/acceptance-20260916-dali10/gate-logs-t28/t28-freeze-correction.md',
     '**报告类 ⇒ 引用请现算**；§5 引用纪律'),
]

now = datetime.datetime.now().astimezone().isoformat(timespec='seconds')
rows = []
for label, relpath, note in ENTRIES:
    p = relpath if os.path.isabs(relpath) else os.path.join(WS, relpath)
    if not os.path.isfile(p):
        rows.append({'label': label, 'path': relpath, 'missing': True})
        continue
    d = open(p, 'rb').read()
    # ⚠️ 不把时间戳写进 row —— 否则同一输入每次运行产出不同文件（我实测：连跑两次哈希不同）
    rows.append({
        'label': label,
        'path': relpath,
        'size': len(d),
        'sha256': hashlib.sha256(d).hexdigest(),
        'note': note,
    })

doc = {
    'purpose': 't28/t30/t42 稳定锚点清单 —— 单一真源。引用方请直接读取本文件，勿手抄哈希。',
    'generatedBy': 'compile-diagnostician (t28/t30/t33 执行者)',
    'anchorsObservedAt': now,
    'determinismRule': ('本文件内容**只由被登记文件的内容决定**（不含每行读取时间戳）⇒ '
                        '同一输入重复运行应产出逐字节相同的文件；若其哈希变化，'
                        '说明被登记的某个文件确实变了 —— 这正是它作为"漂移探测器"的价值。'),
    'readingRule': ('凡标注"报告类文档"的条目会随作者更正而漂移 ⇒ 引用时必须现算 + 标时刻；'
                    '其余条目自交付后未再编辑，可作稳定锚点。本工作区源受 DLP 保护，'
                    '一切读取/哈希必须用 python（rb），不得用 pwsh 文本工具。'),
    'anchors': rows,
}
# 他方自有文件：本生成器**不写入**这些前缀的文件
DO_NOT_TOUCH_PREFIXES = ('setupArchitect-', 't34-carrier', 't34-CARRIER')  # setup-architect ③：其指针文件一并受保护（不改名、只拦写入）
out = os.path.join(HERE, 't28-anchors.json')
# (a) 输出重定向：`--out <path>` ⇒ 沙箱实验可改**输出目标**，而非只隔离输入
if '--out' in sys.argv:
    _i = sys.argv.index('--out')
    if _i + 1 < len(sys.argv):
        out = sys.argv[_i + 1]
        print('[out-redirect] 输出目标 = %s' % out)
# ⚠️ 保护他方命名空间：本生成器**整篇重写**该文件，若无条件覆盖会**静默抹掉**其它成员
#    写入的顶层键（实测：setup-architect 已新增 `setupArchitectFreezeAnchors`）。
#    故先读回现盘，把**非本生成器所有**的键原样保留。
OWN_KEYS = {'purpose', 'generatedBy', 'anchorsObservedAt', 'determinismRule', 'readingRule', 'anchors',
            'preservedPeerNamespaces'}   # ← 必须包含自身键，否则复跑会把它当"他方键"再包一层（实测踩过）
_inp = out
if '--in' in sys.argv:
    _j = sys.argv.index('--in')
    if _j + 1 < len(sys.argv):
        _inp = sys.argv[_j + 1]
        print('[in-redirect] 读取目标 = %s' % _inp)
if os.path.isfile(_inp):
    try:
        prev = json.loads(io.open(_inp, encoding='utf-8-sig').read())
        # 兼容历史：先前运行可能已把键包进 preservedPeerNamespaces，这里展开后再收集一次
        merged = {}
        # 1) 先收历史层里**每个子键**（并集累积，避免把多键压成 1 键）
        for k, v in (prev.get('preservedPeerNamespaces') or {}).items():
            if k in ('preservedPeerNamespaces',):
                continue
            merged[k] = v
        # 2) 再收现盘顶层里的他方键（同样逐键并集）
        for k, v in prev.items():
            if k not in OWN_KEYS and k != 'preservedPeerNamespaces':
                merged[k] = v
        # 3) 与他方**自有文件**并集：若他方已迁出，仍保留到此命名空间（只读其文件）
        for f in os.listdir(HERE):
            if f.startswith('setupArchitect-') and f.endswith('.json'):
                try:
                    other = json.loads(io.open(os.path.join(HERE, f), encoding='utf-8-sig').read())
                    merged.setdefault('setupArchitectFreezeAnchors', {})
                    merged['setupArchitectFreezeAnchors']['mirrorOf'] = f
                    merged['setupArchitectFreezeAnchors']['mirrorSizeAtMirrorTime'] = os.path.getsize(os.path.join(HERE, f))
                    # ⭐ 镜像记录须能回答『镜像的是哪一份』—— size **不能识别内容**（本 run 有『同尺寸三哈希』实证）；
                    #    `mirroredContentSha256` **指称一个修订、不会因后续追加而过期**（size 会：误差甚至变号）
                    merged['setupArchitectFreezeAnchors']['mirroredContentSha256'] = (
                        __import__('hashlib').sha256(open(os.path.join(HERE, f), 'rb').read()).hexdigest())
                    merged['setupArchitectFreezeAnchors']['mirrorSizeNote'] = (
                        'value expires; recompute —— 该值是**镜像时刻**的 size，不构成该文件的现身份；'
                        '引用请以 全路径 + 当次现算 sha256 为准')
                    merged['setupArchitectFreezeAnchors']['mirrorAt'] = (
                        __import__('datetime').datetime.now().astimezone().isoformat(timespec='seconds'))
                    # ⚠️ 移除**旧键** `mirrorSize`（会随并集从历史层带过来 ⇒ 成为"记死的旧尺寸"；活体漂移实例）
                    merged['setupArchitectFreezeAnchors'].pop('mirrorSize', None)
                except Exception:
                    pass
        if merged:
            doc['preservedPeerNamespaces'] = merged
            print('  保留他方命名空间: %s' % ', '.join(sorted(merged)))
    except Exception as e:                                    # 读不动也不阻断生成
        print('  WARN: 读取现盘以保留他方键失败: %s' % e)
body = json.dumps(doc, ensure_ascii=False, indent=2)
if '--check' in sys.argv:
    cur = io.open(out, encoding='utf-8').read() if os.path.isfile(out) else ''
    strip = lambda s: re.sub(r'"anchorsObservedAt": "[^"]*",\n', '', s)
    print('现盘哈希: %s' % (hashlib.sha256(open(out, 'rb').read()).hexdigest() if cur else 'N/A'))
    print('重算主体与现盘一致(忽略时间戳行): %s' % (strip(cur) == strip(body + "\n")))
    sys.exit(0)
io.open(out, 'w', encoding='utf-8').write(body)
print('WROTE %s (%d B / %s)' % (out, os.path.getsize(out), hashlib.sha256(open(out, 'rb').read()).hexdigest()))
print('锚点条目: %d' % len(rows))
for r in rows:
    if r.get('missing'):
        print('  MISSING  %s' % r['label'])
    else:
        print('  %-22s %-46s %8d B  %s' % (r['label'], r['path'], r['size'], r['sha256']))
