# -*- coding: utf-8 -*-
# proj_config.py — project_config.json 统一读取器 (唯一输入入口)
# 职责: 读 project_config.json → 相对路径解析为绝对路径 + 从 vs_src_dir 派生源文件。
#   换项目只改 project_config.json, 活跃脚本默认读它 (--config 可覆盖)。
#
# 用法:
#   import proj_config
#   cfg = proj_config.load()                          # 默认读本文件同目录的 project_config.json
#   cfg = proj_config.load('D:/x/other.json')         # 显式指定
#   cfg['_root']                 # workspace 根 (跨项目知识 .claude/references 等用它)
#   cfg['project_dir']           # 项目工作目录绝对路径 (Project/<name>)
#   cfg['inputs']['cbit']        # 外部输入 (绝对路径)
#   cfg['derived']['test_cpp']   # vs_src_dir 派生: test.cpp / sub.cpp / StdAfx.h
#   cfg['intermediates']['sch_connect_map']   # 中间产物绝对路径
#   cfg['outputs']['meta']       # 输出绝对路径
#   proj_config.config_from_argv(sys.argv)    # 从命令行提取 --config (若有)
#
# DLP: project_config.json 也是 DLP 透明加密 → rb 读 + utf-8-sig 回退解码 (与各脚本 read_enc 同法)。

import hashlib
import json
import os

_DEFAULT_CONFIG = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               'project_config.json')
if not os.path.isfile(_DEFAULT_CONFIG):
    # 迁移后: 脚本群在 <workspace>/scripts/ 下, 而 project_config.json 的权威位置是
    # workspace 根 (相对路径以 config 所在目录为基准) → 从自身目录逐级上溯查找。
    _d = os.path.dirname(os.path.abspath(__file__))
    while True:
        _cand = os.path.join(_d, 'project_config.json')
        if os.path.isfile(_cand):
            _DEFAULT_CONFIG = _cand
            break
        _parent = os.path.dirname(_d)
        if _parent == _d:
            break
        _d = _parent


def _read(path):
    with open(path, 'rb') as f:
        raw = f.read()
    for enc in ('utf-8-sig', 'utf-8', 'gbk'):
        try:
            return raw.decode(enc)
        except (UnicodeDecodeError, ValueError):
            continue
    return raw.decode('utf-8', errors='replace')


def _resolve(root, p):
    p = str(p)
    if os.path.isabs(p):
        return os.path.normpath(p)
    return os.path.normpath(os.path.join(root, p))


def _resolve_section(root, sec):
    return {k: _resolve(root, v) for k, v in (sec or {}).items()}


def sha256_file(path):
    """rb 读原始内容(经 DLP 白名单解密) → sha256 十六进制小写；缺失/目录返回 None。

    哈希的是「解密后」内容，故 DLP 透明加密下哈希稳定(不随密文重加密漂移)，
    能真实反映文件内容变化。
    """
    if not path or not os.path.isfile(path):
        return None
    digest = hashlib.sha256()
    with open(path, 'rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def _input_hashes(inputs, derived):
    """对输入文件 + 派生文件算 sha256，返回 {role: {path, sha256, exists}}。

    跳过目录类键(vs_src_dir)与空值；role 用 'input.<key>' / 'derived.<key>'。
    """
    result = {}
    for key, path in inputs.items():
        if key == 'vs_src_dir' or not path:
            continue
        result['input.' + key] = {
            'path': path,
            'sha256': sha256_file(path),
            'exists': os.path.isfile(path),
        }
    for key, path in derived.items():
        result['derived.' + key] = {
            'path': path,
            'sha256': sha256_file(path),
            'exists': os.path.isfile(path),
        }
    return result


def load(config_path=None):
    """读取 project_config.json → 解析后路径 dict (所有路径已绝对化)。"""
    config_path = config_path or _DEFAULT_CONFIG
    config_path = os.path.abspath(config_path)
    if not os.path.exists(config_path):
        raise FileNotFoundError('project_config.json 不存在: ' + config_path)

    data = json.loads(_read(config_path))
    root = os.path.dirname(config_path)

    inputs = _resolve_section(root, data.get('inputs'))
    vs = inputs.get('vs_src_dir', '')
    derived = {
        'test_cpp': os.path.join(vs, 'test.cpp') if vs else '',
        'sub_cpp': os.path.join(vs, 'sub.cpp') if vs else '',
        'stdafx_h': os.path.join(vs, 'StdAfx.h') if vs else '',
    }
    # 显式 derived 段覆盖派生值 (可选, 默认无需手填)
    for k, v in (data.get('derived') or {}).items():
        derived[k] = _resolve(root, v)

    project_dir = _resolve(root, data.get('project_dir', '')) if data.get('project_dir') else ''

    return {
        'project': data.get('project', ''),
        'project_dir': project_dir,
        'inputs': inputs,
        'optional_inputs': _resolve_section(root, data.get('optional_inputs')),
        'intermediates': _resolve_section(root, data.get('intermediates')),
        'outputs': _resolve_section(root, data.get('outputs')),
        'derived': derived,
        '_input_hashes': _input_hashes(inputs, derived),
        '_root': root,
        '_config': config_path,
    }


def config_from_argv(argv):
    """从 sys.argv 列表提取 --config 值(若有), 否则 None。

    守卫: 下一项不是 flag 才当路径 (否则 `--config --foo` 会把 --foo 吞成配置路径,
    静默回落到默认 config)。
    """
    if '--config' in argv:
        i = argv.index('--config')
        if i + 1 < len(argv) and not str(argv[i + 1]).startswith('--'):
            return argv[i + 1]
    return None
