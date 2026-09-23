# -*- coding: utf-8 -*-
import json, os, sys

P = r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\tm108-v2-trial\review\t8-review-findings.json'
s = open(P, 'rb').read().decode('utf-8')

PATCHES = []

# (a) three new reviewed inputs
PATCHES.append((
'''      "byteLevelMatch": "matches backup/tm108-v2-impl__test.cpp.before lines 2147..2227 exactly"
    }
  ],''',
'''      "byteLevelMatch": "matches backup/tm108-v2-impl__test.cpp.before lines 2147..2227 exactly"
    },
    {
      "id": "R14",
      "path": "D:/PROJECT6-DALI/ForCodexDebug/source/BoardCheck.h",
      "role": "framework header outside test.cpp, inspected for C11 under the widened scope (captain-named candidate)",
      "sha256_plaintext": "ad562c1c14929bbf71f5549269ce6c44c16352eb4d4299a130952f714d5d83ea",
      "bytes": 32536,
      "hashStableAcrossReview": true,
      "reasonInspected": "declares class CBC_log (:214) with public log() (:759) and test_log() (:760) taking a component string plus limits and unit, and the only instance CBC_log bc_log; (:778)"
    },
    {
      "id": "R15",
      "path": "D:/PROJECT6-DALI/ForCodexDebug/source/treg.h",
      "role": "framework header outside test.cpp, inspected for C11 under the widened scope (captain-named candidate)",
      "sha256_plaintext": "e10c2ac7e2b53b043467ed1579e76de9c41bde2b6e7d5b787a3e0d8ccc262bbc",
      "bytes": 51157,
      "hashStableAcrossReview": true,
      "reasonInspected": "declares TREG_LOG::log_data (:195, private), TREG_ERROR::treg_error_log (:176, public static), and the log_data_t / test_t callback typedefs (:108/:110); treg.h IS in the include closure of test.cpp through StdAfx.h"
    },
    {
      "id": "R16",
      "path": "D:/PROJECT6-DALI/ForCodexDebug/source/src/treg.h",
      "role": "second copy of treg.h in the tree, checked so that the C11 ruling is copy-independent",
      "sha256_plaintext": "ae0d6d6221f8fdb5409e98956218211740170ad6bbfa70ef016d0efbf61450ff",
      "bytes": 47730,
      "hashStableAcrossReview": true,
      "note": "NOT byte-identical to source/treg.h; in BOTH copies log_data is declared under 'private:' in class TREG_LOG, so the C11 conclusion does not depend on which copy the build uses"
    }
  ],'''))

