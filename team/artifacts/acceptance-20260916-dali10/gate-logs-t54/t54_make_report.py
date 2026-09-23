# -*- coding: utf-8 -*-
"""t54：生成 build-report.json（verdict=blocked，如实）。

关键判据（本脚本现算，不手抄）：
  · 部署态（compiledRevision）TM600 相对 rev 32 期望 [48,60,61,76,83] ⇒ 缺 [48,76] ⇒ bst-sw NEW-RED
  · 候选 payload 相对同期望 ⇒ missing=[] ⇒ 落盘后预期 GREEN
  · 归因 = "实现未落盘"（任务/首轮红因从"缺 110"变为"缺 48/76"），**不记作缺陷或回归**
所有哈希由脚本现算写入。
"""
import datetime
import hashlib
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
RUN = os.path.join(WS, 'team', 'artifacts', 'acceptance-20260916-dali10')
LOG = os.path.join(RUN, 'gate-logs-t54')
sys.path.insert(0, os.path.join(WS, 'scripts'))
import verify_relay_trace as V  # noqa: E402

DEP = 'D:/PROJECT6-DALI/ForCodexDebug/source/test.cpp'
PAY = os.path.join(RUN, 'implementation-payload-TM600-TM601.cpp')
CONTRACT = os.path.join(RUN, 'setup-contract.json')


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def info(p):
    d = open(p, 'rb').read()
    return len(d), hashlib.sha256(d).hexdigest(), datetime.datetime.fromtimestamp(
        os.path.getmtime(p)).isoformat(timespec='seconds')


def setons(path):
    t = io.open(path, encoding='utf-8-sig', errors='replace').read()
    out = {}
    for fn, blk in V.fn_blocks(t):
        nums = set()
        for r in V.parse_setons(blk):
            m = re.match(r'K(\d+)_', r)
            if m:
                nums.add(int(m.group(1)))
            elif re.fullmatch(r'\d+', r):
                nums.add(int(r))
        out[fn] = nums
    return out


C = json.loads(io.open(CONTRACT, encoding='utf-8-sig').read())
idx = {}
for e in (C.get('aliasResolution') or []):
    a = str(e.get('alias', ''))
    nums = set()
    for x in ((e.get('resolution') or {}).get('closedRelayNumbers') or []):
        if isinstance(x, int):
            nums.add(x)
        else:
            nums |= {int(y) for y in re.findall(r'\d+', str(x))}
    users = set()
    for x in (e.get('usedByTm') or []):
        users |= set(re.findall(r'\b(TM\d+)\b', str(x)))
    idx[a] = (nums, users)


def expect(tm_base):
    d = C['tmDeltas'][tm_base]
    exp = {}
    for a in [str(x) for x in (d.get('aliasesUsed') or [])]:
        for n in sorted(idx.get(a, (set(), set()))[0]):
            exp.setdefault(n, 'aliasResolution[%s].closedRelayNumbers (tmDeltas.%s.aliasesUsed)' % (a, tm_base))
    for a, (nums, users) in idx.items():
        if tm_base in users:
            for n in sorted(nums):
                exp.setdefault(n, 'aliasResolution[%s].closedRelayNumbers (usedByTm lists %s)' % (a, tm_base))
    return exp


exp600, exp601 = expect('TM600'), expect('TM601')
dep, pay = setons(DEP), setons(PAY)
rev = C.get('revision')
b2 = [x for x in C['aliasResolution'] if x.get('alias') == 'bst2sw'][0]

d_size, d_sha, d_mt = info(DEP)
p_size, p_sha, p_mt = info(PAY)
c_size, c_sha, c_mt = info(CONTRACT)
stdout_log = os.path.join(LOG, 'run-gates-t54-stdout.log')
bst_log = os.path.join(LOG, 'bst-sw.log')

# 门禁逐门（从 stdout 解析）
txt = io.open(stdout_log, encoding='utf-8-sig', errors='replace').read()
gates = []
for m in re.finditer(r'^\s{2}(\S+)\s+(.+?)\s+(GREEN|NEW-RED|KNOWN-RED|FIXED)\s+(-?\d+)\s+([\d.]+)\s*$', txt, re.M):
    gates.append({'id': m.group(1), 'desc': m.group(2).strip(), 'status': m.group(3),
                  'exit': int(m.group(4))})

# ⚠️ 门禁实际读取的契约 rev 来自**门禁日志自述**（证据锚），不是现盘 rev
_bst_log_txt = io.open(bst_log, encoding='utf-8-sig', errors='replace').read() if os.path.isfile(bst_log) else ''
_m = re.search(r'rev=(\d+)', _bst_log_txt)
gateRevFromLog = _m.group(1) if _m else None
print('  [归属] 门禁日志自述 rev = %s ; 现盘 rev = %s' % (gateRevFromLog, C.get('revision')))

