# -*- coding: utf-8 -*-
"""t33：生成 build-report.json —— 本次为 **blocked** 态（两个独立阻塞）。

为什么不做成 pass：t33 的 verify 命令实测 exit=1，且 Release 编译**物理无法执行**
（ForCodexDebug 在本会话沙箱外只读）。按 run 纪律"不把权限失败伪装成实现失败或完成"，
本报告如实记 verdict=blocked，并把已取得的门禁证据与两次阻塞证据完整落盘。

所有哈希均由本脚本**从磁盘现算**（不手抄），避免出现"手抄哈希打错"这类早期失误。
"""
import datetime
import hashlib
import io
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
RUN = os.path.join(WS, 'team', 'artifacts', 'acceptance-20260916-dali10')
LOGDIR = os.path.join(RUN, 'gate-logs-t33')
TARGET = 'D:/PROJECT6-DALI/ForCodexDebug'


def sha(p):
    with open(p, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()


def rel(p):
    return os.path.relpath(p, WS).replace('\\', '/')


def run_entry(command, cwd, started_at, exit_code, log_path):
    return {'command': command, 'cwd': cwd, 'startedAt': started_at, 'exitCode': exit_code,
            'log': rel(log_path), 'logSha256': sha(log_path)}


# ---- 门禁逐门状态（从 run-gates stdout 日志解析, 见 §gates）----
stdout_log = os.path.join(LOGDIR, 'run-gates-t33-stdout.log')
txt = io.open(stdout_log, encoding='utf-8-sig').read()
gate_rows = []
for m in re.finditer(r'^\s{2}(\S+)\s+(.+?)\s+(GREEN|NEW-RED|KNOWN-RED|FIXED)\s+(-?\d+)\s+([\d.]+)\s*$',
                     txt, re.M):
    gate_rows.append({'id': m.group(1), 'desc': m.group(2).strip(), 'status': m.group(3),
                      'exit': int(m.group(4)), 'sec': float(m.group(5))})
full_exit = 1 if 'FULL_EXIT' not in txt else None   # 实测由外层捕获, 见 evidence
suite_exit = 1

# ---- 编译尝试（同一命令内的 -Build 分支）----
build_log = os.path.join(LOGDIR, 'build.log')
build_exit = None
build_msb = None
if os.path.isfile(build_log):
    bt = io.open(build_log, encoding='utf-8-sig', errors='replace').read()
    m = re.search(r'构建失败, 总耗时|构建 \[Release\]', bt)
    m2 = re.search(r'error (MSB\d+)', bt)
    build_msb = m2.group(1) if m2 else None
    build_exit = 1 if 'error MSB' in bt else (0 if 'completed=pass' in bt else None)

# ---- 新增红清单（从 stdout 解析）----
new_red_lines = re.findall(r'^\s+-\s+(\S.*)$', txt, re.M)

# ---- 源码 before/after 锚点（现算 + 与 before 文件比对）----
before = json.load(io.open(os.path.join(LOGDIR, 't33-blocked-before-anchors.json'), encoding='utf-8'))
after = json.load(io.open(os.path.join(LOGDIR, 't33-blocked-after-anchors.json'), encoding='utf-8'))
anchor_rows = []
for k, v in before.items():
    a = after.get(k, {})
    anchor_rows.append({'file': k, 'path': v['path'], 'beforeSize': v['size'],
                        'beforeSha256': v['sha256'], 'afterSize': a.get('size'),
                        'afterSha256': a.get('sha256'), 'unchanged': bool(a.get('unchanged'))})

# ---- 门禁脚本与 t28/t30 产物的落地哈希（t33 要求记录）----
guards = {}
for label, p in (
    ('run_gates.ps1', os.path.join(WS, 'scripts', 'run_gates.ps1')),
    ('gate_baseline.json', os.path.join(WS, 'scripts', 'gate_baseline.json')),
    ('check_input_sync.py (t28 RS 断言)', os.path.join(WS, 'scripts', 'check_input_sync.py')),
    ('verify_bst_sw_sequence.py (t30 契约断言)', os.path.join(WS, 'scripts', 'verify_bst_sw_sequence.py')),
    ('verify_relay_trace.py (t25)', os.path.join(WS, 'scripts', 'verify_relay_trace.py')),
    ('t28-red-proof.json', os.path.join(RUN, 'gate-logs-t28', 't28-red-proof.json')),
    ('t28-summary.md', os.path.join(RUN, 'gate-logs-t28', 't28-summary.md')),
    ('t30-summary.md', os.path.join(RUN, 'gate-logs-t30', 't30-summary.md')),
    ('bst-sw 正控日志 (t30)', os.path.join(RUN, 'gate-logs-t30', 'bst-sw-positive-control.log')),
    ('review/t28-independent-opinion.md', os.path.join(RUN, 'review', 't28-independent-opinion.md')),
):
    guards[label] = {'path': rel(p), 'size': os.path.getsize(p), 'sha256': sha(p)} if os.path.isfile(p) else {'path': rel(p), 'missing': True}

report = {
    'runId': 'acceptance-20260916-dali10',
    'targetRoot': TARGET,
    'configuration': 'Release',
    'producedBy': 'compile-diagnostician (t33, attempt 1 / a49ee326-a0b3-4fe5-a1f9-1afa6fa57f9d)',
    'generatedAt': datetime.datetime.now().astimezone().isoformat(timespec='seconds'),
    'verdict': 'blocked',
    'verdictReason': ('TWO INDEPENDENT BLOCKERS: (1) t29 is task-status=completed but its output is NOT applied to the '
                      'target tree — deployed test.cpp = 15c7d2b8... (mtime 18:53:33) still lacks K109/K110, so t30\'s '
                      'contract assertion reports bst-sw = NEW-RED; t29\'s own output says "REPLACE-and-land remain" for '
                      'the captain. (2) Release compilation is physically impossible from this session: the target tree '
                      'is outside the session workspace and read-only — MSBuild fails with error MSB3491 writing '
                      'source/Release/F12011.tlog/F12011.lastbuildstate (access denied), and a direct write probe to that '
                      'directory is also denied. No build-report may claim a compiled artefact under these conditions.'),
    'gates': [
        run_entry('pwsh -NoProfile -File scripts/run_gates.ps1 -Build -LogDir team/artifacts/acceptance-20260916-dali10/gate-logs-t33',
                  rel(WS), '2026-09-16T19:5x+08:00', suite_exit, stdout_log),
    ],
    'gateTable': gate_rows,
    'gateSummary': {
        'totalGates': len(gate_rows),
        'green': sum(1 for g in gate_rows if g['status'] == 'GREEN'),
        'knownRed': [g['id'] for g in gate_rows if g['status'] == 'KNOWN-RED'],
        'newRed': [g['id'] for g in gate_rows if g['status'] == 'NEW-RED'],
        'baseline': 'gate_baseline.json (cbit) — unchanged; KNOWN-RED is baseline-exempt, NEW-RED is blocking',
        'suiteExitCode': suite_exit,
        'newRedDetail': new_red_lines,
    },
    'builds': [
        run_entry('python scripts/fast_rebuild.ps1 D:/PROJECT6-DALI/ForCodexDebug/source -Config Release -Platform Win32 -Incremental -LogFile <gate-logs-t33/build.log>',
                  rel(WS) + '/scripts', '2026-09-16T19:5x+08:00', build_exit if build_exit is not None else 1,
                  build_log),
    ],
    'buildDetail': {
        'invokedBy': 'scripts/run_gates.ps1 -Build (incremental Build target, Release|Win32)',
        'solution': TARGET + '/source/F12011.sln',
        'msbuildPath': 'C:\\Program Files (x86)\\MSBuild\\12.0\\Bin\\MSBuild.exe',
        'platformToolset': 'v120',
        'platform': 'Win32',
        'result': 'FAILED — not a code error: MSBuild error %s (access denied writing source/Release/F12011.tlog/F12011.lastbuildstate)'
                  % (build_msb or 'MSB3491'),
        'errors': 1, 'warnings': 0,
        'dllUnchanged': {'path': TARGET + '/F12011.dll', 'size': before['F12011.dll']['size'],
                         'sha256': before['F12011.dll']['sha256'], 'mtime': '2026-09-16 18:56:54',
                         'note': 'pre-existing artefact written by an earlier (write-capable) session; NOT built by this task'},
    },
    'sourceAnchors': anchor_rows,
    'guardsLandedHashes': guards,
    'referenceEvidenceNotReused': {
        'note': 'per t33 non-goals, gate-logs-t23 and gate-logs-t23-build were NOT reused as final evidence',
        't23GateLogsPresent': os.path.isdir(os.path.join(RUN, 'gate-logs-t23')),
    },
    'diagnostics': [
        {'id': 'T33-B1', 'severity': 'blocker', 'kind': 'dependency-not-landed',
         'problem': 't29 (K109/K110 closure) reports status=completed but the target tree is unchanged: '
                    'test.cpp 469714 B / 15c7d2b8d37b15648d552ad5dde14e57b5c0d520d05a41c8c41492a06236c01a, '
                    'regex \\bK(109|110)\\b = 0 hits. t29 output: "Independent review (rule-reviewer) and the '
                    'captain\'s REPLACE-and-land remain."',
         'evidence': ['gate-logs-t33/bst-sw.log', 'gate-logs-t33/t33-blocked-before-anchors.json'],
         'neededToClear': 'captain applies the t29 payload to D:/PROJECT6-DALI/ForCodexDebug/source/test.cpp '
                          '(and records the post-landing hash)'},
        {'id': 'T33-B2', 'severity': 'blocker', 'kind': 'sandbox-write-denied',
         'problem': 'Release build cannot write its incremental-build state: MSBuild error MSB3491 on '
                    'source/Release/F12011.tlog/F12011.lastbuildstate; direct write probe to that directory also denied. '
                    'The session sandbox is D:/Newtest/DSH/ATE-Coding-Plat only; D:/PROJECT6-DALI/ForCodexDebug is '
                    'read-only for this agent.',
         'evidence': ['gate-logs-t33/build.log', 'gate-logs-t33/run-gates-t33-stdout.log'],
         'neededToClear': 'either the captain (write-capable) executes the Release build, or this agent is given a '
                          'session whose workspace includes the target tree'},
    ],
    'fixes': [],
    'limitations': [
        'BLOCKED, NOT PASSED: the verify command exited 1 and the Release build did not run to completion; no compiled '
        'artefact was produced by this task.',
        'A successful compile would NOT prove electrical/hardware correctness. No instrument, bench or hardware '
        'verification of any kind was performed. "Compile closed" != "electrically signed off".',
        'BLOCKER-1: t29 is status=completed but NOT landed; the tree under test is the pre-fix tree, so any gate or build '
        'evidence from it describes a tree that is about to be replaced (this is exactly what t33 forbids).',
        'BLOCKER-2: the target tree is read-only from this session (sandbox); MSBuild cannot write '
        'source/Release/F12011.tlog, so Release compilation is impossible here regardless of t29.',
        'The gate table above is nonetheless a valid measurement OF THE CURRENT (pre-fix) TREE and shows the expected '
        'signature: bst-sw = NEW-RED (K110 missing) — i.e. t30\'s guard fires, and no other gate regressed.',
        'Known-red accounting: cbit = KNOWN-RED (baseline-exempt, gate_baseline.json unchanged); relay-trace and '
        'input-sync are GREEN, so t28\'s RS assertions and t25\'s harness fixes are in place and passing.',
        'referenceEvidenceNotReused: gate-logs-t23 / gate-logs-t23-build were deliberately NOT reused as final evidence.',
    ],
}

out = os.path.join(RUN, 'build-report.json')
io.open(out, 'w', encoding='utf-8').write(json.dumps(report, ensure_ascii=False, indent=2))
print('WROTE %s (%d B / %s)' % (rel(out), os.path.getsize(out), sha(out)))
print('  verdict =', report['verdict'])
print('  gateTable rows =', len(gate_rows), '| green =', report['gateSummary']['green'],
      '| newRed =', report['gateSummary']['newRed'], '| knownRed =', report['gateSummary']['knownRed'])
print('  build exit =', report['builds'][0]['exitCode'], '| MSBuild error =', build_msb)
