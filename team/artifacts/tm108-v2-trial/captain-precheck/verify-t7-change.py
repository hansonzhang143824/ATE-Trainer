# Captain's post-change verification for t7 (independent of the implementer's manifest prose).
# Run AFTER t7 reports DONE (before dispatching t8) and again at the commander's final sign-off.
# Reader: python byte mode (DLP plaintext) - never pwsh/.NET on these files.
#
# Smoke-test history (2026-09-17, recorded so the bugs are not repeated):
#  v1 (a) read the before-image without newline='' so universal-newline translation stripped '\r'
#         and printed a spurious 166-line diff on an unchanged file; (b) ran the C1 check over the
#         function body only, excluding the comment header :2150/:2152 where the assertion lives.
#  v2 had a wrong before-image filename and a stray no-op SequenceMatcher line.
#  v3 (this file) fixes all of the above and adds a backup-hash-verified full-file scope check.
import difflib, hashlib, io, json, os, re, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

TARGET = r'D:\PROJECT6-DALI\ForCodexDebug\source\test.cpp'
RUN = r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\tm108-v2-trial'
BASE_DIR = os.path.join(RUN, 'captain-precheck')
BASELINE = os.path.join(BASE_DIR, 't7-pre-change-baseline.json')
BLOCK_BEFORE = os.path.join(BASE_DIR, 'tm108-block-before.txt')
MANIFEST = os.path.join(RUN, 'implementation', 'implementation-manifest.json')
OUT_JSON = os.path.join(BASE_DIR, 't7-post-change-verification.json')
OUT_DIFF = os.path.join(BASE_DIR, 't7-block-diff.txt')
SYMBOL = 'DUT_API int TM108_HSKP_VAC1_PRST'
CTX = 70        # the conformant revision adds a ~44-line banner ABOVE the symbol, plus step comments.
                # CTX=8 (v3) was blind to that banner: it returned c1_candidate_lines=[] and a false
                # "OK" verdict on 2026-09-17. Widened; the C1 window is further pinned to the banner.


def pl(path):
    b = open(path, 'rb').read()
    return b, b.decode('utf-8-sig', errors='replace')


def pl_text(path):
    return open(path, 'rb').read().decode('utf-8-sig', errors='replace')


base = json.load(open(BASELINE, encoding='utf-8'))['files']['test.cpp']
raw, txt = pl(TARGET)
lines = txt.split('\n')

block_before = pl_text(BLOCK_BEFORE) if os.path.exists(BLOCK_BEFORE) else ''

start = next((i for i, l in enumerate(lines) if SYMBOL in l), None)
end = None
if start is not None:
    for j in range(start + 1, len(lines)):
        if lines[j].rstrip('\r') == '}':
            end = j
            break

lo = max(0, start - CTX)
hi = min(len(lines) - 1, end + 2)
span = (lo, hi)
block_after = '\n'.join(lines[lo:hi + 1])
span_lines = lines[lo:hi + 1]
joined = '\n'.join(span_lines)

res = {
    'runId': 'tm108-v2-impl', 'task': 't7', 'checkedBy': 'captain',
    'reader': 'python byte mode (DLP plaintext)',
    'after': {
        'sha256_plaintext': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw),
        'utf8_bom': raw[:3] == b'\xef\xbb\xbf', 'crlf_count': txt.count('\r\n'),
        'line_count': len(lines), 'dut_api_count': len(re.findall(r'DUT_API\s+int', txt)),
        'tm108_occurrence_lines': [i + 1 for i, l in enumerate(lines) if 'TM108' in l],
        'function_line_span': [start + 1, end + 1], 'extracted_span': [lo + 1, hi + 1],
    },
    'before': {
        'sha256_plaintext': base['sha256_plaintext'], 'bytes': base['bytes'],
        'line_count': base['line_count'], 'dut_api_count': base['dut_api_count'],
        'crlf_count': base['crlf_count'],
        'function_line_span': [base['tm108']['start_line'], base['tm108']['end_line']],
    },
}
a = res['after']
c = res['checks'] = {}

c['file_changed'] = a['sha256_plaintext'] != res['before']['sha256_plaintext']
c['bom_preserved'] = a['utf8_bom'] == base['utf8_bom']
c['crlf_delta'] = a['crlf_count'] - res['before']['crlf_count']
c['signature_present_and_unchanged'] = any(SYMBOL + '(short funcindex, LPCTSTR funclabel)' in l for l in lines)
c['dut_api_count_delta'] = a['dut_api_count'] - res['before']['dut_api_count']
c['tm108_occurrences_now'] = len(a['tm108_occurrence_lines'])

# --- contract invariants that must survive the edit (from review/t8-review-task-contract.md §4b/§4c) ---
c['closure_set_13_65_present'] = bool(re.search(r'SetOn\([^)]*K13_VBAT_Cap[^)]*K65_nQON_PU', joined))
c['k21_not_closed'] = not re.search(r'SetOn\([^)]*K21_VAC_Cap', joined)
c['no_cbite_release_added'] = not re.search(r'cbite\.(SetOff|RelayOff|Off|Reset)', joined)
c['cbite_seton_closure_lines'] = [i for i, l in enumerate(span_lines)
                                  if 'cbite.SetOn' in l]
