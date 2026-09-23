import io
p = 'team/artifacts/acceptance-20260916-dali10/gate-logs-t54/t54_make_report.py'
t = io.open(p, encoding='utf-8-sig').read()
i = t.find('_rec = {')
seg = t[i:i + 4000]
# 打印顶层键名（缩进 4 的 'key':）
import re
keys = re.findall(r"^    '([A-Za-z][A-Za-z0-9_]*)':", seg, flags=re.M)
print('  _rec 顶层键 =', keys)
print()
for k in ('lastAppendDecision', 'appendPolicyBoundary', 'countUnitNote', 'appendPolicy', 'prePolicyCountsAtPolicyWrite'):
    print('  含 %-30s %s' % (k, k in seg))
print()
j = seg.find('appendPolicy')
print('  appendPolicy 段上下文：')
print(seg[max(0, j - 300):j + 900])
