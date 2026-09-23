# t11 analyser - DLP discipline: every read of the target uses python byte mode only.
# Reader for all target values below: python open(p,'rb'); kind: plaintext.
import hashlib, re, sys, io

LIVE = r"D:\PROJECT6-DALI\ForCodexDebug\source\test.cpp"
BEFORE = r"D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\tm108-v2-trial\implementation\backup\tm108-v2-impl__test.cpp.before"


def load(p):
    b = open(p, 'rb').read()
    txt = b.decode('utf-8-sig')
    return b, txt


def props(name, b):
    crlf = b.count(b'\r\n')
    lf = b.count(b'\n')
    print("== %s" % name)
    print("   sha256   %s" % hashlib.sha256(b).hexdigest())
    print("   size     %d   bom %s   crlf %d   bare_lf %d   total_lf %d"
          % (len(b), b[:3] == b'\xef\xbb\xbf', crlf, lf - crlf, lf))


def nl_lines(txt):
    """display-line convention: split on LF (== the reviewer's 'lines' count)."""
    parts = txt.split('\n')
    if parts and parts[-1] == '':
        parts = parts[:-1]
    return parts


def line_is_comment(s):
    t = s.strip()
    if t == '':
        return True
    return t.startswith('//') or t.startswith('/*') or t.startswith('*') or t.startswith('*/')


def noncomment(lines):
    return [ln.rstrip('\r') for ln in lines if not line_is_comment(ln)]


def find_bare_lf(b):
    """line numbers (LF convention) of lines terminated by a bare LF."""
    out = []
    idx = 0
    n = 1
    while True:
        j = b.find(b'\n', idx)
        if j < 0:
            break
        if j == 0 or b[j - 1] != 0x0D:
            out.append(n)
        n += 1
        idx = j + 1
    return out


lb, lt = load(LIVE)
bb, bt = load(BEFORE)
props("LIVE " + LIVE, lb)
props("BEFORE " + BEFORE, bb)

L = nl_lines(lt)
B = nl_lines(bt)

print("")
print("== line counts (LF convention)")
print("   live   lines %d   (split items %d)" % (len(L), len(lt.split('\n'))))
print("   before lines %d" % len(B))
print("   live bare-LF line numbers  : %s" % find_bare_lf(lb))
print("   before bare-LF line numbers: %s" % find_bare_lf(bb))

print("")
print("== RF-04 item 1: TM108 signature line")
sig = 'DUT_API int TM108_HSKP_VAC1_PRST(short funcindex, LPCTSTR funclabel)'
for nm, arr in (("live", L), ("before", B)):
    hits = [i + 1 for i, ln in enumerate(arr) if ln.rstrip('\r') == sig]
    print("   %-6s exact-signature lines: %s" % (nm, hits))
    sub = [i + 1 for i, ln in enumerate(arr) if 'TM108_HSKP_VAC1_PRST' in ln]
    print("   %-6s TM108_HSKP_VAC1_PRST occurrences: %s" % (nm, sub))

print("")
print("== RF-04 item 2: non-comment line counts")
nl = noncomment(L)
nb = noncomment(B)
print("   live   non-comment lines: %d" % len(nl))
print("   before non-comment lines: %d" % len(nb))
print("   sequences identical      : %s" % (nl == nb))

print("")
print("== RF-04 item 3: DUT_API TM symbol counts")
for nm, arr, txt in (("live", L, lt), ("before", B, bt)):
    c1 = len(re.findall(r'DUT_API\s+int\s+TM\d+', txt))
    c2 = len(re.findall(r'DUT_API\s+int\s+TM\d+\w*\s*\(', txt))
    c3 = len([x for x in arr if re.match(r'\s*DUT_API\s+int\s+TM\d+', x)])
    c4 = len(re.findall(r'DUT_API\s+int\s+TM\w+\s*\(', txt))
    print("   %-6s DUT_API\\s+int\\s+TM\\d+ = %d | +word*( = %d | line-anchored = %d | TM\\w+( = %d"
          % (nm, c1, c2, c3, c4))

print("")
print("== TM108 span and step headings")
# locate the live TM108 function span
s = next(i for i, ln in enumerate(L) if ln.rstrip('\r') == sig)
# closing brace: first line that is exactly '}' at col 0 after signature
e = next(i for i in range(s + 1, len(L)) if L[i].rstrip('\r') == '}')
print("   live   signature line %d, closing brace line %d, span %d-%d" % (s + 1, e + 1, s + 1, e + 1))
sb = next(i for i, ln in enumerate(B) if ln.rstrip('\r') == sig)
eb = next(i for i in range(sb + 1, len(B)) if B[i].rstrip('\r') == '}')
print("   before signature line %d, closing brace line %d, span %d-%d" % (sb + 1, eb + 1, sb + 1, eb + 1))

for nm, arr, a, b_ in (("live", L, s, e), ("before", B, sb, eb)):
    print("   -- %s TM108 step/heading tokens:" % nm)
    for i in range(max(0, a - 90), b_ + 1):
        ln = arr[i].rstrip('\r')
        if re.search(r'Step\s*\d|======', ln):
            print("      %5d  %s" % (i + 1, ln))

print("")
print("== sibling Step 4 headings (whole file, live)")
for i, ln in enumerate(L):
    ln2 = ln.rstrip('\r')
    if 'Step 4' in ln2:
        print("      %5d  %s" % (i + 1, ln2))

print("")
print("== TM107 / TM109 headings (live)")
for i, ln in enumerate(L):
    ln2 = ln.rstrip('\r')
    if ln2.startswith('// TM107') or ln2.startswith('// TM109') or ln2.startswith('DUT_API int TM107') or ln2.startswith('DUT_API int TM109'):
        print("      %5d  %s" % (i + 1, ln2))

print("")
print("== count of '======' banner lines in live file: %d" % len([x for x in L if '======' in x]))
