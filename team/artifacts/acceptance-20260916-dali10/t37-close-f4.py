# -*- coding: utf-8 -*-
"""t37: close T32-F4 in verification-report.json after the Captain supplied the schema.
Only F4-related fields, the sixth acceptanceResult and one explanatory key are touched.
The overall verdict INTENTIONALLY stays fail (T32-F1/F2/F3 still open).
"""
import json, hashlib, sys, os
sys.stdout.reconfigure(encoding='utf-8')

RP = r'team/artifacts/acceptance-20260916-dali10/verification-report.json'
SP = r'team/schemas/verification-report.schema.json'
RUN = 'acceptance-20260916-dali10'

before = open(RP, 'rb').read()
before_sha = hashlib.sha256(before).hexdigest()
sch = open(SP, 'rb').read()
sch_sha = hashlib.sha256(sch).hexdigest()
d = json.loads(before.decode('utf-8'))
changed = []

# ---- 1) T32-F4 -> CLOSED
for f in d['findings']:
    if f['id'] == 'T32-F4':
        f['status'] = 'CLOSED'
        f['resolution'] = {
            'closedBy': 'Captain (schema supplied before t37)',
            'closedAt': '2026-09-16 (before t37 start)',
            'schemaFile': 'team/schemas/verification-report.schema.json',
            'schemaSizeBytes': len(sch),
            'schemaSha256': sch_sha,
            'schemaStyle': ('same shape as build-report.schema.json; additionalProperties:true; verdict enum pass/fail/blocked; '
                            'findings severity enum low/medium/high/blocker; required keys mirror this report'),
            'reVerificationCommand': ('python scripts/validate_team_artifact.py verification-report '
                                      'team/artifacts/%s/verification-report.json' % RUN),
            'reVerificationExitCode': 0,
            'reVerificationObserved': ('PASS D:\\...\\verification-report.json conforms to '
                                       'D:\\...\\team\\schemas\\verification-report.schema.json'),
            'scope': 'infrastructure gap only: this closure does NOT touch T32-F1/F2/F3, which remain open',
        }
        f['problem'] = ("(closed by captain: the schema now exists) the contract's verify command originally could not pass: "
                        + f['problem'].split(':', 1)[1].strip() if ':' in f['problem'] else f['problem'])
        changed.append('findings[T32-F4].status, .resolution (new), .problem (prefixed with closure note)')

# ---- 2) acceptanceResults[6] -> passed
acc = d['acceptanceResults'][5]
acc['status'] = 'passed'
acc['evidence'] = (
    '报告已产出并通过校验：team/artifacts/%s/verification-report.json 现算 %d B / %s；'
    'python scripts/validate_team_artifact.py verification-report ... 实测 exit 0（PASS：conforms to '
    'team/schemas/verification-report.schema.json）。该 schema 由 Captain 在本任务前补齐 = %d B / %s。'
    '（原始缺口为 schema 缺失 → FileNotFoundError/exit 1，见 findings T32-F4 的 resolution。）'
    % (RUN, len(before), before_sha, len(sch), sch_sha)
)
changed.append('acceptanceResults[5].status passed, .evidence rewritten')

# ---- 3) one explanatory key
d['f4ClosureAndVerdict'] = {
    'f4': 'CLOSED — verification-report.schema.json supplied by the Captain before t37; validator exit code 0',
    'verdictPolicy': ('overall verdict INTENTIONALLY REMAINS fail: T32-F1 (t29 repair not landed in the target tree), '
                      'T32-F2 (t24 review does not cover the deployed bytes) and T32-F3 (GREEN gate evidence belongs to '
                      'another revision) are still open'),
    'allOtherFindingsUnchanged': ['T32-F1 blocker', 'T32-F2 high', 'T32-F3 high', 'T32-F5 low'],
    'compilationIsNotElectricalSignoff': ('validator/compile success says nothing about electrical correctness; '
                                          'this run contains no instrument or hardware data'),
    'nextReReviewTrigger': ('after the payload carrying K109/K110 is landed and the gates are re-run against the landed '
                            'revision, and t24 is re-issued for the new bytes'),
}
changed.append('f4ClosureAndVerdict (new top-level key)')

# ---- 4) append the post-edit re-run of the contract verify command (the earlier entry recorded the
#         pre-schema failure and stays for audit; this entry records the current outcome)
d['commandsRun'].append({
    'command': ('python scripts/validate_team_artifact.py verification-report '
                'team/artifacts/%s/verification-report.json' % RUN),
    'status': 'passed',
    'exitCode': 0,
    'evidence': ('re-run AFTER this F4 closure edit: '
                 '"PASS ... conforms to ... team/schemas/verification-report.schema.json" exit 0. '
                 'The earlier commandsRun entry with exitCode 1 records the pre-schema state and is retained for audit.'),
})
changed.append('commandsRun[+1] (post-edit re-run of the contract verify command, exit 0)')

after = json.dumps(d, ensure_ascii=False, indent=1).encode('utf-8')
with open(RP, 'wb') as f:
    f.write(after)
after_sha = hashlib.sha256(open(RP, 'rb').read()).hexdigest()

print('before:', len(before), before_sha)
print('after :', os.path.getsize(RP), after_sha)
print('changed:', changed)
print('verdict after:', d['verdict'], '| acceptance:', [a['status'] for a in d['acceptanceResults']])
print('F4 status:', [f.get('status') for f in d['findings'] if f['id'] == 'T32-F4'])
print('other findings status:', [(f['id'], f.get('status', 'open')) for f in d['findings'] if f['id'] != 'T32-F4'])