report = {
    'runId': 'acceptance-20260916-dali10',
    'targetRoot': 'D:/PROJECT6-DALI/ForCodexDebug',
    'configuration': 'Release',
    'producedBy': 'compile-diagnostician (t54, attempt 1 / 42042bdb-7a27-4661-8c46-f0ede914a804)',
    'generatedAt': datetime.datetime.now().astimezone().isoformat(timespec='seconds'),
    'verdict': 'blocked',
    'verdictReason': ('判据（现算，非预测）：契约 rev %s 的 bst2sw 期望 = %s。'
                      '**部署态（＝门禁实际输入，compiledRevision=%s…）** TM600 实际 %s ⇒ 缺 %s ⇒ bst-sw NEW-RED；'
                      '**候选 payload** TM600 实际 %s ⊇ 期望 ⇒ missing=[] ⇒ 落盘后预期 GREEN。'
                      '⇒ 红因 = **实现未落盘**（目标树仍为 t23 版），**非缺陷、非回归**；'
                      '按 Captain 裁定，不把该红记作 t54 的失败原因，也不得为迎合门禁补 110。'
                      % (rev, sorted(exp600), d_sha[:8], sorted(dep.get('TM600_HS_RDSON', set())),
                         sorted(set(exp600) - dep.get('TM600_HS_RDSON', set())),
                         sorted(pay.get('TM600_HS_RDSON', set())))),
    'contract': {
        # ⚠️ 单一基准原则（schematic-expert 指出"两态混放"）：本块**只**描述门禁态身份；
        #    现盘态三值一律只放 currentOnDisk，避免"rev32 紧邻 rev39 的哈希"被误读为同一版本。
        'baseline': 'gate-read (门禁日志自述)',
        'path': 'team/artifacts/acceptance-20260916-dali10/setup-contract.json',
        'revision': gateRevFromLog,
        'revisionNote': ('本块所有字段均为**门禁态**（= 门禁那次运行实际读到的版本）；'
                         '现盘值见 currentOnDisk —— 两者基准不同，引用时必须分别声明。'),
        'currentOnDisk': {'baseline': 'on-disk (现盘)', 'revision': rev, 'size': c_size,
                          'sha256': c_sha, 'mtime': c_mt},
        'gateExpectationSet': {
            'value': ['由日志自述取得：TM600 期望 [48,60,61,76,83]'],
            'consistencyCheck': ('rule-reviewer 指出"日志自称 rev=32 但期望集像是 ch5 口径"可能自相矛盾；'
                                 '我方实测：**rev 28 快照的 bst2sw=[110,61]** ⇒ exp=[60,61,83,110]（旧口径），'
                                 '**现盘 rev 39** ⇒ exp=[48,60,61,76,83]。⇒ ch5 口径出现在 **(rev28, 现盘] 区间**内，'
                                 'rev 32 落在该区间 ⇒ **自称与期望集并不矛盾**。'),
            'residualCaveat': ('⚠️ 现存字节快照**无法**把区间收窄到"恰好 rev 32"；且门禁当初**实际读入的那份 32 号文件'
                              '已不存在**（无字节快照）⇒ 该次运行的契约归属只能到'
                              '"**日志自述 + 区间相容**"这一级，不能声称"已用字节证明读的是 rev 32"。'),
            'evidence': 'gate-logs-t54/t54_verify_rev_vs_expectation.py / t54-rev-vs-expectation.log',
        },
        'bst2sw_closedRelayNumbers': b2['resolution'].get('closedRelayNumbers'),
        # ⚠️ 两名区分（schematic-expert 指出）：契约里"被取代"有两个不同概念，名字极易混读。
        'bst2sw_closedRelayNumbersSuperseded': {
            'value': b2['resolution'].get('closedRelayNumbersSuperseded'),
            'meaning': '**被取代的闭集**（旧 ch18 对 `[110,61]`）',
        },
        'bst2sw_supersededCh1VariantRelaySet': {
            'value': b2['resolution'].get('supersededRelaySet'),
            'meaning': ('**被取代的 CH1 变体集**（`K_FPVIH_TO_BST_B` = `[131,132,134,135]`），'
                        '**不是**本项曾被要求的闭集 —— 旧闭集见上一字段 `[110,61]`'),
            'contractField': 'resolution.supersededRelaySet',
            'contractEvidence': (b2['resolution'] or {}).get('evidenceSupersededChannel1'),
        },
        # 旧名保留为**只读别名**（明确标注语义），避免已引用者落空
        'bst2sw_supersededRelaySet': {
            'value': b2['resolution'].get('supersededRelaySet'),
            'aliasOf': 'bst2sw_supersededCh1VariantRelaySet',
            'warning': '⚠️ 该名字**易被误读为"被取代的闭集"**；旧闭集实为 `[110,61]`（见 bst2sw_closedRelayNumbersSuperseded）',
        },
        'note': 't53 收尾（路径 1）已落地：权威期望由 ch18 的 [110,61] 切到 ch5 路线 [48,60,61,76]',
    },
    'compiledRevision': {
        'path': DEP, 'size': d_size, 'sha256': d_sha, 'mtime': d_mt,
        'label': '在役 t23 版（**未落盘**）',
        'note': ('**目标树未落盘** ⇒ 本报告的门禁结论归属该修订；'
                 '候选 payload 未应用，故不得写成"已落盘"或"已编译新树"'),
    },
    'candidatePayload': {
        'path': 'team/artifacts/acceptance-20260916-dali10/implementation-payload-TM600-TM601.cpp',
        'size': p_size, 'sha256': p_sha, 'mtime': p_mt,
        'label': '沙箱候选（DELIVERED，未 DEPLOYED）',
        'tm600_seton': sorted(pay.get('TM600_HS_RDSON', set())),
        'tm601_seton': sorted(pay.get('TM601_LS_RDSON', set())),
        'equivalenceJudgement': {
            'method': ('等价判定（**非门禁产出**）：复现 check_contract_closures() 的判据 '
                       'missing = set(exp) - set(SetOn)，输入为候选 payload'),
            'tm600_missing': sorted(set(exp600) - pay.get('TM600_HS_RDSON', set())),
            'tm601_missing': sorted(set(exp601) - pay.get('TM601_LS_RDSON', set())),
            'expected_after_landing': 'GREEN（missing=[]）',
        },
    },
    'gates': [{
        'command': 'pwsh -NoProfile -File scripts/run_gates.ps1 -LogDir team/artifacts/acceptance-20260916-dali10/gate-logs-t54',
        'cwd': '.', 'startedAt': datetime.datetime.fromtimestamp(os.path.getmtime(stdout_log)).isoformat(timespec='seconds'),
        'exitCode': 1, 'log': 'team/artifacts/acceptance-20260916-dali10/gate-logs-t54/run-gates-t54-stdout.log',
        'logSha256': sha(stdout_log),
    }],
    'gateTable': gates,
    'gateSummary': {
        'totalGates': len(gates),
        'green': sum(1 for g in gates if g['status'] == 'GREEN'),
        'newRed': [g['id'] for g in gates if g['status'] == 'NEW-RED'],
        'knownRed': [g['id'] for g in gates if g['status'] == 'KNOWN-RED'],
        'suiteExitCode': 1,
        'newRedDetail': ['TM600_HS_RDSON 缺 K48', 'TM600_HS_RDSON 缺 K76'],
        'log': 'team/artifacts/acceptance-20260916-dali10/gate-logs-t54/bst-sw.log',
        'logSha256': sha(bst_log),
        'note': ('其它 11 门与首轮完全一致（无新增红、无回退）；cbit 为基线豁免（KNOWN-RED）'),
    },
    'expectations': {
        'TM600_HS_RDSON': {'expected': sorted(exp600), 'sources': exp600},
        'TM601_LS_RDSON': {'expected': sorted(exp601), 'sources': exp601},
        'derivation': ('expected_for_tm()：aliasResolution[*].resolution.closedRelayNumbers，'
                       '按 tmDeltas.<TM>.aliasesUsed 与 usedByTm 索引；pinRouteTable 仅 locator、relaySet 仅预算池'),
    },
    'attributionSplit': {
        'required': '真因与旁因**不得合并记账**（Captain 令）',
        'trueCause': ('**真因＝部署态缺 `K48/76`**：在役 `test.cpp` 的 TM600 未闭 BST 侧 `K48_ACM5_AMP_REF`+`K76_ACM_BST` ⇒ '
                      '按 t45/t48 的改道机制，源被送往 `SW1_F/SW2_F`（**既非 BST、也非 BOOT0**）⇒ 属**活危害**；'
                      '这是本批必须落盘 payload 才能消除的原因。'),
        'sideCause': ('**旁因＝契约决策字段曾未切换（假红）**：`aliasResolution[bst2sw].resolution.closedRelayNumbers` 曾长时间保留 '
                      'ch18 口径 `[110,61]` ⇒ 屏幕要求一个**非必需**的 `110`、且**看不见真正的缺口 `48/76`**；'
                      '该假红**已由 t53 落地（现 rev %s 为 `[48,60,61,76]`）解除**。' % rev),
        'note': '两因性质不同：真因是**实现缺口**（须落盘修复），旁因是**契约未消歧**（已解决，不再产生红）。',
    },
    'gateRunAccounting': {
        'gateLogsT54Runs': 1,
        'note': ('本次 t54 在本目录下只产生 **1** 次 `run_gates.ps1` 运行（`run-gates-t54-stdout.log`）；'
                 '报告中**未**声称任何"重跑后 GREEN"（目标树未落盘、门禁输入仍是 `15c7d2b8…`）。'),
    },
    'attributionLimitations': [
        '**"GREEN" ≠ "闭合集被约束"**：bst-sw 为**子集判定**（未启用 --check-extra）⇒ 多余闭合不可见。'
        '本批方案 B（仅闭 ACM200 族 {48,76} + SW {60,61}）由工程判断与契约一致性保证，**门禁不具备反证能力**；'
        '欲使其受门禁保护须另立明确决定启用 --check-extra 并定义 budget 池。',
        '本报告门禁结论归属 compiledRevision（在役 t23 版）；候选 payload 的 GREEN 属**等价判定**，不是门禁产出。',
        '"**断言期望集取自错字段**" ≠ "**断言写错**"：该字段被标 contestedAttribution；'
        '本轮实测时其权威值已由 t53 切到 ch5 路线 ⇒ 归因按实际 rev 判定（见 contract 段），不归咎脚本。',
    ],
    'controls': {
        'purpose': ('阳性/阴性/部署态三项并列对照，证明"门禁仍能发现真缺陷"（B-6 类盲区已关闭）——'
                    '**均在同一契约 rev %s 下完成**，沙箱内、未改脚本、未启用 --check-extra、未动 gate_baseline.json。' % rev),
        'method': ('复现 `expected_for_tm()` 派生规则与 `missing = set(exp) - set(SetOn)` 判据；'
                   '**不是** `verify_bst_sw_sequence.py` 进程输出（该脚本 main() 在 targets 为空时提前 return，'
                   '故 --src 无法对仅有 TM600/TM601 的副本端到端跑）。部署态一列为**真实 run_gates 输出**。'),
        'positive': {'label': '沙箱副本，从 TM600 的 SetOn 去掉 K48_ACM5_AMP_REF + K76_ACM_BST',
                     'tm600_seton': sorted([13, 57, 60, 61, 83, 85, 126]),
                     'missing': [48, 76], 'verdict': '报红（真缺口被捕获）'},
        'negative': {'label': '终批 payload 原样', 'file': 'implementation-payload-TM600-TM601.cpp',
                     'tm600_seton': sorted(pay.get('TM600_HS_RDSON', set())),
                     'missing': sorted(set(exp600) - pay.get('TM600_HS_RDSON', set())), 'verdict': 'PASS'},
        'deployed': {'label': '在役 test.cpp:9081（真实门禁输入）',
                     'tm600_seton': sorted(dep.get('TM600_HS_RDSON', set())),
                     'missing': sorted(set(exp600) - dep.get('TM600_HS_RDSON', set())),
                     'verdict': 'FAIL（红因＝缺 [48,76]，不再是缺 110）'},
        'artifact': 'team/artifacts/acceptance-20260916-dali10/gate-logs-t54/t54-controls.json',
        'log': 'team/artifacts/acceptance-20260916-dali10/gate-logs-t54/t54-controls.log',
    },
    'diagnostics': [{
        'id': 'T54-D1', 'severity': 'blocker', 'kind': 'not-landed',
        'problem': '目标树未落盘 ⇒ 无法产出真正的 bst-sw GREEN；且 verify_bst_sw_sequence.py 的 '
                   'main() 在 targets 为空时提前 return，故 --src 也无法用于对候选文件校验契约闭合。',
        'evidence': ['gate-logs-t54/run-gates-t54-stdout.log', 'gate-logs-t33/t54-execution-constraint.md'],
        'neededToClear': 'Captain 落盘候选 payload 后，我重跑一次 run_gates.ps1 ⇒ 期望 bst-sw GREEN ⇒ verdict 转 pass',
    }],
    'exitZeroSemantics': {
        'required': 'Captain 令：报告必须区分两种 exit 0',
        'pass': ('**PASS（执行了断言且无缺口）** —— `bst-sw` 在含 ZCD/OCP 目标的源文件上运行，'
                 '契约闭合断言已执行、`missing=[]`，exit 0 表示真正通过。'),
        'emptyPass': ('**空 PASS（未执行断言）** —— `verify_bst_sw_sequence.py::main()` 在 '
                      '`targets = derive_targets(...)` 为空时**直接 `return 0`**，契约闭合断言**整段被跳过**。'
                      '故在**部署树之外的源文件**（如只有 TM600/TM601 的候选 payload）上得到 exit 0 '
                      '**不等于通过**，而是"该源文件无 ZCD 目标 ⇒ 未执行断言"。'),
        'observed': ('本轮实测：`--src <候选payload>` ⇒ `[scan] test.cpp 无 rampi_capv 电流斜坡测试项 (非 ZCD/OCP 家族), 空 PASS` / exit 0 '
                     '⇒ **属"空 PASS"，不得计为通过**。'),
    },
    'capabilityLimitations': [{
        'id': 'B-7',
        'title': '`bst-sw` 的契约闭合断言在**空 `targets`** 下被静默跳过（fail-open）',
        'detail': ('`main()` L490 `targets = derive_targets(...)`；L497-499 `if not targets: print("[scan] … 空 PASS"); return 0` '
                   '—— **早退发生在任何判定之前**，而契约闭合断言在 L502/L515 才执行 ⇒ 空集时**整段被跳过**。'
                   '且 `targets` 与"判定哪些 TM"不同源：`check_contract_closures(..., scope=)` 的 `scope` 来自 '
                   '`resolve_scope()`（L409-413）⇒ `DEFAULT_TM_SCOPE`（L259），**不来自 `targets`**。'
                   '触发条件：`--src` 指向不含 `rampi_capv(` 家族的源（`derive_targets` L96-114 按此筛选）'
                   '—— 例如只含 TM600/TM601 的副本，正是本 run 专用夹具形态。'),
        'selfContradiction': ('同文件 L506-507 自述"**契约是高电流路线闭合集合的权威, 缺失必须红而不是静默跳过**"，'
                              '但该原则只落实在"契约读不到"这条路径；"目标集为空"仍静默 PASS ⇒ **同一条原则只落实一半**。')
        ,
        'behaviorEvidence': ('实测 `--src <候选payload>` ⇒ `[scan] … 非 ZCD/OCP 家族, 空 PASS` / exit 0；'
                             '**加 `--tm-scope TM600_HS_RDSON,TM601_LS_RDSON` 后仍空 PASS / exit 0** ⇒ `--tm-scope` 救不了。 '
                             '【结构性原因（行级）】**任何 scope 参数都到不了断言**：早退 `L497-499 return 0` 早于 '
                             '`L512 _scope = resolve_scope(args)` 与 `L515 check_contract_closures(...)` '
                             '⇒ 不是"scope 值不对"，而是**代码路径根本走不到** ⇒ 用 `--tm-scope` 绕行'
                             '**从设计上被封死**（把实测上升为结构性结论）。'),
        'consequence': '**"未落盘 ⇒ 无法用被审脚本判候选 payload"**；且 **任何 `targets=0` 的门禁 PASS 都不能作为 t54 判据的证据**（它没检查任何东西）。',
        'relatedTo': '与 B-6（覆盖受登记完整性限制）同族；B-7 是"覆盖受作用域早退限制"。',
        'guardrails': ['(a)【主张】把 `if not targets` 改为 FAIL（与 L506-507 既定原则一致、改动最小）',
                       '(b) 或保留现行行为但要求日志出现 `targets=N (N>0)` 并在验收记录中写明'],
        'fixScope': '**本批不授权改 `scripts/`**（Captain 裁定）；修复属独立 owner 决定，且不得动 `gate_baseline.json`（28 B / `021015da…02cb1d`）。',
        'evidence': ('gate-logs-t54/t54-gate-failopen-forms.md ; gate-logs-t54/t54_verify_failopen.py / t54-failopen-verify.log ; '
                     'gate-logs-t33/t54-execution-constraint.md ; gate-logs-t54/t54-guard-overridable.log'),
    }],
    'gateFailOpenForms': {
        'theme': '本 run 累计三类**门禁 fail-open 形态**，主题统一为"**要 fail-closed**"。详见 `gate-logs-t54/t54-gate-failopen-forms.md`。',
        'forms': [
            {'id': 1, 'name': '展开器静默截断（工具≠语义）',
             'mechanism': '`verify_relay_trace.parse_defines()`：StdAfx.h 多值宏 **209/209 被截为首值**',
             'affectsThisRunGate': ('**否（不产生假通过）**，但须记限定：'
                                    '**成员性检查（L401/L403）对被列出的多值宏只覆盖首值** '
                                    '（`n = defines[r]`，而 `r` 来自 `parse_setons()`、不做宏展开）'
                                    '⇒ **`relay-trace` 的 PASS 不是多值宏的逐条校验证据**。'
                                    '对本 run 无实际影响：TM607/608/609/640 走**显式单值别名**'
                                    '（`K48_ACM5_AMP_REF`+`K76_ACM_BST`），该路径校验完整；'
                                    'Cap 别名↔规范名映射路径（`cap_defs`/L316）亦不受影响。'),
             'guardrail': ('先测展开器再信展开；判"宏闭了哪些 K"用 StdAfx.h 原文逐字展开。'
                           '另：该门的成员性检查（L401/L403）对多值宏只覆盖首值 ⇒ **欠严（under-strict）**，'
                           '不得作为"多值宏逐条校验"的证据。')},
            {'id': 2, 'name': '子集判定（判据不对称）',
             'mechanism': '`missing = exp − actual`：多余闭合不可见（未启用 `--check-extra`）',
             'affectsThisRunGate': '是（能力边界）—— "GREEN ≠ 闭合集被约束"',
             'guardrail': '若需约束须显式启用 `--check-extra` 并定义 budget 池'},
            {'id': 3, 'name': '空目标集 fail-open（作用域早退）★B-7',
             'mechanism': '`targets=[] ⇒ "空 PASS" + exit 0`，契约闭合断言整段被跳过；`--tm-scope` 无效',
             'affectsThisRunGate': '是 —— 造成"未落盘无法判候选 payload"',
             'guardrail': '空 `targets` 应 FAIL（首选），或强制记录 `targets=N (N>0)`'},
        ],
    },
    'provenanceSources': {
        'rule': ('**引用他方产物时必须标注来源与归属**：'
                 '`peer ledger (owner=<name>), cited by path + recomputed sha256`；'
                 '**不得称其为"中立基准"**（复核方因独立性不宜依赖被审方自档）。'),
        'baselineTriad': {
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
            'epistemicPair': {
                'synthesis': ('**没做快照的过去不可追，做了快照的将来可证。**'
                              '（`corollary` 与 `gateInputSnapshot` 是同一 epistemic 缺陷的'
                              '"过去"与"未来"两半，合起来才闭环 —— schematic-expert 指出。）'),
                'past': ('**过去（不可补）**：某历史修订究竟写了什么，只有**当时的字节快照**能独立说明；'
                         '本 run 唯一幸存的是 rev 28（`[110,61]`）⇒ 24–28 之间其余状态'
                         '**永久只能靠自述/推断**。'),
                'future': ('**未来（可保）**：`gateInputSnapshot` ⇒ **从下一次运行起**，'
                           '输入的归属由"日志自述"变为"**字节可证**"。'),
                'exception': ('**rev 28 是唯一"事后仍可补"的例外** —— 因为当时有人复制了字节'
                              '（`backups/t53-20260916-211719/` 三件套）。'),
            },
        },
        'peerLedgers': [{
            'label': 'peer ledger (owner=setup-architect)',
            'path': 'team/artifacts/acceptance-20260916-dali10/gate-logs-t28/setupArchitect-anchors.json',
            'note': ('cited by path + recomputed sha256；**非中立基准**。'
                     'reviewer 拒绝将其作复核依据（独立性 / 其同样在变）；实施方交叉核对可用。'),
        }, {
            'label': 'own ledger (owner=compile-diagnostician)',
            'path': 'team/artifacts/acceptance-20260916-dali10/gate-logs-t28/t28-anchors.json',
            'note': 'cited by path + recomputed sha256；我方自档，同样**非中立基准**。',
        }],
        'crossReference': {
            't34L45': ('`t34` 新增 L45（binding）：**bst-sw 的 PASS 不得作为覆盖证据，'
                       '除非同次输出亦显示 `[scan] targets=N` 且 N>0** —— 与本报告 `emptyPassGuard`/'
                       '`exitZeroSemantics` **同源**；我方 `run_gates.ps1` 零引用 `targets` 的实测与其一致。'),
            'note': 'Captain 若批"编排器兜底（run_gates.ps1 断言 targets>0）"，本方 re-run 前置可直接复用该断言。',
        },
    },
    'gateInputSnapshot': {
        'status': ('**已机制验证（本轮实测通过）** —— 但**尚未在真实重跑中执行**（该次运行还未发生）。'),
        'rule': ('**跑门禁前，把该次运行的输入复制到** `backups/<task>-<timestamp>-gateinputs/` **并与门禁日志同放**。'
                 '⇒ 该次运行的归属从"**日志自述**"升级为"**字节可证**"。'),
        'why': ('正是纪律 3 的补救手段，只是**把应用对象从"被覆写的产物"扩展到"每次门禁运行的输入"**；'
                '将来若被质疑"那次到底读的是哪一版"，**有字节可证**，不必再靠日志自述。'),
        'tool': 'gate-logs-t54/t54_snapshot_gate_inputs.py（`python <script> <task-tag> [--dry-run]`）',
        'captures': ['setup-contract.json（门禁读取的契约）',
                     'implementation-payload-TM600-TM601.cpp（候选交付件）',
                     'scripts/gate_baseline.json（基线，应始终 28 B）'],
        'mechanismEvidence': ('本轮机制测试：dry-run 先冒烟（不写盘）→ 真跑一次 ⇒ 生成 '
                              '`backups/t54-mechtest-20260916-231923-gateinputs/`；'
                              '核对三项快照与源**逐位一致**（377,694 / 43,806 / 28 B）✓'),
        'cost': '零风险（两条 copy）；**不改任何脚本、不改门禁、不动基线**。',
        'appliesTo': 't54 的最后一次重跑（落盘后）。',
    },
    'standardTriHash': ('**活档产物的标准三哈希**（用途不同、不可互换）：'
                        '① `sha256` = **身份**（逐字节同盘）；'
                        '② `sha256_lf_normalized` = **跨序列化可比重**（行尾无关）；'
                        '③ `reproducibleBodySha256` = **幂等判定**（剔除 `generatedAt`、跨次可比）。'
                        '⇒ **判『内容是否变』必须用 ③**，不得拿 ① 直接比。'),
    'livenessDeclaration': {
        'status': '**LIVE (活档)** — **不得标 FROZEN**',
        'why': ('本文件由 `gate-logs-t54/t54_make_report.py` 反复重生成；'
                '其 size/sha256 会随每次追加而变（本轮已多次）。'),
        'citeRule': ('引用一律「全路径 + **当次现算 sha256** + 现算时刻」；'
                     '**不得引用本文件内的任何自算哈希**（自引用会立刻过期）。'),
        'receiptInstead': ('如需"某一版的字节身份"，读外部收据 '
                           '`gate-logs-t54/build-report.receipt.json`（生成后重算，含 size/sha256/entries/at）。'),
    },
    'unionPreservationExperiment': {
        'ruledBy': 'rule-reviewer（裁定"做一次"，并要求用**第三方前缀**以真正走到并集路径）',
        'design': ('**离线副本**上放入 3 条键到**第三方命名空间** `qaProbeAnchors`'
                   '（**非** `setupArchitect-` 前缀 ⇒ 才走"他方键 ⇒ 并集累积"那条路径），'
                   '随后跑生成器，再现算结果。'),
        'result': {
            'qaProbeAnchors.anchors': 3,
            'allThreeKept': True,
            'setupArchitectFreezeAnchors.anchors': 1,
            'protectedNamespaceUntouched': True,
            'generatorExit': 0,
        },
        'secondaryConclusion': {
            'claim': '**第三方前缀（非 `setupArchitect-`）同样走并集累积路径** ⇒ 该机制**不限于**受保护前缀。',
            'whyItMatters': ('解释了**为什么该机制对一般他方键也安全**：'
                             '`DO_NOT_TOUCH_PREFIXES` 只管『直通保留』，**并集逻辑对所有他方键生效**。'),
            'notedBy': 'rule-reviewer：该结论是其『必须用第三方前缀』设计约束的**正当性证明**（不只方法学必要）。',
        },
        'conclusion': ('**(ii) 不丢当前内容：成立**；且**第三方前缀同样走并集路径** '
                       '⇒ 该机制**不限于**受保护前缀。'),
        'mustNotBeCitedAs': ('⚠️ **不得**引作 **(iii) 恢复历史** 的证据 —— 那 8 条无字节副本，'
                             '属**原理上不可测**。'),
        'thirdPartyReproduction': {
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
        'restored': '实验后**已还原活档**（含 PROBE 检查 = False ⇒ 真源未被污染）。',
        'evidence': 'gate-logs-t54/t54-reviewer-experiment-union.log（1,448 B，含副本路径/键名/条数/跑后现算）',
    },
    'withdrawnClaims': [
        {
            'claim': '"`relay-trace` 的判据不受 `parse_defines()` 截断影响"（我早前结论）',
            'status': '**已撤回（方向对但过强）**',
            'supersededBy': ('**欠严（under-strict）**：`cap_defs`/L316 这条 Cap 别名↔规范名映射路径'
                             '**确实不受影响**；但 `n = defines[r]` 在 **L401 `if n in on_set` / L403 `if n in nc_set`** '
                             '被**当数字使用**，而 `r` 来自 `parse_setons()`（原样取 SetOn 实参、**不做宏展开**）⇒ '
                             '当 SetOn 写多值宏名时**只校验首值那一个继电器**'
                             '（例 `K_FPVIH_TO_PGND_A=154,155` ⇒ 只校验 154；`K_FPVIH_TO_BST_A=46,48,76` ⇒ 只校验 46）。'),
            'whyItMattered': ('我原来只追到 L397 便下结论，属"范围没盖全"；'
                              '正确表述：**PASS 不是假通过，但不作为"多值宏逐条校验"的证据**。'),
            'evidence': ('逐行复核 `scripts/verify_relay_trace.py` L376/L401/L403/L406 + L92-98 `parse_setons()`；'
                         'log: `gate-logs-t54/t54-n-numeric-verify.log`；'
                         '现口径：`gate-logs-t54/t54-gate-failopen-forms.md` 形态 1。'),
            'raisedBy': 'schematic-expert（我复核确认）',
        },
    ],
    'checkExtraStance': {
        'currentRule': ('**禁用要求自 rev 29 起已解除**（本版闭合单路线，多余闭合不再产生）。'
                        '⇒ 是否启用 `--check-extra` 属**独立决定**：需先定义 budget 池并实测，'
                        '**不得顺手打开**，**也不得写成 "RE-ENABLED"**。'),
        'thisRunChoice': ('本轮 t54 **未启用** `--check-extra` —— 这是**本次核验选择走默认判据**，'
                          '**不是**在执行任何现行禁令；故本报告的行文一律为"未启用（本次选择）"。'),
        'whyItMatters': ('`bst-sw` 默认＝**子集判定**（`missing = exp − actual`）⇒ **多余闭合不可见** '
                         '⇒ "GREEN ≠ 闭合集被约束"（见 attributionLimitations[0]）。'),
        'unchanged': '未改门禁脚本、未动 `scripts/gate_baseline.json`（28 B / `021015da…02cb1d`）。',
    },
    'attributionThreeStates': {
        'required': 'Captain 令：三态并列，不得合并记账',
        'deployed': {'tm600_seton': sorted(dep.get('TM600_HS_RDSON', set())),
                     'state': '缺 `[48,76]`（**活危害 + 真缺陷**：TM600 在驱动 ch5 仪器而 `K48` 未闭 ⇒ 源被改道 `SW1_F`/`SW2_F`）'},
        'oldPayload': {'sha256_short': '2d0984d9…（39,457 B，已被取代）',
                       'state': '**闭错腿（`109/110`）+ 缺 `[48,76]`**'},
        'currentPayload': {'sha256': p_sha, 'size': p_size,
                           'tm600_seton': sorted(pay.get('TM600_HS_RDSON', set())),
                           'state': '**已合规**（⊇ 期望 ⇒ `missing=[]`）'},
        'note': '三态性质不同：部署态是活危害、旧 payload 为历史、现 payload 合规 ⇒ **不得合并**。',
    },
    'emptyPassGuard': {
        'status': ('⚠️ **已记录、但【未强制】**（rule-reviewer 指出，我实测确认）：本条只是**验收格式约定**，'
                   '**尚未进入任何脚本或编排器** ⇒ 属"新增守卫记录而无消费者"，读者可能误以为已强制。'),
        'enforcementGap': {
            'earlyExitStillInCode': '`verify_bst_sw_sequence.py` L497-499 `if not targets: print(…空 PASS); return 0`',
            'noEnforcementFound': ('扫 `scripts/**`（.py/.ps1）：`if not targets` 仅 **1 处**（即上述早退）；'
                                   '`emptyPassGuard`/`targets==0`/`len(targets)==0` 断言 **0 命中**；'
                                   '编排器 `run_gates.ps1` 对 `targets`/`scan`/`emptyPassGuard` 命中 **均为 0** '
                                   '⇒ **不知道 targets 空否**。'),
            'residualRisk': ('**若将来 `derive_targets` 返回空（计划/作用域改动），门禁会打印 PASS 并 exit 0，'
                             '而实际未做任何检查** —— "未检查"被映射为 PASS。'),
        },
        'fixOptions': [
            '(i)【推荐·零目标＝无证据＝不得 PASS】把 L497-499 改为 `return 1`（或 `raise SystemExit(1)`）——断言而非早退；',
            '(ii) 保留早退但在编排器兜底：`run_gates.ps1` 解析 `[scan] targets=N`，**N==0 即判 NEW-RED**。',
        ],
        'criterion': '**"未检查"绝不可映射为 PASS**（本 run 的门禁语义正是"exit code 即结论"）。',
        'fixScope': '**本批不授权改 `scripts/`**（Captain 裁定）⇒ 立为**具名待办**；在闭合前**禁止以该门禁的 PASS 作为覆盖证据**。',
        'rule': ('**t54 的 PASS 须同时满足 `[scan] targets=N>0`；否则该 PASS 为空跳（未执行断言）。**'
                 '（schematic-expert 提出；Captain 已把 B-7 记为门禁能力局限。本条为可执行验收格式。）'),
        'rationale': ('`verify_bst_sw_sequence.py` L497-499：`if not targets: print(…空 PASS); return 0` '
                      '⇒ 空集时**契约闭合断言整段被跳过**却仍 exit 0 ⇒ "exit 0"本身不足以证明检查已执行。'),
        'counterExample': ('`--src <候选payload>`（只含 TM600/TM601）⇒ 日志无 `targets=`，'
                           '而是"无 rampi_capv 电流斜坡测试项 … 空 PASS" / exit 0 ⇒ **空跳，不得计为通过**。'),
        'evidenceThisRun': {
            'gateLog': 'team/artifacts/acceptance-20260916-dali10/gate-logs-t54/bst-sw.log',
            'note': ('本轮 t54 的 bst-sw 日志含 `[scan] targets=4`（>0）⇒ **契约闭合断言确已执行**，'
                     '故该次 NEW-RED 是真判定、不是空跳。'),
            'rowLevelEvidence': {
                'L1': 'TM600_HS_RDSON: 契约声明必需 [48,60,61,76,83] … 缺失=[48,76] (缺失数 2)',
                'L2': 'TM601_LS_RDSON: … 缺失=[] (缺失数 0)',
                'L3': '契约来源: setup-contract.json rev=32',
                'L4': '[scan] D:\\PROJECT6-DALI\\ForCodexDebug\\source\\test.cpp ← **跑的是部署树**',
                'L6': '[scan] targets=4 FAIL=2 ← **targets>0 ⇒ 断言确已执行**',
            },
            'precisionNotes': [
                ('`FAIL=2` 是**错误条数**，不是"两个 TM" —— L9/L10 是 TM600 的**两条继电器级错误**'
                 '（K48、K76 各一条）；TM601 缺失为 0。'),
                '扫描对象是**部署树**（L4）⇒ 与"部署树含 rampi_capv 家族故 targets 非空"一致。',
                ('该次契约已是 **rev=32** 且期望集为修正后的 `[48,60,61,76,83]`'
                 '⇒ 与"判决字段已改对、此后各版维持"的时间线一致。'),
            ],
        },
    },
    'builds': [{
        'command': ('pwsh -NoProfile -File scripts/run_gates.ps1 -Build -LogDir '
                    'team/artifacts/acceptance-20260916-dali10/gate-logs-t33   （t33 实测；本轮 t54 按沙箱只跑一次门禁、未重复 -Build）'),
        'cwd': 'D:/Newtest/DSH/ATE-Coding-Plat',
        'startedAt': '2026-09-16T19:5x+08:00',
        'exitCode': 1,
        'log': 'team/artifacts/acceptance-20260916-dali10/gate-logs-t33/build.log',
        'logSha256': sha(os.path.join(RUN, 'gate-logs-t33', 'build.log')),
        'status': 'failed_permission',
        'reason': ('MSBuild **error MSB3491**：写 source/Release/F12011.tlog/F12011.lastbuildstate **访问被拒绝**'
                   '（本会话工作区不含目标树；直接写探针亦被拒）⇒ Release 编译**必须由可写会话（Captain）执行**。'
                   '引用该证据时须标注"证据来源＝可写会话/本会话只读"。'
                   '另：目标树未落盘，即便编译其对象也不是候选 payload。'),
    }],
    'buildDetail': {
        'result': 'NOT ATTEMPTED IN THIS TASK — Release 编译须由可写会话执行（本会话对目标树只读；'
                  '前轮实测 MSBuild error MSB3491 写 tlog 被拒）',
        'evidenceSource': '本会话无编译证据；编译证据须来自可写会话（Captain），并须标注来源',
    },
    'fixes': [],
    'limitations': [
        'BLOCKED, NOT PASSED：bst-sw 为 NEW-RED（部署态缺 48/76），本轮未产出 pass。',
        '**编译成功 ≠ 电性/硬件正确**；未做任何机台/硬件验证；本轮**未做编译**（须可写会话）。',
        '门禁只读一次（无 -Build）；未改任何门禁脚本、未动 gate_baseline.json（28 B / 021015da…02cb1d）、未启用 --check-extra。',
        '契约与 payload 均为随时间变动的产物 ⇒ 引用前现算。',
    ],
}
out = os.path.join(RUN, 'build-report.json')
io.open(out, 'w', encoding='utf-8').write(json.dumps(report, ensure_ascii=False, indent=2))
print('WROTE %s (%d B / %s)' % (out, os.path.getsize(out), sha(out)))
print('  verdict =', report['verdict'])
print('  契约 rev =', rev, '| bst2sw =', b2['resolution'].get('closedRelayNumbers'))
print('  门禁: %d 门, GREEN=%d, NEW-RED=%s, KNOWN-RED=%s'
      % (len(gates), report['gateSummary']['green'], report['gateSummary']['newRed'], report['gateSummary']['knownRed']))
print('  部署态 TM600 缺 =', sorted(set(exp600) - dep.get('TM600_HS_RDSON', set())))
print('  候选 payload missing =', sorted(set(exp600) - pay.get('TM600_HS_RDSON', set())))


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
    'sha256_lf_normalized': _hl.sha256(_b.replace(b"\r\n", b"\n")).hexdigest(),
    'topLevelEntries': len(_json.loads(_b.decode('utf-8-sig'))),
    'reproducibleBodySha256': _hl.sha256(
        _json.dumps(
            {k: v for k, v in _json.loads(_b.decode('utf-8-sig')).items()
             if k not in ('generatedAt', 'receipts')},
            ensure_ascii=False, sort_keys=True).encode('utf-8')
    ).hexdigest(),
    'reproducibleNote': ('剔除 `generatedAt` 与 `receipts` 后的 body 哈希；projectionSpec v2 ⇒ 跨次生成稳定。'
                         '（更正留痕：v1 曾以"收据历史行 sha 在变"为由，该理由不成立且已撤回。）'),
    'projectionSpec': {
        'exclude': ['generatedAt', 'receipts'],
        'version': 2,
        'serialization': ("json.dumps(body, ensure_ascii=False, sort_keys=True)，分隔符为 Python json 默认，无尾随换行"),
        'encoding': 'utf-8',
        'bodyDefinition': ("body = {k: v for k, v in json.loads(<file bytes>.decode('utf-8-sig')).items() "
                           "if k not in exclude} ⇒ 再按上述 serialization/encoding 序列化后取 sha256"),
        'stabilityNote': ('不稳定来源是 `generatedAt`（每次生成）与 `receipts`；均已排除 ⇒ v2 下跨次稳定。'
                          '⚠️ 排除项 `receipts` 在当前正文中不存在（正文键路径穷举 0 命中）⇒ 属**预防性**，'
                          '本身不构成升版本理由；**升 v2 的正当理由＝v1 未声明序列化与编码 ⇒ 第三方同字节也无法复现**。'),
        'note': ('跨秒不变；跨版本不可混用 —— 排除项/序列化/编码任一变化都必须换版本号。'),
    },
    'standardTriHash': ('活档产物的标准三哈希（用途不同、不可互换）：'
                        'sha256 = 身份（逐字节同盘）；sha256_lf_normalized = 跨序列化可比重（行尾无关）；'
                        'reproducibleBodySha256 = 幂等判定（剔除 generatedAt、跨次可比）。'),
    'hashInvariance': {
        'sha256': '逐字节同盘身份（含 generatedAt ⇒ 跨次重生成会变）',
        'sha256_lf_normalized': '行尾不变（跨编辑器 / CRLF-LF 可比）',
        'reproducibleBodySha256': '时间戳不变（跨秒/跨次可比；用于判内容是否变）',
    },
    'isFrozen': False,
    'appendPolicy': ('**本账本仅在身份（body 哈希，projectionSpec 口径）变化时追加**；'
                     '**因此"一段时间无增长"不等于"无运行"** —— 新策略下运行可以发生而有意不记。'
                     '**运行计数一律查 `runSeq`**。'
                     '⚠️ **制度边界以事件表述、不锚行号**：生效点与【预策略段】规模见 `appendPolicyBoundary`。'),
    'appendPolicyBoundary': {
        'note': ('**事件表述的边界**（自哪个 runSeq 起生效）⇒ 作为**历史事件永久稳定**；'
                 '**本字段不写『账本当前共多少行』** —— 那是**当前测量、必然漂**。'
                 '【预策略段】规模见 `prePolicyCountsAtPolicyWrite`（**带限定名的历史读数**）。'),
        'effectiveFromRunSeq': None,
        'prePolicySegments': None,
    },
    'prePolicyCountsAtPolicyWrite': {
        'note': ('**预策略段（每次运行都追加的那一段）的规模 —— 取值为本字段首次写入时的测量**。'
                 '⚠️ 名字自带限定：这是写入时刻的历史读数，不是账本当前总量。'),
        'lines': None,
        'distinctBodyIdentities': None,
        'asOf': None,
        'frozen': True,
    },
    'lastAppendDecision': {
        'note': ('**本次生成对历史账本的追加决策（每次都会重算、因此总是可见）** —— '
                 '`reason` 只在真正追加的行里出现 ⇒ 在 skip 情形下**结构上不可达** ⇒ '
                 '故把决策放在本字段（收据每次重算），而**不改任何历史行**。'),
        'policy': '仅在身份（reproducibleBodySha256，projectionSpec 口径）变化时追加',
        'appended': None,
        'byIdentity': None,
        'reason': None,
        'ledgerLinesAtDecision': None,
    },
    'countUnitNote': ('计数单位：`lineCount` 是**行的条数**；状态数须按 '
                      '(size, sha256, reproducibleBodySha256, at) 去重后计。'
                      '⚠️ `at` 只到**秒** ⇒ 同秒两次运行得到同 at 同 sha 两行 ⇒ 同 at 不构成同一性；'
                      '故**状态数是运行次数的下界**；精确运行计数请用 `runSeq`；秒级 at 不是计数装置。'
                      '⚠️ 自证请**按行计**（"含该字段的行数 = N / M"），不得按文件计。'),
    'note': '报告为**活档**；本收据每次生成后重算。引用某一版身份请用本文件，勿用报告内的自算哈希。',
}
_rec_p = os.path.join(RUN, 'gate-logs-t54', 'build-report.receipt.json')
open(_rec_p, 'w', encoding='utf-8').write(_json.dumps(_rec, ensure_ascii=False, indent=2))
print('RECEIPT %s (%d B)' % (_rec_p, os.path.getsize(_rec_p)))