# (b) widen RF-01 evidence
PATCHES.append((
'''CONCLUSION: the implementer's capability claim is CONFIRMED for test.cpp.''',
'''CONCLUSION AT THE ORIGINAL (test.cpp-ONLY) SCOPE: the file exposes no log-writing primitive other than SetTestResult. THE CAPTAIN THEN WIDENED THIS CHECK, withdrawing the test.cpp-only restriction as its own scope error, on the principle that absent-from-test.cpp is not absent-from-the-project. WIDENED RESULT - every named candidate outside test.cpp was probed in python byte mode and NONE is a usable vehicle for R3 s6 logPlan. (i) BoardCheck.h:214 class CBC_log with public log() at :759 and test_log() at :760 (component string plus limits plus unit), instance CBC_log bc_log; at :778: NOT USABLE - BoardCheck.h is NOT in the transitive include closure of test.cpp (closure computed over local headers: Coutlier.h, FMEA.h, LogDataStruct.h, Pin_Channel_define.h, StdAfx.h, Test_Method.h, mylib.h, spec.h, src/visa.h, src/visatype.h, stdafx.h, sub.cpp, sub.h, tempchar.h, test.cpp, treg.h - BoardCheck.h absent), so the type is not even declared for a TM translation unit; the only instance bc_log (:778) sits in BoardCheck's PRIVATE section (nearest specifier private: at :767); CBC_log, bc_log and test_log have ZERO users outside BoardCheck.h/.cpp across all 36 source files; the only instantiations are a local BoardCheck bc; at source/diags.cpp:80 and inside run_diags() (source/diags.cpp:188), which test.cpp:797 calls once from the startup path behind if (DO_BoardCheck) and never from a TM; and the qualified name CBC_log:: occurs 0 times ANYWHERE in the tree, i.e. log() and test_log() are declared but never defined and never called. BoardCheck is a dialog-based board-check utility (BoardCheckGroup, DialogTemplate, listbox, buttons) and BoardCheck.cpp writes NOTHING to the station datalog (0 SetTestResult, 0 msLogData, 0 SetTestNumber; only GetMeasResult 151, i.e. it READS results and CSV). (ii) treg.h:195 TREG_LOG::log_data: NOT REACHABLE - declared under private: (:194) in class TREG_LOG whose friends are only TREG, TRIM_NODE and TRIM_GRP_NODE (:187-189), and a TM function is none of those. This is the important negative result: its implementation (treg.cpp:285-348) IS a genuine datalog write path with exactly the shape R3 s6 needs - it carries a testname string plus limits and unit via log_data_func(site, testname, lolim, hilim, value, unit, no_scaling), else test_func(testnum, value, site, 0), else msLogData(...) - but every piece of the plumbing is private static (TREG_LOG::datalog_func at treg.cpp:275, registered by the private register_dlog_func at treg.h:197), and the ONLY public route into it is a TRIM/TRIM_GRP node execute(..., int log_level = TREG_LOG_STD, ...) at treg.h:559/:565/:742, i.e. the TRIM FRAMEWORK, which R1 s1 declares TM108 does not trigger (trim = null, Trim declared not to trigger the framework). There is no public TREG wrapper: the only log members on the TREG side are the private log_data, the TREG_LOGLEVEL enum, and the log_level default parameters. The conclusion holds for BOTH copies of treg.h in the tree. (iii) treg.h:176 TREG_ERROR::treg_error_log: technically CALLABLE (public static, and treg.h reaches test.cpp through StdAfx.h) but NOT A logPlan VEHICLE - its definition (treg.cpp:227-251) is a debug console error channel: it increments error_count and on the first call does FreeConsole(); AllocConsole(); SetConsoleTitleA(AccoTEST Debug Window); freopen(conout$, w+t, stdout); then printf_s on a numbered line built from the format. All 47 of its uses in treg.cpp are ERROR paths (TREG: No TRIM parameter defined.; post_value define is wrong in PGS...), none is a data record; its sibling TREG_ERROR::error (treg.cpp:256-267) routes to error_func then etsfatalerror() on ETS364 or MessageBox(), i.e. a FATAL error; and TREG_ERROR is used 0 times in test.cpp and sub.cpp. It cannot produce R3 s6 unit/precision/per-site datalog records and using it would misuse a fatal-error console channel. (iv) treg.h:108/:110 log_data_t and test_t: callback TYPEDEFS under #ifdef TREG_ETS364, not callable primitives; the callback is invoked only from the private TREG_LOG::log_data. Not a vehicle. CORROBORATION that SetTestResult IS this project datalog primitive: the framework own logdata helper source/src/treg.cpp:62 stslogdata() writes through CParam::SetTestResult; the active standard R-LOG (rules-registry.md:37) defines the log rule in terms of SetTestResult; and no other candidate API name exists in the tree (WriteLog, AddLog, LogMessage, PrintLog, SetLog, LogString = 0 hits; msLogData only in treg.cpp; DataLog once in BoardCheck.cpp; LogData 91 times in test.cpp and 0 times as a call). CONCLUSION AT THE WIDENED SCOPE: none of the captain candidates is usable, so DEV-3 is a contract-vs-capability finding, NOT a code defect against ate-implementer.'''))

