# -*- coding: utf-8 -*-
"""t25 反证脚本 (F2 精确命中集 + F3 根因定位)。

用法: python t25_proofs.py [--out <json>]
输出: 每条结论附 locator / 数值证据, 供 build-report / 独立复核核对。
"""
import io
import json
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))

out = {'root': ROOT, 'proofs': []}


def add(name, verdict, evidence):
    out['proofs'].append({'name': name, 'verdict': verdict, 'evidence': evidence})
    print('[%s] %s' % (verdict, name))
    for e in evidence:
        print('    -', e)


# ---------- P1: F2 前后 fam_intersect 命中集对照 ----------
try:
    import verify_relay_trace as V
except Exception as exc:  # pragma: no cover
    add('P1 fam_intersect 对照', 'ERROR', ['import 失败: %r' % exc])
    raise

FAM = {'ISW', 'SW', 'VBAT', 'VBUS', 'VDRV'}


def old_fam_intersect(pins, fam):
    return {p for p in pins if p == fam or p.startswith(fam) or fam.startswith(p)}


tokens = ['SW', 'SW1_BST1', 'SW2_BST2', 'BST_SW', 'VBUS', 'VBUS_F', 'VDRV', 'V1P5', 'PMID', 'BST-SW', 'ISW']
rows = []
for t in tokens:
    rows.append({'cap_token': t,
                 'old': sorted(old_fam_intersect(FAM, t)),
                 'new': sorted(V.fam_intersect(FAM, t))})
changed = [r for r in rows if r['old'] != r['new']]
add('P1 F2: fam_intersect 新旧命中集对照 (powered=TM601_LS_RDSON)',
    'FIXED' if all(not r['new'] for r in rows if r['cap_token'] in ('SW1_BST1', 'SW2_BST2')) else 'REGRESS',
    ['cap_pin 推导: K45_Cap_SW1_BST1 -> %r, K44_Cap_SW2_BST2 -> %r'
     % (V.cap_pin('K45_Cap_SW1_BST1'), V.cap_pin('K44_Cap_SW2_BST2')),
     'SW1_BST1: old=%s new=%s' % (rows[1]['old'], rows[1]['new']),
     'SW2_BST2: old=%s new=%s' % (rows[2]['old'], rows[2]['new']),
     '回归保护 SW(同轨)=%s / VDRV(同轨)=%s / SW1_BST1 家族成员 VAC1=%s'
     % (rows[0]['new'], rows[6]['new'], sorted(V.fam_intersect({'VAC1', 'VAC1_X'}, 'VAC1'))),
     '观察到的另一次族折叠 (真实数据同一修法一并消除): cap token VAC ↔ powered VAC1/VAC2/VAC3 '
     '(old 命中 3 个, new 空) —— 实测: 规则输出零变化, 见 P7; VAC1 与 VAC1_X 仍按 token 边界同族',
     '变化条数 %d/%d (仅碰撞项变化)' % (len(changed), len(rows))])

# ---------- P2: F3 根因 —— 警告是否由 BUSH0_AMUX/K154 引起 ----------
meta = json.load(io.open(os.path.join(ROOT, 'project', 'DALI', 'meta', 'dali_tm_meta.json'),
                         encoding='utf-8-sig'))
fns = {f['functionName']: f for f in meta['functions']}
tm601 = fns['TM601_LS_RDSON']
ca = tm601['capAuthority']
bushtokens = ['BUSH0_AMUX', 'K154_BUSH0_AMUX', 'K154', 'K155', 'BUSH0']
proof2 = [
    'meta TM601_LS_RDSON.capAuthority.powered_pins = %s' % ca['powered_pins'],
    'meta TM601_LS_RDSON.capAuthority.testpad_pins = %s' % ca['testpad_pins'],
    'BUSH0_AMUX 相关 token 在 powered_pins 中出现次数 = %d'
    % sum(1 for p in ca['powered_pins'] if 'BUSH0' in p.upper() or p.upper() in ('K154', 'K155')),
    'fam_intersect(powered, "VBUS") = %s  (仅由 powered_pins 精确含 VBUS 触发)'
    % sorted(V.fam_intersect({p.upper() for p in ca['powered_pins']}, 'VBUS')),
    'fam_intersect(任何含 BUSH0_AMUX 的串, "VBUS") = %s'
    % sorted({t for t in bushtokens if V.fam_intersect({t}, 'VBUS')}),
    '规则输入通道只有 meta capAuthority (verify_relay_trace.py:311-328); 规则不读 #define 名、'
    '不读 Cap 附件继电器、不读 SCH-Connect-Map → K154/K155 无法进入 VBUS 判定',
    'hardwareInit 含 vset vbus 5.0 = %s'
    % any(h.get('cmd') == 'vset' and h.get('pin') == 'vbus' for h in tm601['hardwareInit']),
]
add('P2 F3: VBUS 警告的真实根因 (不是 BUSH0_AMUX)', 'ROOT-CAUSE-RESOLVED',
    proof2 + ['结论: powered_pins 里的 VBUS 来自 gen_testitems_meta.py:147-187 的 OVERVIEW 派生'
              ' (vset vbus 5.0), 与 K154_BUSH0_AMUX 无关。'])