# ==== RECEIPT_HISTORY_V1：收据历史账本（append-only）====
# rule-reviewer 指出：收据若每次覆写 ⇒ 只留"最近一版"身份，与"只增不改"精神不一致。
#   故：`receipt.json` 仍作最新版便利指针；另设 `receipts.jsonl` 追加历史行（含链式字段）。
_hist_p = os.path.join(RUN, 'gate-logs-t54', 'build-report.receipts.jsonl')
_prev_lines = []
_known_bodies = set()
if os.path.isfile(_hist_p):
    # 读**字节**并去掉行终止符（本文件为 CRLF ⇒ \r 一并去掉）；与 meta 的可执行定义一致
    _raw = open(_hist_p, 'rb').read()
    _prev_lines = [l for l in _raw.split(b'\n') if l.strip()]
    for _l in _prev_lines:                       # 收集既有"身份"（body 哈希）
        try:
            _known_bodies.add(_json.loads(_l).get('reproducibleBodySha256'))
        except Exception:
            pass
_line = dict(_rec)
_line['lineCount'] = len(_prev_lines) + 1   # **行的条数**（不是状态数）
_line['runSeq'] = (len(_prev_lines) + 1)   # **单调序号**：秒级 at 无法分离同秒事件（schematic-expert ③）
# 字段定义（务必区分）：
#   prevLineSha256    = 上一行**原始行字节**的 sha256 —— **链用的就是它**
#   ledger_self_sha256= 本行**语义摘要**的 sha256 —— **不是链用的那个**（用错会得错结论）
_line['prevLineSha256'] = (_hl.sha256(_prev_lines[-1].rstrip(b'\r\n')).hexdigest() if _prev_lines else None)  # CRLF ⇒ rstrip
_line['ledger_self_sha256'] = _hl.sha256(
    (b'\n'.join(_prev_lines) + b'\n' + _json.dumps(_line, ensure_ascii=False).encode('utf-8'))
).hexdigest()
_line['reason'] = ('identity-change' if _rec.get('reproducibleBodySha256') not in _known_bodies
                          else 'routine-reverify (identity unchanged => NOT appended)')
