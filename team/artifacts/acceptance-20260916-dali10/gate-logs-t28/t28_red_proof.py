# -*- coding: utf-8 -*-
"""t28 RED-proof harness —— 证明"重生成静默抹除 meta 修正"从**检不出**变成**可检出失败**。

方法 (只读现盘 meta, 不动 project/DALI/meta):
  1. 造一份**副本 config**: 其余字段与 project_config.json 完全一致, 只把 `outputs.meta`
     指向探针内容 `t26-regen-probe/dali_tm_meta.regen.json` (== t26 覆盖前逐字节的 meta)。
     副本放在 `gate-logs-t28/` 内 → 相对路径 (project/..., scripts/...) 仍解析到 workspace 根,
     而 meta 指向探针 ⇒ 完整模拟"重生成把 meta 还原"这一回退。
  2. 用**修复前**脚本跑副本 config → 期望 `IN SYNC` / exit 0  ⇒ 证明原风险真实 (**检不出**)。
  3. 用**修复后**脚本跑副本 config → 期望 RS-1..RS-4 变红 / exit 1 ⇒ 证明回退可检出。

用法: python t28_red_proof.py
"""
import hashlib
import io
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.abspath(os.path.join(HERE, '..'))
WS = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
PROBE = os.path.join(RUN, 't26-regen-probe', 'dali_tm_meta.regen.json')
OLD = os.path.join(HERE, 'backups', 'check_input_sync.py.pret28')   # 修复前脚本
NEW = os.path.join(WS, 'scripts', 'check_input_sync.py')            # 修复后脚本


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def stage_old_script():
    """修复前脚本要能 import proj_config ⇒ 同目录放一份副本 (不改任何被测文件)。"""
    dst = os.path.join(HERE, 'backups', 'proj_config.py')
    src = os.path.join(WS, 'scripts', 'proj_config.py')
    if not os.path.isfile(dst) or sha(dst) != sha(src):
        io.open(dst, 'wb').write(open(src, 'rb').read())
    return dst


def build_regen_yaml():
    """忠实模拟"重生成": 生成器会**同拍刷新** yaml 的 `_sync.metaSha256` (写新 meta 的哈希)。

    线上 yaml 是 DLP 保护文件且不在本任务 inScope ⇒ 只写**副本** yaml (一行戳改为探针 meta 的哈希)。
    这正是 t26 F2 的核心: 旧门把"重新同步过的戳"当成同步证据, 于是语义回退**完全没有红点**。
    """
    src = os.path.join(WS, 'project', 'DALI', 'meta', 'test_conditions.yaml')
    raw = open(src, 'rb').read()
    bom = raw[:3] == b'\xef\xbb\xbf'
    txt = raw.decode('utf-8-sig')
    new_sha = sha(PROBE)
    out_lines = []
    hit = 0
    for ln in txt.split('\n'):
        if ln.strip().startswith('metaSha256:') and hit == 0:
            out_lines.append('  metaSha256: %s' % new_sha)
            hit += 1
        else:
            out_lines.append(ln)
    if hit != 1:
        raise SystemExit('ERROR: 未能在副本 yaml 中定位唯一 metaSha256 行 (hit=%d)' % hit)
    dst = os.path.join(HERE, 'redproof-test_conditions.regen.yaml')
    data = '\n'.join(out_lines).encode('utf-8')
    io.open(dst, 'wb').write((b'\xef\xbb\xbf' + data) if bom else data)
    return dst


