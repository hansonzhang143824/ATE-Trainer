# t11 verification - reads everything fresh from disk, python byte mode only.
import hashlib, re, difflib, os

LIVE = r"D:\PROJECT6-DALI\ForCodexDebug\source\test.cpp"
BACKUP = r"D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\tm108-v2-trial\implementation\backup\tm108-v2-impl__test.cpp.before"
T7COPY = r"D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\tm108-v2-trial\review\copy\test.cpp"


def load(p):
    b = open(p, 'rb').read()
    txt = b.decode('utf-8-sig')
    L = txt.split('\n')
    assert L[-1] == '', "file does not end with LF"
    return b, L[:-1]


def props(nm, b):
    crlf = b.count(b'\r\n'); lf = b.count(b'\n')
    print("   %-28s sha %s  size %-7d bom %-5s crlf %-5d bareLF %d  lines %d"
          % (nm, hashlib.sha256(b).hexdigest(), len(b), b[:3] == b'\xef\xbb\xbf', crlf, lf - crlf, lf))


def nc(L):
    return [s for s in L if not (s.strip() == '' or s.strip().startswith('//') or s.strip().startswith('/*')
                                 or s.strip().startswith('*') or s.strip().startswith('*/'))]


def strip_comments(txt):
    out = []; i = 0; n = len(txt)
    while i < n:
        c = txt[i]
        if c in '"\'':
            q = c; out.append(c); i += 1
            while i < n:
                if txt[i] == '\\':
                    out.append(txt[i]); i += 1
                    if i < n:
                        out.append(txt[i]); i += 1
                    continue
                out.append(txt[i])
                if txt[i] == q:
                    i += 1; break
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


print("== 1. files (python byte mode, plaintext)")
lb, L = load(LIVE)
bb, B = load(BACKUP)
props("LIVE (delivered t11)", lb)
props("BACKUP (pre-change)", bb)
t7 = None
if os.path.exists(T7COPY):
    t7b, t7L = load(T7COPY)
    props("review/copy (t7 revision)", t7b)

print("")
print("== 2. audit anchor unchanged")
print("   backup sha256 == manifest beforeSha256 : %s"
      % (hashlib.sha256(bb).hexdigest() == "15c7d2b8d37b15648d552ad5dde14e57b5c0d520d05a41c8c41492a06236c01a"))
print("   backup size 469714 / crlf 9350 / bareLF 3 / bom: %s"
      % (len(bb) == 469714 and bb.count(b'\r\n') == 9350 and bb.count(b'\n') - bb.count(b'\r\n') == 3
         and bb[:3] == b'\xef\xbb\xbf'))

print("")
print("== 3. comments-only property (reader: python byte mode + comment stripper)")
nl, nb = nc(L), nc(B)
print("   non-comment lines: backup %d  delivered %d  sequence byte-identical: %s" % (len(nb), len(nl), nl == nb))
sa = ' '.join(strip_comments(bb.decode('utf-8-sig')).split())
sb = ' '.join(strip_comments(lb.decode('utf-8-sig')).split())
print("   comment-stripped whitespace-normalised: backup sha %s" % hashlib.sha256(sa.encode()).hexdigest())
print("   comment-stripped whitespace-normalised: deliv. sha %s" % hashlib.sha256(sb.encode()).hexdigest())
print("   byte-identical: %s" % (sa == sb))
if t7 is not None:
    print("   delivered non-comment == t7-revision non-comment: %s" % (nl == nc(t7L)))
    print("   delivered comment-stripped == t7 comment-stripped: %s"
          % (sb == ' '.join(strip_comments(t7b.decode('utf-8-sig')).split())))

print("")
print("== 4. signature / symbols (reader: python byte mode, display-line convention = split on LF)")
sig = 'DUT_API int TM108_HSKP_VAC1_PRST(short funcindex, LPCTSTR funclabel)'
for nm, arr in (("backup", B), ("delivered", L)):
    print("   %-10s exact-signature lines %s   occurrences of TM108_HSKP_VAC1_PRST %d"
          % (nm, [i + 1 for i, x in enumerate(arr) if x.rstrip('\r') == sig],
             len([x for x in arr if 'TM108_HSKP_VAC1_PRST' in x])))
ot = '\n'.join(B); nt = '\n'.join(L)
print("   DUT_API\\s+int\\s+TM\\d+   : backup %d  delivered %d"
      % (len(re.findall(r'DUT_API\s+int\s+TM\d+', ot)), len(re.findall(r'DUT_API\s+int\s+TM\d+', nt))))