_rec['appendPolicyBoundary']['effectiveFromRunSeq'] = len(_prev_lines) + 1
_rec['appendPolicyBoundary']['prePolicySegments'] = len(_prev_lines)
# 冻结：优先从**已落盘的 meta 档**读回（否则每次重建都会『首次写入』⇒ asOf 反复刷新）
_ppc_prev = {}
try:
    _mp = os.path.join(RUN, 'gate-logs-t54', 'build-report.receipts.meta.json')
    if os.path.isfile(_mp):
        _ppc_prev = (_json.loads(io.open(_mp, encoding='utf-8-sig').read())
                     .get('prePolicyCountsAtPolicyWrite') or {})
except Exception:
    _ppc_prev = {}
if _ppc_prev.get('lines') is not None:
    _rec['prePolicyCountsAtPolicyWrite'] = _ppc_prev          # 已冻结 ⇒ 原样保留
else:
    _ppc = _rec['prePolicyCountsAtPolicyWrite']
    _ppc['lines'] = len(_prev_lines)
    _ppc['distinctBodyIdentities'] = len(_known_bodies - {None})
    _ppc['asOf'] = _dt.datetime.now().astimezone().isoformat(timespec='seconds')
    # 落盘到 meta 档，作为**冻结的历史读数**（下一次生成即可读回）
    try:
        _mp = os.path.join(RUN, 'gate-logs-t54', 'build-report.receipts.meta.json')
        _mj = (_json.loads(io.open(_mp, encoding='utf-8-sig').read())
               if os.path.isfile(_mp) else {})
        _mj['prePolicyCountsAtPolicyWrite'] = _ppc
        open(_mp, 'w', encoding='utf-8').write(_json.dumps(_mj, ensure_ascii=False, indent=2))
    except Exception:
        pass