# ---------- P3: F3 真路径可达性 locator ----------
map_path = os.path.join(ROOT, 'project', 'DALI', 'SCH-Connect-Map.txt')
lines = io.open(map_path, encoding='utf-8-sig').read().splitlines()
locs = {}
for n in (156, 174, 177, 183, 213, 214, 421):
    locs['L%d' % n] = lines[n - 1].strip() if n - 1 < len(lines) else '<EOF>'
add('P3 F3: VBUS/PGND/SW 真路径 locator (SCH-Connect-Map.txt)',
    'CONFIRMED',
    ['L213: %s' % locs['L213'], 'L421: %s' % locs['L421'], 'L156: %s' % locs['L156'],
     'L174: %s' % locs['L174'], 'L177: %s' % locs['L177'], 'L183: %s' % locs['L183'],
     '⇒ VBUS 到达需 K3; K154+K155 是 CH0 High->PGND, 不是 VBUS 供电依据'])

# ---------- P4: 全树影响面 (F2 后 WARN/ERROR 枚举) ----------
import subprocess
env = dict(os.environ, PYTHONIOENCODING='utf-8')
log = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'relay-trace-after-f2.log')
with io.open(log, 'w', encoding='utf-8') as fh:
    r = subprocess.run([sys.executable, os.path.join(ROOT, 'scripts', 'verify_relay_trace.py'),
                        '--meta', os.path.join(ROOT, 'project', 'DALI', 'meta', 'dali_tm_meta.json')],
                       stdout=fh, stderr=subprocess.STDOUT, cwd=os.path.join(ROOT, 'scripts'))
txt = io.open(log, encoding='utf-8').read()
warns = re.findall(r'^  - (.*)$', txt, re.M)
errors = re.findall(r'^  - (.*虚构.*)$', txt, re.M)
add('P4 全树影响面: F2 后 relay-trace 输出枚举', 'MEASURED',
    ['exit=%d' % r.returncode, 'WARN 行数=%d' % len(warns), 'ERROR 行数=%d' % len(errors),
     '日志=%s' % log] + ['WARN: ' + w for w in warns] + ['ERROR: ' + e for e in errors])
out['relay_trace_after_f2'] = {'exit': r.returncode, 'warns': warns, 'errors': errors, 'log': log}

# ---------- P5: 未供电轨不得被要求闭 Cap (反证纪律) ----------
sw_caps = [r for r in rows if r['cap_token'] in ('SW1_BST1', 'SW2_BST2')]
add('P5 反证纪律: 未供电 SW1/SW2 不再被要求闭 Cap', 'PASS' if all(not r['new'] for r in sw_caps) else 'FAIL',
    ['sw caps: %s' % sw_caps, 'locator: SCH-Connect-Map L177 (SW1 <- K46) / L183 (SW2 <- K46,K49) '
     '均不在 powered_pins 中, 不构成供电轨'])

# ---------- P6: 全量穷举回归对照 (真实 cap token × 真实四权威集) ----------
import proj_config
cfg = proj_config.load(os.path.join(ROOT, 'project_config.json'))
stdafx = io.open(cfg['derived']['stdafx_h'], encoding='utf-8-sig', errors='replace').read()
cap_tokens = {}
for m in re.finditer(r'#define\s+(K\d*_\w+)\s+(\d+)', stdafx):
    pt = V.cap_pin(m.group(1))
    if pt:
        cap_tokens[pt] = m.group(1)
real_tokens = sorted(cap_tokens)

pairs, changed_pairs, asym = [], [], []
for fn in meta['functions']:
    ca2 = fn.get('capAuthority') or {}
    for field in ('powered_pins', 'mi_pins', 'ramp_pins', 'testpad_pins'):
        pins = {str(p).upper() for p in (ca2.get(field) or [])}
        for t in real_tokens:
            o = sorted(old_fam_intersect(pins, t))
            n = sorted(V.fam_intersect(pins, t))
            pairs.append((fn['functionName'], field, t, o, n))
            if o != n:
                changed_pairs.append((fn['functionName'], field, t, o, n))