# (c) sharpen repair condition
PATCHES.append((
'''and 'the quantities are in the comments' is NOT accepted by this review as satisfying a logPlan record."''',
'''and 'the quantities are in the comments' is NOT accepted by this review as satisfying a logPlan record. WIDENED-SCOPE ADDENDUM: the re-issue must name a mechanism that is actually REACHABLE FROM A NON-TRIM TM ITEM. If the intended channel is the framework datalog, note that its only writer (TREG_LOG::log_data) is private and fenced to the Trim framework, so exposing it to ordinary TM items would be a PLATFORM/FRAMEWORK change outside ate-implementer's authority and must be raised as such rather than assigned to the implementer. If no reachable channel can be named, option (b) - explicit downgrade to documented comment provenance, stated as the method's own position - is the closure."'''))

# (d) routing note
PATCHES.append((
'''No executable line of test.cpp needs to change to close RF-01."''',
'''No executable line of test.cpp needs to change to close RF-01. The widened project-level probe confirms this: the three captain-named candidates are respectively not declared for a TM translation unit (CBC_log - BoardCheck.h outside the include closure, instance private, qualified name used 0 times tree-wide), private to the Trim framework (TREG_LOG::log_data), and the wrong channel entirely (TREG_ERROR::treg_error_log, a debug-console error/fatal path)."'''))

# (e) widen the C11 answer
PATCHES.append((
'''I also found the same rule fails on the failure path: the code has no no-trigger detection, so a segment with no trigger would log the 0 initialiser (marked as inference RR-02, since the primitive's no-trigger behaviour is undocumented)."''',
'''I also found the same rule fails on the failure path: the code has no no-trigger detection, so a segment with no trigger would log the 0 initialiser (marked as inference RR-02, since the primitive's no-trigger behaviour is undocumented). WIDENED SCOPE (captain correction, accepted): the original check was confined to test.cpp, and absent-from-test.cpp is not absent-from-the-project. I therefore probed every named candidate outside test.cpp and ruled each one out individually with mechanism-level evidence. CBC_log (BoardCheck.h:214/:759/:760) is not usable: BoardCheck.h is NOT in the transitive include closure of test.cpp, its only instance bc_log is a private member of BoardCheck (BoardCheck.h:778 under private: at :767), it has zero users outside BoardCheck.* in the whole tree, and the qualified name CBC_log:: appears 0 times tree-wide so log()/test_log() are undefined and uncalled. TREG_LOG::log_data (treg.h:195) is a genuine datalog writer with exactly the needed shape (testname string plus limits plus unit, via log_data_func / test_func / msLogData) but is private with only TREG, TRIM_NODE and TRIM_GRP_NODE as friends, and its only public route is a Trim node execute() - so it is unreachable from a non-Trim TM item such as TM108, which R1 s1 classifies as trim = null. TREG_ERROR::treg_error_log (treg.h:176) is public static and therefore callable, but its definition (treg.cpp:227-251) AllocConsole()s an AccoTEST Debug Window and printf_s()es numbered lines - it is a debug console ERROR channel, all 47 of its uses in treg.cpp are error paths, its sibling error() is fatal (etsfatalerror / MessageBox), and TREG_ERROR is used 0 times in test.cpp - so it cannot carry R3 s6 unit/precision/per-site records. The log_data_t and test_t entries at treg.h:108/:110 are callback TYPEDEFS, not callable primitives. Corroboration: the framework own logdata helper source/src/treg.cpp:62 stslogdata() itself writes through CParam::SetTestResult, and no other log-API name exists anywhere in the tree. CONCLUSION UNCHANGED: none of the candidates is usable, so DEV-3 is a contract-vs-capability finding owned by test-method-expert, NOT a code finding against ate-implementer. One residual UNKNOWN is recorded honestly as RR-12: CParam's full public surface cannot be enumerated from this checkout because no class CParam declaration exists anywhere under the target root, so a text/logging method on CParam could exist in the external SDK header and would, if found, flip this finding to a code finding."'''))

