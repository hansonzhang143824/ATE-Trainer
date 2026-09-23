import hashlib
import io
import json
import os
import re

RUN = 'team/artifacts/acceptance-20260916-dali10'
P = os.path.join(RUN, 'build-report.json')
b = open(P, 'rb').read()
J = json.loads(b.decode('utf-8-sig'))
GEN = r'^\s*"generatedAt": ".*?",\s*$'


def ser(j, ex):
    d = {k: v for k, v in j.items() if k not in ex}
    return hashlib.sha256(json.dumps(d, ensure_ascii=False, sort_keys=True).encode('utf-8')).hexdigest()


def byl(bb):
    return hashlib.sha256(re.sub(GEN, '', bb.decode('utf-8-sig'), flags=re.M).strip().encode('utf-8')).hexdigest()


print('KEY  report top-level has:', [k for k in J if k in ('projectionSpec', 'receipts', 'hashInvariance', 'generatedAt')])
print('A: exclude={generatedAt}          sort_keys =', ser(J, {'generatedAt'})[:20])
print('B: exclude={generatedAt,receipts} sort_keys =', ser(J, {'generatedAt', 'receipts'})[:20], '<- v2 now')
print('C: line-strip generatedAt (old v1)        =', byl(b)[:20])
print('A==B ?', ser(J, {'generatedAt'}) == ser(J, {'generatedAt', 'receipts'}), '=> receipts exclusion is NO-OP')
print('C==A ?', byl(b) == ser(J, {'generatedAt'}), '=> serialization differs => THAT is the v1->v2 change')
