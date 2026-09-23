# Verify two specific claims in t7-selfcheck.md against the delivered revision.
import difflib, os, re

A = r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\tm108-v2-trial'
TGT = r'D:\PROJECT6-DALI\ForCodexDebug\source\test.cpp'
BK = os.path.join(A, 'implementation', 'backup', 'tm108-v2-impl__test.cpp.before')

L = open(TGT, 'rb').read().decode('utf-8-sig', errors='replace').split('\n')
B = open(BK, 'rb').read().decode('utf-8-sig', errors='replace').split('\n')
SYM = 'DUT_API int TM108_HSKP_VAC1_PRST'

sig_lines = [i + 1 for i, l in enumerate(L) if SYM in l]
print('symbol line(s) in delivered file         :', sig_lines)
print('exactly-once full signature              :',
      sum(1 for l in L if SYM + '(short funcindex, LPCTSTR funclabel)' in l))
print("selfcheck check 8 regex 'DUT_API int TM\\w+(' :",
      len([l for l in L if re.match(r'DUT_API int TM\w+\(', l)]))
print('count of all "DUT_API int " declarations :',
      len([l for l in L if re.match(r'DUT_API int ', l)]))

sm = difflib.SequenceMatcher(None, B, L, autojunk=False)
ops = [o for o in sm.get_opcodes() if o[0] != 'equal']
after = (min(o[3] for o in ops) + 1, max(o[4] for o in ops))
before = (min(o[1] for o in ops) + 1, max(o[2] for o in ops))
print('changed opcodes                          :', len(ops))
print('BEFORE-line range across all opcodes     :', before)
print('AFTER-line  range across all opcodes     :', after)
print("selfcheck check 6 claims 'display lines 2149-2216' -> AFTER range match?",
      after == (2149, 2216))
print("selfcheck: symbol line claim 2191, actual:", sig_lines, '-> match?', sig_lines == [2191])
