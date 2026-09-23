import os,re
SRC=r'D:\PROJECT6-DALI\ForCodexDebug\source'
def L(p):
    t=open(p,'rb').read().decode('utf-8-sig',errors='replace')
    x=t.split('\n'); return [y[:-1] if y.endswith('\r') else y for y in x]
tl=L(os.path.join(SRC,'treg.cpp'))
out=[]
# definitions of TREG_ERROR::treg_error_log / error / register_error_func
for i,l in enumerate(tl):
    if re.search(r'(int|void)\s+TREG_ERROR::(treg_error_log|error|vprintf_s|register_error_func)', l):
        out.append('=== definition at treg.cpp:%d ===' % (i+1))
        for n in range(i+1, min(len(tl)+1, i+40)):
            out.append('  %5d| %s' % (n, tl[n-1].rstrip()))
        out.append('')
# where does treg_error_log write to? look for file handles / globals near error_func
for i,l in enumerate(tl):
    if re.search(r'error_func\s*=|error_count|ERROR_LOG|error_log|fopen|msLogData|SetTestNumber', l) and i < 400:
        out.append('  %5d| %s' % (i+1, l.rstrip()))
open(r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\tm108-v2-trial\review\tools\out\errlog.txt','w',encoding='utf-8').write('\n'.join(out))
print('\n'.join(x for x in out if all(ord(c)<128 for c in x))[:9000])