_appended = _rec.get('reproducibleBodySha256') not in _known_bodies
_rec['lastAppendDecision']['appended'] = _appended
_rec['lastAppendDecision']['byIdentity'] = _rec.get('reproducibleBodySha256')
_rec['lastAppendDecision']['reason'] = ('identity-change' if _appended
                                        else 'routine-reverify (identity unchanged => NOT appended)')
_rec['lastAppendDecision']['ledgerLinesAtDecision'] = len(_prev_lines)
open(_rec_p, 'w', encoding='utf-8').write(_json.dumps(_rec, ensure_ascii=False, indent=2))
if _appended:
    with io.open(_hist_p, 'a', encoding='utf-8') as _f:
        _f.write(_json.dumps(_line, ensure_ascii=False) + '\n')
    print('RECEIPT-HISTORY appended lineCount=%d reason=identity-change' % _line['lineCount'])
else:
    print('RECEIPT-HISTORY skipped (routine re-verify; identity unchanged)')
    _ = _line['reason']


# ==== RECEIPT_META_V1：定义档（带版本 + 自身身份）====
# schematic-expert ③：定义档自身也会漂 ⇒ 必须带版本，且定义按版本引用（递归以钉定版本号终止）
_meta_p = os.path.join(RUN, 'gate-logs-t54', 'build-report.receipts.meta.json')
try:
    _m = io.open(_meta_p, encoding='utf-8-sig').read() if os.path.isfile(_meta_p) else None
    _mj = _json.loads(_m) if _m else {}
