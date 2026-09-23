# -*- coding: utf-8 -*-
"""t37 step 2: append the post-edit re-run of the contract verify command to commandsRun.
Idempotent: replaces any prior 'post-edit re-run' entry instead of stacking duplicates.
"""
import json, hashlib, sys, os
sys.stdout.reconfigure(encoding='utf-8')

RP = r'team/artifacts/acceptance-20260916-dali10/verification-report.json'
RUN = 'acceptance-20260916-dali10'
MARK = 're-run AFTER this F4 closure edit'

before = open(RP, 'rb').read()
b_sha = hashlib.sha256(before).hexdigest()
b_size = len(before)
d = json.loads(before.decode('utf-8'))

d['commandsRun'] = [c for c in d['commandsRun'] if MARK not in (c.get('evidence') or '')]
d['commandsRun'].append({
    'command': ('python scripts/validate_team_artifact.py verification-report '
                'team/artifacts/%s/verification-report.json' % RUN),
    'status': 'passed',
    'exitCode': 0,
    'evidence': ('re-run AFTER this F4 closure edit: "PASS ... conforms to ... '
                 'team/schemas/verification-report.schema.json" exit 0. The earlier commandsRun entry with exitCode 1 '
                 'records the pre-schema state and is retained for audit.'),
})

after = json.dumps(d, ensure_ascii=False, indent=1).encode('utf-8')
with open(RP, 'wb') as f:
    f.write(after)
a_sha = hashlib.sha256(open(RP, 'rb').read()).hexdigest()
print('before:', b_size, b_sha)
print('after :', os.path.getsize(RP), a_sha)
print('commandsRun:', [(c['status'], c['exitCode']) for c in d['commandsRun']])
print('verdict:', d['verdict'], '| F4:', [f.get('status') for f in d['findings'] if f['id'] == 'T32-F4'],
      '| acceptance:', [a['status'] for a in d['acceptanceResults']])
