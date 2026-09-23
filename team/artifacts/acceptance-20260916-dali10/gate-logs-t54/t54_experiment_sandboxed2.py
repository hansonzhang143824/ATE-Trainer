# -*- coding: utf-8 -*-
"""机制化 (a) 补全：还需**输入**重定向（`--in <path>`）——
"隔离输出"之后，生成器若仍**读** canonical 活路径，实验就测不到注入的探针（本轮实测：注入 0 条生效）。
⇒ 完整机制化 = **`--in` + `--out` 双重重定向**；随后重跑实验并跑后断言。
"""
import ast
import hashlib
import io
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
T28 = os.path.abspath(os.path.join(HERE, '..', 'gate-logs-t28'))
LIVE = os.path.join(T28, 't28-anchors.json')
GEN = os.path.join(T28, 't28_make_anchors.py')


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


print('=== 补输入重定向 --in ===')
src = io.open(GEN, encoding='utf-8-sig').read()
ast.parse(src)
OLD = "if os.path.isfile(out):"          # 读回现盘的判断处
NEW = ("_inp = out\n"
       "if '--in' in sys.argv:\n"
       "    _j = sys.argv.index('--in')\n"
       "    if _j + 1 < len(sys.argv):\n"
       "        _inp = sys.argv[_j + 1]\n"
       "        print('[in-redirect] 读取目标 = %s' % _inp)\n"
       "if os.path.isfile(_inp):")
if "'--in' in sys.argv" in src:
    print('  已含 --in（幂等）')
elif OLD in src:
    out_src = src.replace(OLD, NEW, 1)
    # 同时把其内部读该文件的语句也换成 _inp
    out_src = out_src.replace("prev = json.loads(io.open(out, encoding='utf-8-sig').read())",
                              "prev = json.loads(io.open(_inp, encoding='utf-8-sig').read())")
    ast.parse(out_src)
    io.open(GEN, 'w', encoding='utf-8', newline='').write(out_src)
    print('  已加入 --in → %d B' % os.path.getsize(GEN))
else:
    print('  WARN: 锚点未命中')
    sys.exit(1)
ast.parse(io.open(GEN, encoding='utf-8-sig').read())
print('  语法 OK')

print('\n=== 重跑实验（--in 副本 + --out 沙箱 + 跑后断言）===')
live_before = sha(LIVE)
inp = LIVE + '.sbx-in'
outp = LIVE + '.sbx-out'
open(inp, 'wb').write(open(LIVE, 'rb').read())
A = json.loads(open(inp, 'rb').read().decode('utf-8-sig'))
A.setdefault('preservedPeerNamespaces', {})['qaProbeAnchors'] = {
    'anchors': {k: {'sentinel': True} for k in ('SANDBOX-1.json', 'SANDBOX-2.json', 'SANDBOX-3.json')}}
open(inp, 'w', encoding='utf-8').write(json.dumps(A, ensure_ascii=False, indent=2))
print('  输入副本注入 3 条（第三方前缀 qaProbeAnchors）')

r = subprocess.run([sys.executable, GEN, '--in', inp, '--out', outp],
                   capture_output=True, text=True, encoding='utf-8')
print('  exit=%d' % r.returncode)
for l in (r.stdout or '').strip().splitlines()[:3]:
    print('    ' + l.strip())
B = json.loads(open(outp, 'rb').read().decode('utf-8-sig'))
pp = B.get('preservedPeerNamespaces') or {}
n = len((pp.get('qaProbeAnchors') or {}).get('anchors') or {})
print('  qaProbeAnchors.anchors = %d 条（应 3）⇒ 3 条全在 = %s' % (n, n == 3))
print('  setupArchitectFreezeAnchors 在 =', bool(pp.get('setupArchitectFreezeAnchors')))
print('  输出只写沙箱：%s 存在=%s；canonical 未收到输出 = %s'
      % (os.path.basename(outp), os.path.isfile(outp), sha(LIVE) == live_before))

for p in (inp, outp):
    if os.path.isfile(p):
        os.remove(p)
live_after = sha(LIVE)
print('\n=== 跑后断言（固定动作）===')
assert live_after == live_before, '活档被改变！'
print('  assert 通过：活档 sha 前后一致（%s）✓' % live_after[:24])
