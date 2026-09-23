import hashlib, os, json, difflib, re

BASE = r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\tm108-v2-trial'
OUT = os.path.join(BASE, 'review', 'tools', 'out')
os.makedirs(OUT, exist_ok=True)

AFTER = os.path.join(BASE, 'review', 'copy', 'test.cpp')
BEFORE = os.path.join(BASE, 'implementation', 'backup', 'tm108-v2-impl__test.cpp.before')


def load(p):
    with open(p, 'rb') as f:
        b = f.read()
    txt = b.decode('utf-8-sig')
    raw = txt.split('\n')
    lines = [l[:-1] if l.endswith('\r') else l for l in raw]
    if lines and lines[-1] == '':
        lines = lines[:-1]
    return b, lines


ba, A = load(AFTER)
bb, B = load(BEFORE)

sm = difflib.SequenceMatcher(None, B, A, autojunk=False)
ops = sm.get_opcodes()
hunks = ['%s before[%d:%d] after[%d:%d]' % (t, i1, i2, j1, j2) for t, i1, i2, j1, j2 in ops if t != 'equal']
print('=== DIFF HUNKS (%d) ===' % len(hunks))
for h in hunks:
    print(' ', h)

added = 0
removed = 0
for t, i1, i2, j1, j2 in ops:
    if t == 'replace':
        removed += i2 - i1
        added += j2 - j1
    elif t == 'delete':
        removed += i2 - i1
    elif t == 'insert':
        added += j2 - j1
print('added lines:', added, 'removed lines:', removed, 'net:', added - removed)

# write the unified diff
diff = list(difflib.unified_diff(B, A, fromfile='BEFORE(plaintext, table)', tofile='AFTER(plaintext, reviewed)',
                                 lineterm='', n=4))
with open(os.path.join(OUT, 'full_diff.txt'), 'w', encoding='utf-8') as f:
    f.write('\n'.join(diff))
print('diff lines written:', len(diff))

# ---- comment classification of changed lines ----
def classify(line):
    s = line.strip()
    if s == '':
        return 'blank'
    if s.startswith('//') or s.startswith('/*') or s.startswith('*') or s.startswith('*/'):
        return 'comment'
    return 'CODE'

print()
print('=== CHANGED LINES CLASSIFICATION ===')
bad = []
for t, i1, i2, j1, j2 in ops:
    if t == 'equal':
        continue
    for idx in range(i1, i2):
        k = classify(B[idx])
        if k == 'CODE':
            bad.append(('DEL', idx + 1, B[idx]))
    for idx in range(j1, j2):
        k = classify(A[idx])
        if k == 'CODE':
            bad.append(('ADD', idx + 1, A[idx]))
if bad:
    print('!! NON-COMMENT CHANGED LINES: %d' % len(bad))
    for r in bad[:40]:
        print('  ', r)
else:
    print('OK: every changed (added/removed) line is a comment or blank line')

# ---- non-comment line sequence comparison (whole file) ----
def noncomment(lines):
    out = []
    for l in lines:
        s = l.strip()
        if s == '':
            continue
        if s.startswith('//') or s.startswith('/*') or s.startswith('*') or s.startswith('*/'):
            continue
        out.append(l)
    return out

na = noncomment(A)
nb = noncomment(B)
print()
print('non-comment lines before:', len(nb), 'after:', len(na), 'identical sequence:', na == nb)
if na != nb:
    for i, (x, y) in enumerate(zip(nb, na)):
        if x != y:
            print('first difference at non-comment index', i)
            print('  before:', repr(x))
            print('  after :', repr(y))
            break

# ---- brace-only / stripped scan: comments removed entirely ----
def strip_comments(text):
    # remove /* */ and // while respecting string literals
    out = []
    i = 0
    n = len(text)
    state = 'code'
    while i < n:
        c = text[i]
        if state == 'code':
            if c == '"':
                state = 'str'
                out.append(c)
            elif c == "'":
                state = 'chr'
                out.append(c)
            elif c == '/' and i + 1 < n and text[i + 1] == '/':
                state = 'line'
                i += 1
            elif c == '/' and i + 1 < n and text[i + 1] == '*':
                state = 'block'
                i += 1
            else:
                out.append(c)
        elif state == 'str':
            out.append(c)
            if c == '\\':
                i += 1
                if i < n:
                    out.append(text[i])
            elif c == '"':
                state = 'code'
        elif state == 'chr':
            out.append(c)
            if c == '\\':
                i += 1
                if i < n:
                    out.append(text[i])
            elif c == "'":
                state = 'code'
        elif state == 'line':
            if c == '\n':
                state = 'code'
                out.append(c)
        elif state == 'block':
            if c == '*' and i + 1 < n and text[i + 1] == '/':
                state = 'code'
                i += 1
        i += 1
    return ''.join(out)

ta = ba.decode('utf-8-sig')
tb = bb.decode('utf-8-sig')
ca = strip_comments(ta)
cb = strip_comments(tb)
ca_n = re.sub(r'[ \t\r\n]+', ' ', ca).strip()
cb_n = re.sub(r'[ \t\r\n]+', ' ', cb).strip()
print()
print('comment-stripped, whitespace-normalised text identical:', ca_n == cb_n)
print('  stripped len before/after:', len(cb_n), len(ca_n))
print('  stripped sha256 before:', hashlib.sha256(cb_n.encode()).hexdigest())
print('  stripped sha256 after :', hashlib.sha256(ca_n.encode()).hexdigest())

json.dump({'hunks': hunks, 'added': added, 'removed': removed,
           'commentOnly': len(bad) == 0,
           'nonCommentBefore': len(nb), 'nonCommentAfter': len(na),
           'nonCommentIdentical': na == nb,
           'strippedIdentical': ca_n == cb_n},
          open(os.path.join(OUT, 'diff_summary.json'), 'w', encoding='utf-8'), indent=2)
