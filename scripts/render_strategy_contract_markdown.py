import hashlib
import json
import sys
from pathlib import Path


def md_escape(v):
    return str(v).replace('|', '\\|').replace('\n', '<br>')


def h(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    if len(sys.argv) != 2:
        raise SystemExit('usage: render_strategy_contract_markdown.py <contract.json>')
    p = Path(sys.argv[1]).resolve()
    d = json.loads(p.read_text(encoding='utf-8'))
    lines = [
        f'# {d["tm"]} Resource and Configuration Contract', '',
        f'- Revision: {d.get("revision", {}).get("number", 1)}',
        f'- Role: {d["role"]}',
        f'- Verdict: `{d["verdict"]}`',
        f'- JSON SHA-256: `{h(p)}`', '',
        '## Classification', '',
        '| Field | Value |', '| --- | --- |',
    ]
    for key in ('projectType', 'parameterType', 'functionArchitecture'):
        x=d['classification'][key]
        lines.append(f'| {key} | {md_escape(x.get("value", ""))} |')
    lines += ['', '## Source allocation and routes', '', '| Endpoint | Source table | Channel | Route | Actuated relays |', '| --- | --- | --- | --- | --- |']
    for x in d['resourceAllocation']:
        source=f'{x.get("sourceTable","?")} {x.get("slot","")} ch{x.get("channel","")}'
        relays=', '.join('K'+str(n) for n in x.get('requiredActuations', [])) or 'none'
        lines.append(f'| {x["dutPin"]} | {md_escape(source)} | {md_escape(", ".join(x.get("ports", [])))} | {md_escape(x.get("selectedPath", "UNRESOLVED"))} | {relays} |')
    lines += ['', '## Relay groups', '']
    for g in d['relayGroups']:
        lines += [f'### {g["groupId"]}: {g["endpointId"]}', '', f'- Purpose: {g.get("purpose", "")}', f'- Path relays: {md_escape(json.dumps(g.get("pathRelays", []), ensure_ascii=False))}', f'- Isolation: {md_escape("; ".join(g.get("isolationRequirements", [])))}', '']
    lines += ['## Register delta', '', '| Order | Call | Details |', '| --- | --- | --- |']
    for x in d['registerDelta']:
        details='; '.join(f'{k}={v}' for k,v in x.items() if k not in ('order','call','source'))
        lines.append(f'| {x.get("order", "rule")} | {x.get("call", "rule")} | {md_escape(details)} |')
    lines += ['', '## Handoff to test method', '']
    for x in d['handoff']['usableBoundaries']:
        lines.append(f'- {x}')
    if d['openItems']:
        lines += ['', '## Open items (non-blocking unless stated)', '']
        for x in d['openItems']:
            lines.append(f'- `{x.get("id")}`: {x.get("description", x.get("topic", ""))}')
    lines += ['', '## Evidence', '']
    for x in d['evidence']:
        lines.append(f'- `{x.get("file", "")}` — {x.get("locator", "")}')
    out=p.with_suffix('.md')
    out.write_text('\n'.join(lines)+'\n', encoding='utf-8')
    print(f'PASS {out} {h(out)}')

if __name__ == '__main__':
    main()