# (f) gate G-11
PATCHES.append((
'''(and no other is named by R-LOG at rules-registry.md:37). See RF-01."''',
'''(and no other is named by R-LOG at rules-registry.md:37). See RF-01. Re-run at the widened project scope ordered by the captain: BoardCheck.h CBC_log, treg.h TREG_LOG::log_data and treg.h TREG_ERROR::treg_error_log were each examined and none is a usable vehicle (see RF-01 evidence and C11). The gate stays FAIL."'''))

# (g) two new residual risks
PATCHES.append((
'''The hash-bound facts are unaffected." }
  ],''',
'''The hash-bound facts are unaffected." },
    { "id": "RR-12", "severity": "medium", "subject": "CParam's full public surface is not enumerable from this checkout", "detail": "UNKNOWN, stated explicitly rather than assumed. CParam is the only framework object a TM receives (via StsGetParam), and no class CParam declaration exists anywhere under D:/PROJECT6-DALI/ForCodexDebug: the token appears only as a USE (test.cpp 668, source/src/treg.cpp 2, Shmoo.h 1, Test_Method.cpp 1). The class is therefore declared in an external SDK/framework include directory that is not present in this checkout. The observed surface actually used in test.cpp is SetTestResult (188 call sites), GetMaxLimit (3), getNextParam (4) and get_param_name_in_spec (4). Closing action: locate and read the SDK header that declares CParam and enumerate its public API; if it exposes a text or logging method reachable from a TM, RF-01 must be re-opened as a CODE finding against ate-implementer. Until that is done, RF-01 stands on the narrower but sufficient basis that no usable primitive was found among every candidate this tree does expose.", "ownerToVerify": "ate-implementer with compile-diagnostician (include-path owner)" },
    { "id": "RR-13", "severity": "low", "subject": "the tree carries two non-identical copies of treg.h and treg.cpp, and the build's include configuration was not determined", "detail": "source/treg.h (e10c2ac7..., 51157 B) differs from source/src/treg.h (ae0d6d62..., 47730 B), and source/treg.cpp (ae86d1a1..., 160192 B) differs from source/src/treg.cpp (1cefbf11..., 155267 B). Both treg.h copies declare log_data under private: in class TREG_LOG, so the C11 ruling is copy-independent; source/src/treg.cpp:62 additionally defines stslogdata(), which itself uses CParam::SetTestResult. However no .sln/.vcxproj was opened by this role (out of scope, and compilation belongs to compile-diagnostician), so which copy is in the build is UNKNOWN. Closing action: compile-diagnostician records the include path actually used.", "ownerToVerify": "compile-diagnostician" }
  ],'''))

# (h) scopeCorrection block
PATCHES.append((
'''  "reviewStatus": "needs-revision",''',
'''  "scopeCorrection": {
    "raisedBy": "captain (direct input received during t8)",
    "whatChanged": "The t8 contract restricted C11's independent verification to 'no other logging primitive exists in test.cpp'. That scope was too narrow and the captain withdrew it as its own error. RF-01's evidence and the C11 answer were therefore re-based on a project-level probe of every named candidate: BoardCheck.h class CBC_log (:214/:759/:760), treg.h TREG_LOG::log_data (:195), treg.h TREG_ERROR::treg_error_log (:176), and treg.h log_data_t / test_t (:108/:110).",
    "outcome": "Every candidate was ruled out as a usable vehicle for R3 s6 logPlan, each with mechanism-level evidence (include closure, access specifiers, friend lists, method definitions, call sites). The C11 ruling is therefore UNCHANGED in substance and SHARPENED in evidence: DEV-3 remains a contract-vs-capability finding owned by test-method-expert, not a code finding against ate-implementer.",
    "verdictImpact": "none - the terminal verdict remains needs-revision for the same single blocking reason (RF-01)",
    "scopeDisciplineRuleApplied": "absent-from-test.cpp does not mean absent-from-the-project; my first pass committed the narrow-scope error and it is corrected here",
    "whatIsVerifiedVersusInferred": "VERIFIED (measured, not assumed): R1-R5 hashes; the live/backup/manifest hashes and their binding; the backup against the captain's independent pre-change block; the comment-only nature three ways; the TM108 spans; the include closure of test.cpp; the access specifiers and friend lists in BoardCheck.h and both treg.h copies; the absence of any CBC_log:: definition tree-wide; the definition of treg_error_log; the counts in test.cpp and the tree. INFERRED (flagged): that a no-trigger segment logs the 0 initialiser (RR-02), because rampv_capv's no-trigger behaviour is undocumented. UNKNOWN (flagged, not assumed): CParam's full public surface (RR-12), the framework's per-item relay reset (RR-01), and which treg copy is in the build (RR-13).",
    "countDiscrepancyNoted": "The captain's figures 'SetTestResult (200 uses) and GetMeasResult (422)' do not reproduce against any file set I measured. My measurement of test.cpp: SetTestResult 188 call sites (188 raw tokens), GetMeasResult 65 raw and 64 comment-stripped. Tree totals over the 36 source files: SetTestResult 244; GetMeasResult 574 (source/sub.cpp 204, Test_Method.cpp 153, BoardCheck.cpp 151, test.cpp 65, tempchar.cpp 1). LogData: 91 raw tokens in test.cpp but 0 occurrences as a call, confirming the captain's point that it is a step label and not an API. This discrepancy does not affect the C11 conclusion, which rests on access specifiers, include closure and method definitions rather than on counts; it is recorded so the figures can be reconciled."
  },

  "reviewStatus": "needs-revision",'''))

