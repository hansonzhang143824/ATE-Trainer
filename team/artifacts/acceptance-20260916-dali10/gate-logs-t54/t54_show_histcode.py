import io
p = 'team/artifacts/acceptance-20260916-dali10/gate-logs-t54/t54_make_report.py'
t = io.open(p, encoding='utf-8-sig').read().splitlines()
idx = [n for n, l in enumerate(t) if ('_hist_p' in l) or ('_known_bodies' in l) or ("_f.write" in l)]
lo = max(0, min(idx) - 3)
hi = min(len(t), max(idx) + 12)
for k in range(lo, hi):
    print('%4d| %s' % (k + 1, t[k][:120]))
