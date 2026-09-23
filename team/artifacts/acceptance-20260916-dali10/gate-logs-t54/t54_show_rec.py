import io
p = 'team/artifacts/acceptance-20260916-dali10/gate-logs-t54/t54_make_report.py'
t = io.open(p, encoding='utf-8-sig').read()
i = t.find('_rec = {')
print('  _rec 段位置 =', i)
print(t[i:i + 1500])