print("   DUT_API\\s+int\\s+TM\\w+\\s*\\( : backup %d  delivered %d"
      % (len(re.findall(r'DUT_API\s+int\s+TM\w+\s*\(', ot)), len(re.findall(r'DUT_API\s+int\s+TM\w+\s*\(', nt))))
print("   DUT_API\\s+int\\s+\\w+    : backup %d  delivered %d"
      % (len(re.findall(r'DUT_API\s+int\s+\w+', ot)), len(re.findall(r'DUT_API\s+int\s+\w+', nt))))

print("")
print("== 5. cumulative change set (backup -> delivered), display-line convention")
sm = difflib.SequenceMatcher(None, B, L, autojunk=False)
ops = [o for o in sm.get_opcodes() if o[0] != 'equal']
print("   raw change blocks %d   added %d   removed %d   net %+d"
      % (len(ops), sum(o[4] - o[3] for o in ops), sum(o[2] - o[1] for o in ops),
         sum(o[4] - o[3] for o in ops) - sum(o[2] - o[1] for o in ops)))
print("   changed range: backup %d..%d   delivered %d..%d"
      % (min(o[1] for o in ops) + 1, max(o[2] for o in ops),
         min(o[3] for o in ops) + 1, max(o[4] for o in ops)))
print("   hunks @3:", [x for x in difflib.unified_diff(B, L, n=3, lineterm='') if x.startswith('@@')])
sb_ = next(i for i, x in enumerate(B) if x.rstrip('\r') == sig)
se_ = next(i for i in range(sb_ + 1, len(B)) if B[i].rstrip('\r') == '}')
sl_ = next(i for i, x in enumerate(L) if x.rstrip('\r') == sig)
el_ = next(i for i in range(sl_ + 1, len(L)) if L[i].rstrip('\r') == '}')
print("   TM108 span: backup %d..%d   delivered %d..%d" % (sb_ + 1, se_ + 1, sl_ + 1, el_ + 1))
print("   banner: backup 2149..2154   delivered 2149..%d" % (sl_))

print("")
print("== 6. scope confinement")
print("   backup lines 1..2148 == delivered lines 1..2148 : %s" % (B[:2148] == L[:2148]))
print("   backup body-end..  == delivered body-end..       : %s" % (B[se_ + 1:] == L[el_ + 1:]))
print("   TM109 heading line (delivered): %d" % (next(i + 1 for i, x in enumerate(L) if x.startswith('// TM109'))))

print("")
print("== 7. TM108 step headings (delivered)")
for i in range(sl_ - 5, el_ + 1):
    x = L[i].rstrip('\r')
    if re.match(r'\s*// ====== Step \d', x):
        print("      %5d  %s" % (i + 1, x))
print("   TM107 Step 4 (must be untouched, line <=2148): %s"
      % [(i + 1, x.strip()) for i, x in enumerate(L) if x.strip().startswith('// ====== Step 4')
         and i + 1 <= 2148])
print("   TM109 Step 4 (must be untouched): %s"
      % [(i + 1) for i, x in enumerate(L) if x.strip().startswith('// ====== Step 4') and i + 1 > el_])

print("")
print("== 8. no release call / no new API call anywhere")
for pat in ["SetOff", "RelayOff", ".Off(", "DelayOff", "SetOffAll", "Release"]:
    print("   delivered occurrences of %-10s : %d   (backup %d)"
          % (pat, nt.count(pat), ot.count(pat)))
print("   delivered occurrences of 'cbite.SetOn': %d   (backup %d)" % (nt.count('cbite.SetOn'), ot.count('cbite.SetOn')))

print("")
print("== 9. frozen parameter guard (no electrical value touched) - verbatim presence in the TM108 body")
body = '\n'.join(L[sl_ - 1:el_])
for tok in ["cbite.SetOn(K13_VBAT_Cap, K65_nQON_PU, -1)", "delay_ms(3)",
            "VBAT_PD3_FXVI.Set(FV, 3, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON)",
            "I2CWriteSameData(DEV_ADDR, 0x56, 0x16)", "I2CWriteSameData(DEV_ADDR, 0x57, 0x08)",
            "0.0, 10.0, 200, 20, 1.65, TRIG_FALLING, vth_r",
            "10.0, 0.0, 200, 20, 1.65, TRIG_RISING, vth_f",
            "hys[site] = (rise_result[site] - fall_result[site]) * 1e3"]:
    print("   %-58s : %s" % (tok[:58], body.count(tok)))