except Exception:
    _mj = {}
_mj.setdefault('ledger', 'build-report.receipts.jsonl')
_mj['metaVersion'] = _mj.get('metaVersion', 1)
_mj['fieldDefinitions'] = _mj.get('fieldDefinitions') or {
    'prevLineSha256': '上一行原始行字节的 sha256（链用的就是它）',
    'ledger_self_sha256': '本行语义摘要的 sha256（不是链用的那个）',
    'live_sha256': '当次生成时刻的整文件字节哈希',
    'live_lf_sha256': '同上，但行尾归一化（LF）后',
    'reproducibleBodySha256': '剔除 projectionSpec.exclude 后的 body 哈希（幂等/内容判定用）',
}
_mj['warning'] = ('prevLineSha256（链）与 ledger_self_sha256（语义摘要）不是同一个东西；'
                  '用错定义会得到看起来可信的错结论（本 run 实测）')
_mj['metaIdentity'] = {'note': ('本档自身也会漂 ⇒ 带版本 + 定义按版本引用；'
                                '身份字段为上一次生成时现算；引用请按版本号 + 当次现算身份'),
                       'metaAt': _dt.datetime.now().astimezone().isoformat(timespec='seconds')}
open(_meta_p, 'w', encoding='utf-8').write(_json.dumps(_mj, ensure_ascii=False, indent=2))
_b2 = open(_meta_p, 'rb').read()
_mj['metaIdentity']['metaSha256_atWrite'] = _hl.sha256(_b2).hexdigest()
_mj['metaIdentity']['metaSize_atWrite'] = len(_b2)
open(_meta_p, 'w', encoding='utf-8').write(_json.dumps(_mj, ensure_ascii=False, indent=2))
print('RECEIPT-META v%s (%d B)' % (_mj['metaVersion'], os.path.getsize(_meta_p)))
