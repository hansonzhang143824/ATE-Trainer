#!/usr/bin/env python3
"""Project_Info gate: report, write or approve the user-confirmed project paths.

  python scripts/project_info_gate.py check                     # report state; exit 2 when not usable
  python scripts/project_info_gate.py propose                   # print discovered candidates
  python scripts/project_info_gate.py write --from-discovery     # create/overwrite from candidates
  python scripts/project_info_gate.py write --file <json>        # create/overwrite from a JSON file
  python scripts/project_info_gate.py approve --by <name>        # stamp the user's approval
"""
from __future__ import annotations
import argparse, datetime, json, sys
from pathlib import Path
import project_info


def state() -> dict:
    info = project_info.load()
    problems = project_info.problems(info)
    return {'state': 'PROJECT_INFO', 'path': str(project_info.PROJECT_INFO),
            'exists': info is not None, 'usable': not problems, 'problems': problems,
            'approval': (info or {}).get('approval'),
            'inputsDigest': project_info.inputs_digest(info) if info else None,
            'info': info}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('command', choices=('check', 'propose', 'write', 'approve'))
    ap.add_argument('--from-discovery', action='store_true')
    ap.add_argument('--file')
    ap.add_argument('--by', default='user')
    args = ap.parse_args()

    if args.command == 'propose':
        print(json.dumps(project_info.propose(), ensure_ascii=False, indent=2))
        return 0
    if args.command == 'write':
        info = project_info.propose() if args.from_discovery else json.loads(Path(args.file).read_text(encoding='utf-8'))
        project_info.write(info)
        print(json.dumps(state(), ensure_ascii=False, indent=2))
        return 0
    if args.command == 'approve':
        info = project_info.load() or project_info.propose()
        stamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        project_info.write(project_info.stamp_approval(info, args.by, stamp))
        print(json.dumps(state(), ensure_ascii=False, indent=2))
        return 0
    report = state()
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report['usable'] else 2


if __name__ == '__main__':
    raise SystemExit(main())
