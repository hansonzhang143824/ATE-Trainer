# Extract the TM108 function's pre-change image and the two contract-named divergence sites.
# Purpose: after t7 edits, the two required corrections can be checked directly against this
# before-image instead of trusting the implementer's manifest prose.
import hashlib, io, json, os, re, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

TARGET = r'D:\PROJECT6-DALI\ForCodexDebug\source\test.cpp'
BASE = r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\tm108-v2-trial\captain-precheck'
OUT_TXT = os.path.join(BASE, 'tm108-block-before.txt')
OUT_JSON = os.path.join(BASE, 'tm108-divergence-sites-before.json')

raw = open(TARGET, 'rb').read()
txt = raw.decode('utf-8-sig', errors='replace')
lines = txt.split('\n')

start = next(i for i, l in enumerate(lines) if 'DUT_API int TM108_HSKP_VAC1_PRST' in l)
end = next(j for j in range(start + 1, len(lines)) if lines[j].rstrip('\r') == '}')
lo, hi = start - 8, end + 2          # include the comment header and the following blank/brace context

block = '\n'.join(lines[lo:hi + 1])
open(OUT_TXT, 'w', encoding='utf-8', newline='') .write(block)
block_sha = hashlib.sha256(block.encode('utf-8')).hexdigest()

rec = {
    'source': TARGET,
    'source_sha256_plaintext': hashlib.sha256(raw).hexdigest(),
    'reader': 'python byte mode (DLP plaintext)',
    'function_line_span': [start + 1, end + 1],
    'extracted_line_span': [lo + 1, hi + 1],
    'extracted_block_sha256': block_sha,
    'extracted_file': OUT_TXT,
    'divergence_sites': {},
}

# Divergence 1: the DTEST0 == nQON assumption embedded in the comment (contract says do not adopt).
nqon = [i + 1 for i, l in enumerate(lines) if 'nQON' in l and lo <= i <= hi]
dtest = [i + 1 for i, l in enumerate(lines) if 'DTEST0' in l and lo <= i <= hi]
rec['divergence_sites']['div1_dtest0_nqon'] = {'nQON_lines': nqon, 'DTEST0_lines': dtest}

# Divergence 2: the K13 (K13_VBAT_Cap) relay state.
# CORRECTION (2026-09-17, same run): the first version used r'\bK13\b' and r'\bK\d+\b'. Those are
# WRONG for this codebase: the relay object is spelled K13_VBAT_Cap, and '_' is a word character, so
# \bK13\b never matches. That produced the false result K13_lines=[] and relay lines [2168,2170).
# Corrected patterns below; verified by eye against the printed lines.
k13 = [i + 1 for i, l in enumerate(lines) if re.search(r'K13(_|\b)', l) and lo <= i <= hi]
relays = [i + 1 for i, l in enumerate(lines) if re.search(r'K\d+', l) and lo <= i <= hi]
regs = [i + 1 for i, l in enumerate(lines) if re.search(r'0x[0-9A-Fa-f]{2}', l) and lo <= i <= hi]
rec['divergence_sites']['div2_k13_relays'] = {
    'K13_lines': k13, 'all_relay_lines_in_function': relays, 'register_write_lines': regs,
    'correction_note': 'first-run \\b-anchored K13/K\\d+ patterns gave a FALSE negative; corrected'}

# Any limit / tolerance comparison present in the function (RT-4 ownership check).
lim = [i + 1 for i, l in enumerate(lines) if lo <= i <= hi and re.search(
    r'(?i)(limit|tol|spec\b|SetTestResult|Compare|IfFail|Result\s*[<>])', l)]
rec['divergence_sites']['limit_or_result_lines'] = lim

os.makedirs(BASE, exist_ok=True)
json.dump(rec, open(OUT_JSON, 'w', encoding='utf-8'), indent=2)

print('function span      :', rec['function_line_span'])
print('extracted span     :', rec['extracted_line_span'], '->', OUT_TXT)
print('block sha256       :', block_sha)
print('nQON lines         :', nqon)
print('DTEST0 lines       :', dtest)
print('K13 lines          :', k13)
print('relay lines in fn  :', relays)
print('limit/result lines :', lim)
for n in sorted(set(nqon + dtest + k13)):
    print('  %5d | %s' % (n, lines[n - 1].rstrip()[:160]))
