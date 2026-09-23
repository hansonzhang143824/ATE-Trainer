# t11 diff analyser - python byte mode reads only.
import difflib, hashlib, re

LIVE = r"D:\PROJECT6-DALI\ForCodexDebug\source\test.cpp"
BEFORE = r"D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\tm108-v2-trial\implementation\backup\tm108-v2-impl__test.cpp.before"


def lines(p):
    txt = open(p, 'rb').read().decode('utf-8-sig')
    out = txt.split('\n')
    if out and out[-1] == '':
        out = out[:-1]
    return [x.rstrip('\r') for x in out]


A = lines(BEFORE)
B = lines(LIVE)
print("before lines %d   live lines %d" % (len(A), len(B)))

sm = difflib.SequenceMatcher(None, A, B, autojunk=False)
ops = [o for o in sm.get_opcodes() if o[0] != 'equal']
added = sum(o[4] - o[3] for o in ops)
removed = sum(o[2] - o[1] for o in ops)
print("opcodes(non-equal) %d   added %d   removed %d   net %d" % (len(ops), added, removed, added - removed))
print("")
print("raw change blocks (before-line range -> live-line range, 1-based inclusive):")
for tag, i1, i2, j1, j2 in ops:
    print("   %-8s before %d..%d  live %d..%d" % (tag, i1 + 1, i2, j1 + 1, j2))
bmin = min(o[1] for o in ops) + 1
bmax = max(o[2] for o in ops)
lmin = min(o[3] for o in ops) + 1
lmax = max(o[4] for o in ops)
print("")
print("changed range: before %d..%d    live %d..%d" % (bmin, bmax, lmin, lmax))

# unified hunks at context 3
print("")
print("unified_diff n=3 hunk headers:")
for ln in difflib.unified_diff(A, B, n=3, lineterm=''):
    if ln.startswith('@@'):
        print("   " + ln)

# non-comment sequence
def nc(arr):
    out = []
    for s in arr:
        t = s.strip()
        if t == '' or t.startswith('//') or t.startswith('/*') or t.startswith('*') or t.startswith('*/'):
            continue
        out.append(s)
    return out

na, nb = nc(A), nc(B)
print("")
print("non-comment: before %d  live %d  identical-shape %s  identical %s" % (len(na), len(nb), len(na) == len(nb), na == nb))

# comment-stripped normalised whole-file equality (reviewer's stronger check)
def strip_comments(txt):
    out = []
    i = 0
    n = len(txt)
    while i < n:
        c = txt[i]
        if c == '"' or c == "'":
            q = c
            out.append(c); i += 1
            while i < n:
                if txt[i] == '\\':
                    out.append(txt[i]); i += 1
                    if i < n:
                        out.append(txt[i]); i += 1
                    continue
                out.append(txt[i])
                if txt[i] == q:
                    i += 1
                    break
                i += 1
            continue
        if c == '/' and i + 1 < n and txt[i + 1] == '/':
            while i < n and txt[i] != '\n':
                i += 1
            continue
        if c == '/' and i + 1 < n and txt[i + 1] == '*':
            i += 2
            while i + 1 < n and not (txt[i] == '*' and txt[i + 1] == '/'):
                i += 1
            i += 2
            continue
        out.append(c); i += 1
    return ''.join(out)


raw_a = open(BEFORE, 'rb').read().decode('utf-8-sig')
raw_b = open(LIVE, 'rb').read().decode('utf-8-sig')
sa = ' '.join(strip_comments(raw_a).split())
sb = ' '.join(strip_comments(raw_b).split())
print("")
print("comment-stripped normalised: before len %d sha %s" % (len(sa), hashlib.sha256(sa.encode()).hexdigest()))
print("comment-stripped normalised: live   len %d sha %s" % (len(sb), hashlib.sha256(sb.encode()).hexdigest()))
print("byte-identical: %s" % (sa == sb))