# (i) applicable rule for the scope correction
PATCHES.append((
'''{ "id": "role-charter-precedence", "source": "t8-review-task-contract.md:14-16", "scope": "user ruling > signed resource/config contract > signed method contract > active standards > golden > experience; the implemented function is not an authority", "usedFor": "every conformance statement in this review" }''',
'''{ "id": "role-charter-precedence", "source": "t8-review-task-contract.md:14-16", "scope": "user ruling > signed resource/config contract > signed method contract > active standards > golden > experience; the implemented function is not an authority", "usedFor": "every conformance statement in this review" },
    { "id": "scope-discipline", "source": "captain input during t8, withdrawing the test.cpp-only restriction of C11", "scope": "a claim scoped to one file must not be generalised to the project; conversely, absent from test.cpp is not absent from the project", "usedFor": "the widened C11 evidence: include closure, access specifiers, friend lists and method definitions were checked across the target root" }'''))

# apply
for i, (old, new) in enumerate(PATCHES):
    n = s.count(old)
    if n != 1:
        print('PATCH %d FAILED: anchor found %d times (expected 1)' % (i, n))
        sys.exit(1)
    s = s.replace(old, new, 1)
    try:
        json.loads(s)
        print('patch %d applied (JSON still valid)' % i)
    except Exception as e:
        print('patch %d applied BUT JSON INVALID -> %s' % (i, e))
        print('   new has literal newline:', chr(10) in new, '| dquotes in new:', new.count(chr(34)))
        sys.exit(1)

# validate
d = json.loads(s)
req = ['runId','reviewedInputs','applicableRules','phaseTrace','findings','gateResults','waivedFindings','reviewStatus','residualRisks']
print('missing charter fields:', [k for k in req if k not in d])
print('reviewedInputs:', len(d['reviewedInputs']), '| applicableRules:', len(d['applicableRules']),
      '| findings:', len(d['findings']), '| residualRisks:', len(d['residualRisks']),
      '| reviewStatus:', d['reviewStatus'])
print('RF-01 owner/severity:', [f['responsibleOwner'] for f in d['findings'] if f['id']=='RF-01'],
      [f['severity'] for f in d['findings'] if f['id']=='RF-01'])
print('scopeCorrection present:', 'scopeCorrection' in d)
print('C11 answer length:', len(d['checkItemsAnswered']['C11']['detail']))

with open(P, 'wb') as f:
    f.write(s.encode('utf-8'))
import hashlib
print('written bytes:', os.path.getsize(P), 'sha256:', hashlib.sha256(open(P,'rb').read()).hexdigest())