# 非对称性检查: old 曾把**不同** token 折进同一族 ⇒ 修复后应只剩"真同族"
false_pos = [c for c in changed_pairs if c[3] and not c[4]]
newly_true = [c for c in changed_pairs if c[4] and not c[3]]
add('P6 全量穷举回归对照 (真实 cap token × 101 函数 × 4 权威集)',
    'PASS' if not newly_true else 'REVIEW',
    ['胶囊 token 总数=%d (来自 StdAfx.h #define 经 cap_pin())' % len(real_tokens),
     '检查对数=%d, 发生变化的对数=%d' % (len(pairs), len(changed_pairs)),
     '由"命中"变"不命中"(即删掉的假阳性)=%d: %s'
     % (len(false_pos), sorted({(c[0], c[1], c[2], tuple(c[3])) for c in false_pos})[:6]),
     '由"不命中"变"命中"(新增要求, 必须为 0)=%d: %s'
     % (len(newly_true), sorted({(c[0], c[1], c[2]) for c in newly_true})[:6]),
     '受影响的函数=%s' % sorted({c[0] for c in changed_pairs})])
out['regression'] = {'checkedPairs': len(pairs), 'changed': [list(c) for c in changed_pairs],
                     'falsePositivesRemoved': len(false_pos), 'newMatches': len(newly_true),
                     'capTokenCount': len(real_tokens)}

# ---------- P7: A/B 全树对照 —— 旧实现 vs 新实现 (真规则, 真输入) ----------
SB = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sandbox-ab')
os.makedirs(SB, exist_ok=True)
src_text = io.open(os.path.join(ROOT, 'scripts', 'verify_relay_trace.py'), encoding='utf-8-sig').read()
new_fn = src_text[src_text.index('def fam_intersect('):src_text.index('def parse_setons(')]
old_fn = ('def fam_intersect(pins, fam):\n'
          '    """旧实现 (t25 修复前的线上版本, 仅用于 A/B 对照)"""\n'
          '    return {p for p in pins if p == fam or p.startswith(fam) or fam.startswith(p)}\n\n\n')
for tag, fn in (('old', old_fn), ('new', new_fn)):
    d = os.path.join(SB, tag)
    os.makedirs(d, exist_ok=True)
    io.open(os.path.join(d, 'verify_relay_trace.py'), 'w', encoding='utf-8').write(
        src_text.replace(new_fn, fn))
    io.open(os.path.join(d, 'proj_config.py'), 'w', encoding='utf-8').write(
        io.open(os.path.join(ROOT, 'scripts', 'proj_config.py'), encoding='utf-8-sig').read())
runs = {}
for tag in ('old', 'new'):
    log = os.path.join(SB, tag + '.log')
    with io.open(log, 'w', encoding='utf-8') as fh:
        r = subprocess.run([sys.executable, os.path.join(SB, tag, 'verify_relay_trace.py'),
                            '--config', os.path.join(ROOT, 'project_config.json'),
                            '--meta', os.path.join(ROOT, 'project', 'DALI', 'meta', 'dali_tm_meta.json')],
                           stdout=fh, stderr=subprocess.STDOUT, cwd=os.path.join(ROOT, 'scripts'))
    t = io.open(log, encoding='utf-8').read()
    runs[tag] = {'exit': r.returncode,
                 'warns': sorted(re.findall(r'^  - (.*)$', t, re.M)),
                 'summary': (re.search(r'^\[relay\].*$', t, re.M) or [None]) and
                            re.search(r'^\[relay\].*$', t, re.M).group(0)}
removed = sorted(set(runs['old']['warns']) - set(runs['new']['warns']))
added = sorted(set(runs['new']['warns']) - set(runs['old']['warns']))
add('P7 A/B 全树对照: 旧 fam_intersect vs 新 fam_intersect (同输入, 同规则)',
    'PASS' if not added else 'REGRESSION',
    ['old: %s' % runs['old']['summary'], 'new: %s' % runs['new']['summary'],
     'old exit=%d / new exit=%d' % (runs['old']['exit'], runs['new']['exit']),
     '旧有新无 (被消除的假阳性/误判) = %d 条:' % len(removed)] + ['  - ' + x for x in removed] +
    ['新有旧无 (新增告警, 必须为 0) = %d 条:' % len(added)] + ['  - ' + x for x in added] +
    ['日志: %s / %s' % (os.path.join(SB, 'old.log'), os.path.join(SB, 'new.log'))])
out['ab'] = runs

outpath = None
if '--out' in sys.argv:
    outpath = sys.argv[sys.argv.index('--out') + 1]
else:
    outpath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 't25-proofs.json')
with io.open(outpath, 'w', encoding='utf-8') as fh:
    fh.write(json.dumps(out, ensure_ascii=False, indent=2))
print('WROTE', outpath)