def build_copy_config():
    """副本 config: 只改 outputs.meta → 探针 (yaml 戳同步改为探针哈希), 其余路径**全部绝对化**。

    为什么必须绝对化: proj_config.load() 以**配置文件所在目录**为相对路径基准
    (`root = os.path.dirname(config_path)`)。副本放在 gate-logs-t28/ 下, 若保留相对路径,
    连 DFT/SCH 输入都会解析到副本目录 ⇒ 门会因"输入缺失"报红, 那**不是**我们要证的"静默抹除检出"。
    绝对化后: 除 meta(yaml) 处于回退态外, 其余输入/产物与线上完全同一批文件。
    """
    cfg = json.load(io.open(os.path.join(WS, 'project_config.json'), encoding='utf-8-sig'))
    for sec in ('inputs', 'optional_inputs', 'intermediates', 'outputs'):
        for k, v in (cfg.get(sec) or {}).items():
            if v and not os.path.isabs(str(v)):
                cfg[sec][k] = os.path.normpath(os.path.join(WS, str(v))).replace('\\', '/')
    cfg['outputs']['meta'] = PROBE.replace('\\', '/')
    cfg['outputs']['test_conditions'] = build_regen_yaml().replace('\\', '/')
    cfg['_t28RedProof'] = ('副本 config: outputs.meta 指向 t26 重生成探针 (== 覆盖前逐字节 meta), '
                           'outputs.test_conditions 指向戳已同步刷新的副本 yaml ⇒ 完整模拟重生成后的回退态; '
                           '其余路径已绝对化。')
    dst = os.path.join(HERE, 'redproof-config.probe-meta.json')
    io.open(dst, 'w', encoding='utf-8').write(json.dumps(cfg, ensure_ascii=False, indent=2))
    return dst


def run(script, cfg, logname):
    log = os.path.join(HERE, logname)
    with io.open(log, 'w', encoding='utf-8') as fh:
        r = subprocess.run([sys.executable, script, '--config', cfg],
                           stdout=fh, stderr=subprocess.STDOUT, cwd=os.path.join(WS, 'scripts'))
    txt = io.open(log, encoding='utf-8').read()
    return r.returncode, log, txt


def main():
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except AttributeError:
        pass
    cfg = build_copy_config()
    staged = stage_old_script()
    print('修复前脚本的同目录依赖已就位: %s' % staged)
    print('探针 (回退态 meta) = %s' % PROBE)
    print('   %d B / %s' % (os.path.getsize(PROBE), sha(PROBE)))
    print('   与 t26 覆盖前现盘 meta 逐字节相同 (1c8496645492f7b7...): %s'
          % (sha(PROBE) == '1c8496645492f7b75abf3a89f95679291490399d62f4a1a34d6cc5d8b1aa2693'))
    print('副本 config = %s\n' % cfg)

    out = {'probe': PROBE, 'probeSha256': sha(PROBE), 'copyConfig': cfg, 'runs': {}}
    for tag, script, logname in (('BEFORE_fix', OLD, 'redproof-before-fix.log'),
                                 ('AFTER_fix', NEW, 'redproof-after-fix.log')):
        code, log, txt = run(script, cfg, logname)
        rs_lines = [l.strip() for l in txt.splitlines() if '[RS-' in l or 'RS-FAIL' in l or 'NEW-RED' in l]
        verdict = 'IN SYNC' if 'IN SYNC' in txt else ('OUT OF SYNC' if 'OUT OF SYNC' in txt else '?')
        out['runs'][tag] = {'script': script, 'scriptSha256': sha(script), 'exitCode': code,
                            'log': log, 'logSha256': sha(log), 'verdict': verdict,
                            'rsLines': rs_lines}
        print('%s  exit=%d  verdict=%s  script=%s' % (tag, code, verdict,
                                                      os.path.basename(script)))
        for l in rs_lines:
            print('    ' + l[:200])
        print('    log=%s  sha256=%s' % (log, sha(log)[:16]))
        print()

    ok = (out['runs']['BEFORE_fix']['exitCode'] == 0 and out['runs']['BEFORE_fix']['verdict'] == 'IN SYNC'
          and out['runs']['AFTER_fix']['exitCode'] == 1 and out['runs']['AFTER_fix']['verdict'] == 'OUT OF SYNC'
          and sum(1 for l in out['runs']['AFTER_fix']['rsLines'] if 'RS-FAIL' in l) >= 4)
    out['redProofPassed'] = bool(ok)
    print('RED-PROOF PASSED = %s  (修复前检不出 / 修复后 4 条 RS 全红且 exit=1)' % ok)
    io.open(os.path.join(HERE, 't28-red-proof.json'), 'w', encoding='utf-8').write(
        json.dumps(out, ensure_ascii=False, indent=2))
    print('WROTE', os.path.join(HERE, 't28-red-proof.json'))
    return 0 if ok else 1


if __name__ == '__main__':
    raise SystemExit(main())