c['csv_layer_alt_0x55_0x97_absent'] = ('0x97' not in joined) and ('0x55' not in joined)
tol_words = [l.strip() for l in span_lines if re.search(r'(?i)(\btol\w*\b|guard\s*band|margin)', l)]
c['tolerance_word_lines'] = tol_words
c['numeric_tolerance_introduced'] = bool(
    re.search(r'[\u00b1]|\+/-|tolerance\s*[:=]\s*[\d.]+', joined, re.I))
c['measurement_call_pair_present'] = (joined.count('test_method.rampv_capv') == 2
                                      and 'TRIG_FALLING' in joined and 'TRIG_RISING' in joined)
c['register_writes_present'] = ('0x56, 0x16' in joined and '0x57, 0x08' in joined
                                and 'entertestmode()' in joined)

# --- C1: the DTEST0 == nQON identity assertion must be gone or explicitly marked pending ---
# Window = from the TM108 banner (first comment line mentioning TM108 above the symbol) to the end.
banner = next((i for i in range(max(0, start - CTX), start) if 'TM108' in lines[i]), max(0, start - CTX))
c['c1_window_lines'] = [banner + 1, end + 1]
c1_lines = lines[banner:end + 1]
candidate = [l.strip() for l in c1_lines if re.search(r'(?i)nqon', l) and 'DTEST0' in l]
ASSERT = re.compile(r'(DTEST0[^(\n]{0,10}\)?\s*=\s*nQON)|(nQON[^\n]{0,10}\)?\s*=\s*DTEST0)', re.I)
PENDING = re.compile(r'(?i)(OI-T4-01|pending|unresolved|not\s+(yet\s+)?(proven|established))')
c['c1_candidate_lines'] = candidate
c['c1_assertion_still_present'] = any(ASSERT.search(l) for l in candidate)
c['c1_pending_marker_present'] = any(PENDING.search(l) for l in candidate)
c['c1_verdict'] = 'FAIL - forbidden assertion still present' if c['c1_assertion_still_present'] else 'OK - assertion gone'

# --- block diff (self-contained: needs no implementer artifact) ---
block_diff = list(difflib.unified_diff(block_before.split('\n'), block_after.split('\n'),
                                       fromfile='tm108-block-before.txt',
                                       tofile='tm108-block-after.txt', lineterm='', n=3))
c['tm108_block_unchanged'] = (block_before == block_after)
c['tm108_block_diff_lines'] = len(block_diff)
open(OUT_DIFF, 'w', encoding='utf-8', newline='').write('\n'.join(block_diff))

# --- full-file scope check, using the t7 backup but only after proving the backup IS the pre-image ---
scope = {'status': 'UNKNOWN - no manifest/backup yet'}
if os.path.exists(MANIFEST):
    try:
        man = json.load(open(MANIFEST, encoding='utf-8'))
        bks = man.get('backups') or []
        hit = None
        for b in bks:
            orig = (b.get('original') or '').replace('/', '\\')
            if orig.lower().endswith('test.cpp'):
                cand = (b.get('backup') or '')
                cand_abs = cand if os.path.isabs(cand) else os.path.join(RUN, cand)
                if os.path.exists(cand_abs):
                    hit = (b, cand_abs)
                else:
                    # try relative to the workspace root
                    alt = os.path.join(r'D:\Newtest\DSH\ATE-Coding-Plat', cand.replace('/', '\\'))
                    if os.path.exists(alt):
                        hit = (b, alt)
                break
        if hit:
            b, path = hit
            bt = pl_text(path)
            bh = hashlib.sha256(open(path, 'rb').read()).hexdigest()
            ok = (bh == base['sha256_plaintext'])
            hunks = []
            for grp in difflib.SequenceMatcher(None, bt.split('\n'), lines, autojunk=False).get_grouped_opcodes(3):
                first_a = grp[0][1] + 1
                first_b = grp[0][3] + 1
                last_b = grp[-1][4]
                hunks.append([first_a, first_b, last_b])
            inside = all(h[1] >= lo + 1 and h[2] <= hi + 1 for h in hunks)
            scope = {'status': 'CHECKED', 'backup': path,
                     'backup_matches_recorded_preimage': ok,
                     'hunks_before_line/after_start/after_end': hunks,
                     'all_hunks_inside_tm108_span': inside,
                     'tm108_span_after': [lo + 1, hi + 1]}
        else:
            scope = {'status': 'UNKNOWN - manifest has no usable test.cpp backup'}
    except Exception as e:                                   # noqa: BLE001
        scope = {'status': 'UNKNOWN - manifest unreadable: %s' % e}
c['full_file_scope_check'] = scope

os.makedirs(BASE_DIR, exist_ok=True)
json.dump(res, open(OUT_JSON, 'w', encoding='utf-8'), indent=2)

print('after sha256 :', a['sha256_plaintext'])
print('before sha256:', res['before']['sha256_plaintext'])
print('function span:', a['function_line_span'], ' extracted:', a['extracted_span'])
for k, v in c.items():
    print('  %-38s %s' % (k, str(v)[:150]))
print('json :', OUT_JSON)
print('diff :', OUT_DIFF)
