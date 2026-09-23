#!/usr/bin/env python3
"""Popup confirmation of the project material locations.

The Captain runs this whenever an instruction asks to write code. The fixed material
roots and the four project input locations are shown; the user either confirms them
as they are, or clicks Modify, edits them, and then confirms. Confirming writes
Project_Info.json with a fresh approval stamp, which completes this step.

Exit codes: 0 confirmed, 2 no GUI or invalid, 3 cancelled by the user.
"""
from __future__ import annotations
import argparse, datetime, json, os, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import project_info


def describe(value: str) -> str:
    if not str(value).strip():
        return 'EMPTY'
    path = project_info.resolve(value)
    if path.is_dir():
        return 'OK dir'
    if path.is_file():
        return 'OK %d B' % path.stat().st_size
    return 'MISSING'


def rows_of(info: dict) -> list:
    roots = info.get('roots') or {}
    inputs = info.get('inputs') or {}
    rows = [('root', key, '%s  (%s)' % (project_info.ROOT_LABELS[key], key), str(roots.get(key, ''))) for key in project_info.ROOT_KEYS]
    rows += [('input', key, '%s  (%s)' % (project_info.LABELS[key], key), str(inputs.get(key, ''))) for key in project_info.KEYS]
    return rows


def collect(values: dict) -> dict:
    return {'roots': {key: values['root'][key] for key in project_info.ROOT_KEYS},
            'inputs': {key: values['input'][key] for key in project_info.KEYS}}


def apply_and_stamp(info: dict, values: dict, approver: str) -> dict:
    info.update(collect(values))
    return project_info.stamp_approval(info, approver, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))


def invalid(values: dict) -> list:
    candidate = {'projectDir': project_info.load().get('projectDir') if project_info.load() else 'project/DALI'}
    candidate.update(collect(values))
    candidate['approval'] = {'inputsDigest': project_info.inputs_digest(candidate)}
    return [item for item in project_info.problems(candidate) if 'not approved yet' not in item]


def run_gui(info: dict, approver: str):
    import tkinter as tk
    from tkinter import messagebox

    outcome = {'code': 2, 'info': info}
    root = tk.Tk()
    root.title('Project_Info - %s' % info.get('project', ''))
    root.resizable(False, False)

    tk.Label(root, justify='left', anchor='w',
             text='Confirm the fixed material roots and the four project input locations.\n'
                  'Click Confirm to finish this step, or Modify to edit them first.'
             ).grid(row=0, column=0, columnspan=3, sticky='w', padx=14, pady=(14, 10))

    widgets = []
    for index, (kind, key, label, value) in enumerate(rows_of(info), start=1):
        tk.Label(root, text=label, anchor='w').grid(row=index, column=0, sticky='w', padx=(14, 8), pady=3)
        var = tk.StringVar(value=value)
        entry = tk.Entry(root, textvariable=var, width=68, state='readonly')
        entry.grid(row=index, column=1, sticky='we', pady=3)
        status = tk.Label(root, text=describe(value), width=12, anchor='w')
        status.grid(row=index, column=2, sticky='w', padx=(8, 14), pady=3)
        widgets.append((kind, key, var, entry, status))

    def refresh(*_):
        for _kind, _key, var, _entry, status in widgets:
            status.config(text=describe(var.get()))

    def on_modify():
        for _kind, _key, _var, entry, _status in widgets:
            entry.config(state='normal')
        modify.config(text='Modify (editing)', state='disabled')
        widgets[0][3].focus_set()

    def on_confirm():
        values = {'root': {}, 'input': {}}
        for kind, key, var, _entry, _status in widgets:
            values[kind][key] = var.get().strip()
        missing = invalid(values)
        if missing:
            messagebox.showerror('Invalid location', 'Fix these first:\n\n' + '\n'.join(missing))
            return
        outcome['info'] = apply_and_stamp(dict(info), values, approver)
        outcome['code'] = 0
        messagebox.showinfo('Done', 'The material locations are confirmed. This step is complete.')
        root.destroy()

    def on_cancel():
        outcome['code'] = 3
        root.destroy()

    row = len(widgets) + 1
    tk.Button(root, text='Confirm', width=14, command=on_confirm).grid(row=row, column=0, sticky='e', padx=(14, 6), pady=(14, 14))
    modify = tk.Button(root, text='Modify', width=16, command=on_modify)
    modify.grid(row=row, column=1, sticky='w', padx=6, pady=(14, 14))
    tk.Button(root, text='Cancel', width=14, command=on_cancel).grid(row=row, column=2, sticky='w', padx=(6, 14), pady=(14, 14))

    for _kind, _key, var, _entry, _status in widgets:
        var.trace_add('write', refresh)

    root.mainloop()
    return outcome['code'], outcome['info']


def describe_rows(info: dict) -> dict:
    return {'%s:%s' % (kind, key): {'value': value, 'status': describe(value)}
            for kind, key, _label, value in rows_of(info)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--by', default=os.environ.get('USERNAME') or 'user')
    ap.add_argument('--selftest', action='store_true')
    ap.add_argument('--show', action='store_true')
    args = ap.parse_args()

    info = project_info.load() or project_info.propose()

    if args.show:
        print(json.dumps({'path': str(project_info.PROJECT_INFO), 'info': info,
                          'rows': describe_rows(info), 'problems': project_info.problems(info)},
                         ensure_ascii=False, indent=2))
        return 0

    if args.selftest:
        values = {'root': {k: str((info.get('roots') or {}).get(k, '')) for k in project_info.ROOT_KEYS},
                  'input': {k: str((info.get('inputs') or {}).get(k, '')) for k in project_info.KEYS}}
        staged = apply_and_stamp(dict(info), values, args.by + ' (selftest)')
        print(json.dumps({'selftest': 'ok', 'rows': describe_rows(staged), 'invalid': invalid(values),
                          'problems_after_confirm': project_info.problems(staged), 'wrote_file': False},
                         ensure_ascii=False, indent=2))
        return 0

    try:
        code, info = run_gui(info, args.by)
    except Exception as exc:
        print(json.dumps({'state': 'NO_GUI', 'reason': str(exc),
                          'hint': 'run: python scripts/project_info_dialog.py --show', 'info': info},
                         ensure_ascii=False, indent=2))
        return 2

    if code == 0:
        project_info.write(info)
    print(json.dumps({'exit': code, 'approved': code == 0, 'path': str(project_info.PROJECT_INFO),
                      'approval': info.get('approval'), 'rows': describe_rows(info),
                      'problems': project_info.problems(project_info.load() if code == 0 else info)},
                     ensure_ascii=False, indent=2))
    return code


if __name__ == '__main__':
    raise SystemExit(main())
