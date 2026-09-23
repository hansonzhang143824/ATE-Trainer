# t11 edit script - RF-02 / RF-03 comment-only fixes.
# DLP discipline: target read AND write via python byte mode only, preserving UTF-8 BOM and CRLF.
# Usage:  python _t11_edit_test.py            -> dry run (no write)
#         python _t11_edit_test.py --write    -> in-place write of source/test.cpp
import hashlib, re, sys, difflib

LIVE = r"D:\PROJECT6-DALI\ForCodexDebug\source\test.cpp"
WRITE = '--write' in sys.argv

# ---------------------------------------------------------------- expected pre-state
EXPECT_SHA = "b79b911a65a33abd62697f8576bd04b5022194751c9bfc5b174ecdab96d05d5a"
EXPECT_SIZE = 477123
EXPECT_LINES = 9437
EXPECT_CRLF = 9434
EXPECT_BARELF = 3
EXPECT_SIG = 2193
EXPECT_SPAN = (2193, 2309)

old_b = open(LIVE, 'rb').read()
assert hashlib.sha256(old_b).hexdigest() == EXPECT_SHA, "pre-state sha256 mismatch - refusing to edit"
assert len(old_b) == EXPECT_SIZE
assert old_b[:3] == b'\xef\xbb\xbf'
old_txt = old_b.decode('utf-8-sig')
OLD = old_txt.split('\n')
assert OLD[-1] == ''
OLD = OLD[:-1]
assert len(OLD) == EXPECT_LINES, len(OLD)
assert OLD[EXPECT_SIG - 1].rstrip('\r') == 'DUT_API int TM108_HSKP_VAC1_PRST(short funcindex, LPCTSTR funclabel)'
assert OLD[EXPECT_SPAN[1] - 1].rstrip('\r') == '}'


def L(n):
    return OLD[n - 1].rstrip('\r')


# ---------------------------------------------------------------- edits, descending order
# (start_line, number_of_old_lines, [new lines without CR])
EDITS = []

# --- RF-02 site B : display 2287-2289 -> 5 lines (+2)
b_old = [L(2287), L(2288), L(2289)]
assert b_old == [
    '    // {13,65} need no explicit release call: the cbite scope ends with the function, so no relay',
    '    // of this item outlives it. P8 therefore ends with every source off, no rail charged, every',
    '    // keep-open relay still un-actuated and nothing written to the DUT.',
], b_old
b_new = [
    '    // {13,65} need no explicit release call IF the framework resets the relays of an item when its',
    "    // cbite scope ends with the function. That behaviour is ASSUMED here and NOT verified in this",
    "    // run - confirming it is compile-diagnostician's item. P8 therefore ends with every source off,",
    '    // no rail charged, every keep-open relay still un-actuated and nothing written to the DUT, but',
    '    // the release of the closure is itself unconfirmed until that reset is confirmed.',
]
EDITS.append((2287, 3, b_new))

# --- RF-03 : insert a Step 4 heading before display 2240 (0 old lines, +4)
assert L(2240) == '    // P4 rising sweep -> P5 turn-around -> P6 falling sweep (method sec.3 P4/P5/P6)', L(2240)
assert L(2239) == '', repr(L(2239))
assert L(2238) == '    I2CWriteSameData(DEV_ADDR, 0x57, 0x08);'
c_new = [
    '    // ====== Step 4: Measure (library AWG ramp, capture on the observation candidate) ======',
    "    // Heading note: the sibling items' Step 4 line reads \"trigger-capture DTEST0 toggle\". That",
    '    // wording is deliberately NOT reused here, because TM108 does not equate V(DTEST0) with the',
    '    // observation candidate (OI-T4-01 open, RA-5 CANDIDATE ONLY). The step scheme stays 1..6.',
]
EDITS.append((2240, 0, c_new))

# --- RF-02 site A : display 2178-2179 -> 2 lines (same count, no line shift)
a_old = [L(2178), L(2179)]
assert a_old == [
    '//   safety end : the closure set is released implicitly with the cbite scope; no relay of this',
    '//                item is left actuated and no source is left energised',
], a_old
a_new = [
    '//   safety end : no relay of this item is left actuated and no source energised ONLY IF the cbite',
    "//                scope resets the closure - ASSUMED, NOT verified (compile-diagnostician's item).",
]
EDITS.append((2178, 2, a_new))

for start, cnt, new in EDITS:
    for ln, s in enumerate(new, 1):
        assert len(s) <= 100, "new line too wide (%d): %r" % (len(s), s)
    print("EDIT at %d (%d old -> %d new)" % (start, cnt, len(new)))
    for s in new:
        print("      %3d  %s" % (len(s), s))

# apply descending
NEW = list(OLD)
for start, cnt, new in sorted(EDITS, key=lambda e: -e[0]):
    i = start - 1
    assert NEW[i:i + cnt] == OLD[i:i + cnt]
    NEW[i:i + cnt] = [x + '\r' for x in new]

# ---------------------------------------------------------------- invariants
new_txt = '\n'.join(NEW) + '\n'   # '\r' survived inside each element; restore the final LF
assert '\n'.join(OLD) + '\n' == old_txt, "reconstruction is not lossless"
new_b = b'\xef\xbb\xbf' + new_txt.encode('utf-8')

