# -*- coding: utf-8 -*-
r"""_inbox 自动归位脚本 —— Library-Functions 统一管理入口。

用法：
    把新版库文件丢进 Library-Functions\_inbox\ ，然后：
        python -X utf8 ingest.py            # 实际搬移
        python -X utf8 ingest.py --dry-run  # 只预览

规则：
1. 按文件名主干（去扩展名）匹配 Library-Functions 下的类文件夹
   （扫描各文件夹内现有文件的 stem 建映射，大小写不敏感；
    另含别名表 test_method→Test_Method 等）。
2. 同名旧文件覆盖前先备份到 _archive\inbox_backup\<时间戳>\。
3. 识别不了的文件留在 _inbox\ 并在报告中列出，等人工判断。
"""
import os, shutil, sys, time

BASE = os.path.dirname(os.path.abspath(__file__))
INBOX = os.path.join(BASE, '_inbox')
BACKUP_ROOT = os.path.join(BASE, '..', '_archive', 'inbox_backup')
ALIAS = {'test_method': 'Test_Method', 'sharedfunction': 'shared_functions',
         'shared_functions': 'shared_functions', 'subfunc': 'sub_func',
         'sub_func': 'sub_func'}
SKIP_DIRS = {'_inbox'}
SKIP_FILES = {'INDEX.md', 'ingest.py'}


def build_map():
    m = {}
    for entry in sorted(os.listdir(BASE)):
        d = os.path.join(BASE, entry)
        if entry in SKIP_DIRS or not os.path.isdir(d):
            continue
        for fn in os.listdir(d):
            stem = os.path.splitext(fn)[0].lower()
            if stem:
                m.setdefault(stem, entry)
    return m


def main():
    dry = '--dry-run' in sys.argv
    if not os.path.isdir(INBOX):
        print('no _inbox dir, nothing to do'); return
    files = [f for f in os.listdir(INBOX)
             if os.path.isfile(os.path.join(INBOX, f)) and f not in SKIP_FILES]
    if not files:
        print('_inbox is empty'); return
    m = build_map()
    moved, unknown = [], []
    for fn in files:
        stem = os.path.splitext(fn)[0].lower()
        target_dir = m.get(stem) or ALIAS.get(stem.replace('_', '').replace('-', ''))
        if target_dir is None:
            target_dir = ALIAS.get(stem)
        if target_dir is None:
            unknown.append(fn); continue
        src = os.path.join(INBOX, fn)
        dst_dir = os.path.join(BASE, target_dir)
        dst = os.path.join(dst_dir, fn)
        note = ''
        if os.path.exists(dst) and not dry:
            ts = time.strftime('%Y%m%d_%H%M%S')
            bdir = os.path.join(BACKUP_ROOT, ts, target_dir)
            os.makedirs(bdir, exist_ok=True)
            shutil.copy2(dst, os.path.join(bdir, fn))
            note = ' (old backed up)'
        print(f'{fn}  ->  {target_dir}/{fn}{note}')
        if not dry:
            shutil.move(src, dst)
        moved.append((fn, target_dir))
    print(f'--- moved: {len(moved)}, unknown: {len(unknown)} ---')
    for fn in unknown:
        print(f'UNKNOWN (left in _inbox, tell Claude): {fn}')


if __name__ == '__main__':
    main()