print("")
print("== byte-level")
print("   old sha %s size %d lines %d" % (hashlib.sha256(old_b).hexdigest(), len(old_b), len(OLD)))
print("   new sha %s size %d lines %d" % (hashlib.sha256(new_b).hexdigest(), len(new_b), len(NEW)))
print("   line delta %+d   size delta %+d" % (len(NEW) - len(OLD), len(new_b) - len(old_b)))
crlf = new_b.count(b'\r\n'); lf = new_b.count(b'\n')
print("   BOM %s  CRLF %d (old %d)  bare LF %d (old %d)"
      % (new_b[:3] == b'\xef\xbb\xbf', crlf, EXPECT_CRLF, lf - crlf, EXPECT_BARELF))
assert new_b[:3] == b'\xef\xbb\xbf'
assert lf - crlf == EXPECT_BARELF


def nc(arr):
    out = []
    for s in arr:
        t = s.strip()
        if t == '' or t.startswith('//') or t.startswith('/*') or t.startswith('*') or t.startswith('*/'):
            continue
        out.append(s)
    return out


na, nb = nc(OLD), nc(NEW)
print("")
print("== executable content")
print("   non-comment lines: old %d  new %d  sequence byte-identical: %s" % (len(na), len(nb), na == nb))
assert len(na) == len(nb) and na == nb, "NON-COMMENT SEQUENCE CHANGED - aborting"

print("")
print("== signature / symbol counts")
sig = 'DUT_API int TM108_HSKP_VAC1_PRST(short funcindex, LPCTSTR funclabel)'
print("   signature lines old %s new %s"
      % ([i + 1 for i, x in enumerate(OLD) if x.rstrip('\r') == sig],
         [i + 1 for i, x in enumerate(NEW) if x.rstrip('\r') == sig]))
assert [i + 1 for i, x in enumerate(NEW) if x.rstrip('\r') == sig] == [EXPECT_SIG]
print("   'TM108_HSKP_VAC1_PRST' occurrences old %d new %d"
      % (len([x for x in OLD if 'TM108_HSKP_VAC1_PRST' in x]), len([x for x in NEW if 'TM108_HSKP_VAC1_PRST' in x])))
ot = '\n'.join(OLD); nt = '\n'.join(NEW)
print("   DUT_API int TM<n> declarations old %d new %d"
      % (len(re.findall(r'DUT_API\s+int\s+TM\d+', ot)), len(re.findall(r'DUT_API\s+int\s+TM\d+', nt))))
print("   DUT_API int <anything> declarations old %d new %d"
      % (len(re.findall(r'DUT_API\s+int\s+\w+', ot)), len(re.findall(r'DUT_API\s+int\s+\w+', nt))))
assert len(re.findall(r'DUT_API\s+int\s+TM\d+', ot)) == len(re.findall(r'DUT_API\s+int\s+TM\d+', nt)) == 98

print("")
print("== new TM108 span / step headings")
s = next(i for i, x in enumerate(NEW) if x.rstrip('\r') == sig)
e = next(i for i in range(s + 1, len(NEW)) if NEW[i].rstrip('\r') == '}')
print("   signature %d  closing brace %d  span %d-%d" % (s + 1, e + 1, s + 1, e + 1))
for i in range(s - 2, e + 1):
    x = NEW[i].rstrip('\r')
    if re.search(r'Step\s*\d', x):
        print("      %5d  %s" % (i + 1, x))

print("")
print("== scope confinement")
sm = difflib.SequenceMatcher(None, OLD, NEW, autojunk=False)
ops = [o for o in sm.get_opcodes() if o[0] != 'equal']
print("   raw change blocks %d   added %d   removed %d" % (
    len(ops),
    sum(o[4] - o[3] for o in ops),
    sum(o[2] - o[1] for o in ops)))
o_min = min(o[1] for o in ops) + 1; o_max = max(o[2] for o in ops)
n_min = min(o[3] for o in ops) + 1; n_max = max(o[4] for o in ops)
print("   changed range old %d..%d   new %d..%d" % (o_min, o_max, n_min, n_max))
for tag, i1, i2, j1, j2 in ops:
    print("      %-8s old %d..%d -> new %d..%d" % (tag, i1 + 1, i2, j1 + 1, j2))
assert o_min >= 2149 and o_max <= 2309, "change escaped the old TM108 region"
assert n_min >= 2149 and n_max <= e + 1, "change escaped the new TM108 region"
# TM107 fully untouched (ends at old/new line 2148) and TM109's banner untouched
assert OLD[:2148] == NEW[:2148], "prefix (TM107 and everything before) changed"
assert OLD[2309:] == NEW[e + 1:], "suffix (TM109 and everything after) changed"
print("   prefix 1..2148 identical: True    suffix after the TM108 body identical: True")
print("")
print("   hunks @3:", [x for x in difflib.unified_diff(OLD, NEW, n=3, lineterm='') if x.startswith('@@')])

if WRITE:
    with open(LIVE, 'wb') as f:
        f.write(new_b)
    back = open(LIVE, 'rb').read()
    assert back == new_b, "read-back mismatch after write"
    print("")
    print("WROTE %s" % LIVE)
    print("   sha256 %s  size %d" % (hashlib.sha256(back).hexdigest(), len(back)))
else:
    print("")
    print("DRY RUN - nothing written (pass --write to apply)")
