# -*- coding: utf-8 -*-
"""Build team/artifacts/<run-id>/dft-ir.json (t1 deliverable) — part 2: TM108/109/135/600/601/1205 + assembly."""
import os, json, hashlib, sys, datetime
sys.stdout.reconfigure(encoding='utf-8')

ROOT = r"D:/Newtest/DSH/ATE-Coding-Plat"
RUN = "acceptance-20260916-dali10"
RAW = os.path.join(ROOT, "team", "artifacts", RUN, "dft-raw")
DBG_TCPP = r"D:/PROJECT6-DALI/ForCodexDebug/source/test.cpp"

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for c in iter(lambda: f.read(1 << 20), b''):
            h.update(c)
    return h.hexdigest()

H = {
    'xlsx': sha256_file(os.path.join(ROOT, 'project/DALI/Dali_testmode.xlsx')),
    'dftcsv': sha256_file(os.path.join(ROOT, 'project/DALI/input/DFT.csv')),
    'dftrestored': sha256_file(os.path.join(ROOT, 'project/DALI/input/DFT_restored.csv')),
    'meta': sha256_file(os.path.join(ROOT, 'project/DALI/meta/dali_tm_meta.json')),
    'testcpp': sha256_file(DBG_TCPP),
    'progress': sha256_file(os.path.join(ROOT, 'docs/PROGRESS.md')),
    'golden600': sha256_file(os.path.join(ROOT, 'knowledge/references/L4-Golden-code/tm600-normal-highcurrent.cpp')),
    'golden1205': sha256_file(os.path.join(ROOT, 'knowledge/references/L4-Golden-code/TM1205_TRX_BST_UV_GD.cpp')),
    'golden1205md': sha256_file(os.path.join(ROOT, 'knowledge/references/L4-Golden-code/TM1205_TRX_BST_UV_GD.md')),
    'pmi': sha256_file(os.path.join(ROOT, 'knowledge/references/param_type_index.md')),
}
SV = ['tm600.sv', 'tm601.sv', 'tm102.sv', 'tm103.sv', 'tm108.sv', 'tm109.sv', 'tm135.sv', 'tm1205.sv',
      'tm108_1.sv', 'tm001_2.sv', 'tm100.sv', 'tm101.sv']
for n in SV:
    H['sv_' + n] = sha256_file(os.path.join(ROOT, 'project/DALI/reg_config', n))

def E_xlsx(sheet, locator, note=''):
    d = {'path': 'project/DALI/Dali_testmode.xlsx', 'sha256': H['xlsx'],
         'locator': 'sheet=%s!%s' % (sheet, locator)}
    if note: d['note'] = note
    return d

def E_csv(path_rel, key, locator, note=''):
    d = {'path': path_rel, 'sha256': H[key], 'locator': locator}
    if note: d['note'] = note
    return d

def E_sv(n, locator, note=''):
    d = {'path': 'project/DALI/reg_config/' + n, 'sha256': H['sv_' + n], 'locator': locator}
    if note: d['note'] = note
    return d

def E_testcpp(name, line_range=''):
    return {'path': 'D:/PROJECT6-DALI/ForCodexDebug/source/test.cpp', 'sha256': H['testcpp'],
            'locator': ('DUT_API %s%s' % (name, (' ' + line_range) if line_range else ''))}

def E_file(path_rel, hkey, locator, note=''):
    d = {'path': path_rel, 'sha256': H[hkey], 'locator': locator}
    if note: d['note'] = note
    return d

def E_meta(fn):
    return {'path': 'project/DALI/meta/dali_tm_meta.json', 'sha256': H['meta'],
            'locator': 'functions[functionName=%s]' % fn,
            'note': 'derived registry (generated from OVERVIEW by gen_testitems_meta.py) — corroborating, not primary'}

def S(kind, pin, value=None, unit=None, ramp_time=None, ignore=None, note=''):
    o = {'kind': kind, 'pin': pin}
    if value is not None: o['value'] = value
    if unit: o['unit'] = unit
    if ramp_time: o['rampTime'] = ramp_time
    if ignore is not None: o['ignore'] = ignore
    if note: o['note'] = note
    return o

def M(kind, pin, unit=None, note=''):
    o = {'kind': kind, 'pin': pin}
    if unit: o['unit'] = unit
    if note: o['note'] = note
    return o

def L(vmin=None, vmax=None, unit=None, expression=None, sourceRank=1, note=''):
    o = {}
    if expression: o['expression'] = expression
    if vmin is not None: o['min'] = vmin
    if vmax is not None: o['max'] = vmax
    if unit: o['unit'] = unit
    o['sourceRank'] = sourceRank
    if note: o['note'] = note
    return o

def R(kind, reg, value, fields, note=''):
    o = {'kind': kind, 'reg': reg, 'value': value}
    if fields: o['fields'] = fields
    if note: o['note'] = note
    return o

items = json.loads(open(os.path.join(RAW, '_items_part1.json'), encoding='utf-8').read()) if os.path.exists(os.path.join(RAW, '_items_part1.json')) else []
if not items:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import importlib.util
    spec = importlib.util.spec_from_file_location('p1', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dft_ir_items_part1.py'))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    items = m._ITEMS
print('loaded part1 items:', [i['tm'] for i in items])

# ---------------------------------------------------------------- TM108
items.append({
 "tm": "TM108",
 "symbol": "TM108_HSKP_VAC1_PRST",
 "symbolHint": "TM108_HSKP_VAC1_PRST",
 "overviewItem": "TM108 (base) + TM108_1 (DMO/A output variant)",
 "name": "VAC1_PRST",
 "level": "HSKP",
 "description": "VAC1 PRST COMP threshold, observed as a DTEST0/nQON logic toggle while VAC1 is ramped",
 "testType": ["toggle", "grouped"],
 "testTypeNote": "AWG ramp-threshold (UVLO/PRST) toggle; grouped identity = base TM108 + DMO/A variant TM108_1",
 "channels": [
   {"role": "supply", "pins": ["VBAT"], "sense": "none"},
   {"role": "ramp", "pins": ["VAC1"], "sense": "scanned source (voltage at the toggle instant is the result)"},
   {"role": "observer", "pins": ["DTEST0 -> nQON pad"], "sense": "logic level read through nQON_HG1_ACM with K65_nQON_PU pull-up"},
 ],
 "stimuli": [
   S("vset", "vbat", 3.0, "V", "100e-6", 0, "OVERVIEW Code1 / reg_config/tm108.sv (DFT.csv says 4.2 V — see conflicts)"),
   S("ramp_up", "vac1", 10.0, "V", "1e-3", 0, "OVERVIEW Code2 vset[vac1,10,1e-3,0] as written; the OVERVIEW Notes describe the real intent as 'ramp up/down vac1 from 3~5V, 1V/ms'"),
   S("ramp_down", "vac1", 0.0, "V", "1e-3", 0, "OVERVIEW Code2 vset[vac1,0,1e-3,0]"),
   S("en_tm", "(none)", None, None, None, None, "Code2 en_tm[]"),
   S("field", "(none)", None, None, None, None, "Code2 field[(DMUX_EN,1),(DMUX_SEL,22)] -> a2d_vac1_prst routed to DTEST0"),
   S("delay", "(none)", None, None, "1e-3", None, "Code3 delay[1e-3]"),
 ],
 "measurements": [
   M("MV", "DTEST0", "V", "toggle threshold captured on the ramp source: rising threshold and falling threshold; hysteresis = rise - fall (x1e3 mV)"),
 ],
 "limits": [
   L(unit="V", expression="ExpectValue 'rising vth 4.4V, hys 0.35V' (OVERVIEW + meta)", sourceRank=1,
     note="OVERVIEW/meta authoritative value: rise 4.4 V, hys 0.35 V."),
   L(unit="V", expression="DFT.csv record 9 ExpectValue 'rising vth 4.15V, hys 0.35V'", sourceRank=2,
     note="DFT.csv rising threshold 4.15 V vs OVERVIEW 4.4 V — 250 mV discrepancy, recorded as conflict C-02 (not averaged, not silently chosen)."),
 ],
 "sequence": [
   "cbite.SetOn(K13_VBAT_Cap, K65_nQON_PU, -1); delay 3 ms (VAC1 is the scanned input: K21_VAC_Cap must stay open)",
   "VBAT=3 V on; entertestmode(); DMUX_SEL=22 + DMUX_EN=1",
   "library ramp capture: rampv_capv(VAC1 source, observer nQON source, 0->10 V TRIG_FALLING -> rise; 10->0 V TRIG_RISING -> fall)",
   "hys = (rise - fall) x 1e3; power down in three steps",
 ],
 "registerWritesFromOverview": [
   R("I2CWriteSameData", "0x56", "0x16", "DMUX_SEL=22 (a2d_vac1_prst) per reg_config/tm108.sv"),
   R("I2CWriteSameData", "0x57", "0x08", "DMUX_EN=1 per reg_config/tm108.sv"),
 ],
 "variants": [
   {"item": "TM108", "scopeKind": "base", "description": "VAC1 PRST COMP threshold, DTEST0/nQON toggle observation",
    "benchDatapoint": "r 4.059 / f 3.738 (hys ~0.321 V)", "helper": "ramp VAC , INT toggle",
    "evidence": [E_xlsx("OVERVIEW", "row 15 (Item=TM108)"), E_sv("tm108.sv", "0x56=0x16 / 0x57=0x08 / vac1 ramp 10V then 0V, 1e-3"),
                 E_testcpp("TM108_HSKP_VAC1_PRST", "(lines 2148-2225)")]},
   {"item": "TM108_1", "scopeKind": "variant", "description": "Same threshold measured through the DMO/A output instead of DTEST0",
    "fieldDirective": "key1_open[]; field[(DMUX_EN,1),(DMUX_SEL,22)]; field[(D2A_DMO_CHANNEL_SEL,1),(D2A_DMA_CHANNEL_SEL,1),(DM_CHANNEL_SEL_OVER_WRITE,1),(D2A_DMA_EN,1),(D2A_DMO_EN,1)]",
    "evidence": [E_xlsx("OVERVIEW", "row 16 (Item=TM108_1)"), E_sv("tm108_1.sv", "DMO/A observer enable group")]},
 ],
 "groupedIdentity": "TM108 and TM108_1 share the TM108 base with different observation paths (DTEST0 vs DMO/A). Only the TM108 base is named in the acceptance scope.",
 "evidence": [
   E_xlsx("OVERVIEW", "rows 15-16 (Item=TM108, TM108_1)"),
   E_csv("project/DALI/input/DFT.csv", 'dftcsv', 'CSV record 9 (Item=TM108, Function Name=VAC_PRST, ExpectValue rising 4.15V/hys 0.35V, Check=INT, Type=Toggle,MV)',
         'DFT.csv observes INT and writes 0x55=0x97 for field[(EN_DTEST0,1),(DTEST0_MUX,23)] — a different DMUX_SEL from reg_config/tm108.sv (22)'),
   E_csv("project/DALI/input/DFT_restored.csv", 'dftrestored', 'CSV record 9 (identical to DFT.csv for TM108)'),
   E_sv("tm108.sv", "0x56=0x16 (DMUX_SEL=22) / 0x57=0x08"),
   E_meta("TM108_HSKP_VAC1_PRST"),
   E_testcpp("TM108_HSKP_VAC1_PRST", "(lines 2148-2225)"),
 ],
 "ambiguities": [
   "DMUX_SEL is 22 per OVERVIEW+reg_config/tm108.sv but the DFT.csv comment says DTEST0_MUX=23 -> the register value must be settled by t3/t4 (recorded as conflict C-04).",
   "OVERVIEW Code2 writes vset[vac1,10,1e-3] (full 0..10 V sweep) while the Notes specify '3~5V, 1V/ms'; the implemented ramp is 0..10 V.",
   "Observability: DFT.csv checks the INT pin, OVERVIEW/implementation observe DTEST0/nQON — the identity of the physical observation pin is a t2/t3 decision.",
 ],
 "confidence": "high",
 "implementationState": {"presentInDebugTestCpp": True, "functionName": "TM108_HSKP_VAC1_PRST", "lines": "2148-2225"},
})

# ---------------------------------------------------------------- TM109
items.append({
 "tm": "TM109",
 "symbol": "TM109_HSKP_VAC2_PRST",
 "symbolHint": "TM109_HSKP_VAC2_PRST",
 "overviewItem": "TM109",
 "name": "VAC2_PRST",
 "level": "HSKP",
 "description": "VAC2 PRST COMP threshold, observed as a DTEST0/nQON logic toggle while VAC2 is ramped",
 "testType": ["toggle"],
 "testTypeNote": "AWG ramp-threshold (UVLO/PRST) toggle, observed as a DTEST0/nQON logic flip",
 "channels": [
   {"role": "supply", "pins": ["VBAT"], "sense": "none"},
   {"role": "ramp", "pins": ["VAC2"], "sense": "scanned source"},
   {"role": "observer", "pins": ["DTEST0 -> nQON pad"], "sense": "logic level read with K65_nQON_PU pull-up"},
 ],
 "stimuli": [
   S("vset", "vbat", 3.0, "V", "100e-6", 0, "OVERVIEW Code1 / reg_config/tm109.sv (DFT.csv says 4.2 V — see conflicts)"),
   S("ramp_up", "vac2", 10.0, "V", "1e-3", 0, "Code2 vset[vac2,10,1e-3,0]"),
   S("ramp_down", "vac2", 0.0, "V", "1e-3", 0, "Code2 vset[vac2,0,1e-3,0]"),
   S("en_tm", "(none)", None, None, None, None, "Code2 en_tm[]"),
   S("field", "(none)", None, None, None, None, "Code2 field[(DMUX_EN,1),(DMUX_SEL,21)] -> a2d_vac2_prst"),
   S("delay", "(none)", None, None, "1e-3", None, "Code3 delay[1e-3]"),
 ],
 "measurements": [M("MV", "DTEST0", "V", "rising/falling toggle thresholds captured on the ramp source; hys = rise - fall (x1e3 mV)")],
 "limits": [
   L(unit="V", expression="ExpectValue 'rising vth 4.4V, hys 0.35V' (OVERVIEW + meta)", sourceRank=1),
   L(unit="V", expression="DFT.csv record 10 ExpectValue 'rising vth 4.15V, hys 0.35V'", sourceRank=2,
     note="Same 250 mV discrepancy as TM108 — conflict C-02."),
 ],
 "sequence": [
   "cbite.SetOn(K13_VBAT_Cap, K65_nQON_PU, K19_ACM0_VAC2, -1); delay 3 ms",
   "VBAT=3 V on; entertestmode(); DMUX_SEL=21 + DMUX_EN=1",
   "rampv_capv dual sweep (0->10 V TRIG_FALLING = rise, 10->0 V TRIG_RISING = fall)",
   "hys x1e3; three-step power-down",
 ],
 "registerWritesFromOverview": [
   R("I2CWriteSameData", "0x56", "0x15", "DMUX_SEL=21 (a2d_vac2_prst) per reg_config/tm109.sv"),
   R("I2CWriteSameData", "0x57", "0x08", "DMUX_EN=1 per reg_config/tm109.sv"),
 ],
 "variants": [],
 "evidence": [
   E_xlsx("OVERVIEW", "row 17 (Item=TM109)"),
   E_csv("project/DALI/input/DFT.csv", 'dftcsv', 'CSV record 10 (Item=TM109, ExpectValue rising 4.15V/hys 0.35V, Dynamic=vset[vac3,...], Check=INT)',
         'DFT.csv Dynamic drives VAC3 while the item is VAC2 — a source-internal inconsistency in DFT.csv itself'),
   E_csv("project/DALI/input/DFT_restored.csv", 'dftrestored', 'CSV record 10 (identical to DFT.csv for TM109)'),
   E_sv("tm109.sv", "0x56=0x15 (DMUX_SEL=21) / 0x57=0x08"),
   E_meta("TM109_HSKP_VAC2_PRST"),
   E_testcpp("TM109_HSKP_VAC2_PRST", "(lines 2225-2303)"),
 ],
 "ambiguities": [
   "DFT.csv record 10 ramps vac3 (not vac2) and uses DTEST0_MUX=22 (the TM108 value) — duplicate/garbled row; OVERVIEW + reg_config/tm109.sv (DMUX_SEL=21, vac2) is used as primary.",
   "Same INT-vs-DTEST0/nQON observation-pin question as TM108.",
 ],
 "confidence": "high",
 "implementationState": {"presentInDebugTestCpp": True, "functionName": "TM109_HSKP_VAC2_PRST", "lines": "2225-2303"},
})

# ---------------------------------------------------------------- TM135
items.append({
 "tm": "TM135",
 "symbol": "Trim_BG_RES_DIV",
 "symbolHint": "Trim_BG_RES_DIV",
 "overviewItem": "TM135",
 "name": "VREF_1P0",
 "level": "BG",
 "description": "VREF_1P0 ACC — bandgap resistor-divider trim (TRIM_BG_RES_DIV), target 1.000 V measured on ATEST0/VDM",
 "testType": ["trim"],
 "trim": {"flag": True, "node": "bg_res_div", "steps": 8, "target_mV": 1000,
          "stepParams": ["BG_RES_DIV_step0..step7"], "readbackParams": ["BG_RES_DIV_pre_value", "BG_RES_DIV_pre_bit",
                                                                          "BG_RES_DIV_post_bit", "BG_RES_DIV_updated",
                                                                          "BG_RES_DIV_guessed", "BG_RES_DIV_target",
                                                                          "BG_RES_DIV_post_value", "BG_RES_DIV_post_rt"],
          "evidence": [E_testcpp("Trim_BG_RES_DIV", "(lines 3921-3987) header comment: 'treg: bg_res_div, 8步(ASSY F1 bits 2-4), Target=1000mV'"),
                       E_file("knowledge/references/L4-Golden-code/sub-measure-template.cpp", 'golden600', 'sub-measure template (measured via the sub.cpp measure_bg_res_div helper)')]},
 "channels": [{"role": "supply", "pins": ["VBAT"], "sense": "none"},
              {"role": "test-pad", "pins": ["VDM"], "sense": "MV (V(ATEST0) via VDM held high-Z)"}],
 "stimuli": [
   S("vset", "vbat", 5.0, "V", "100e-6", 0, "OVERVIEW Code1 / reg_config/tm135.sv"),
   S("en_tm", "(none)", None, None, None, None, "Code1 en_tm[]"),
   S("field", "(none)", None, None, None, None, "Code2 field[(WAKE_UP,1)] then field[(EN_ATEST0,1),(ATEST0_MUX,10)]"),
   S("delay", "(none)", None, None, "1e-3", None, "Code3 delay[1e-3]"),
   S("vset_off", "vdm", None, None, None, None, "vset_off[vdm] before the trim readback (implementation: FI,0 high-Z)"),
 ],
 "measurements": [M("MV", "ATEST0", "mV", "measure_bg_res_div writes EFUSE_REG_F1 and returns mV (MVRET x 1e3); trim driver compares against the 1000 mV target")],
 "limits": [L(unit="V", expression="ExpectValue=1 (VREF_1P0 target); trim target 1000 mV", sourceRank=1,
              note="OVERVIEW 1 V; 'de test' 0.9853 V; aetest note 'Bench Passed, 0.998V, able to trim'. No tolerance given.")],
 "sequence": ["connect K13_VBAT_Cap", "VBAT=5 V on", "entertestmode(); WAKE_UP=1; EN_ATEST0=1 + ATEST0_MUX=10",
              "release VDM to high-Z", "TRIM_NODE.execute(measure_bg_res_div, spec, ...) — per-step EFUSE write + VDM MV readback",
              "three-step power-down"],
 "registerWritesFromOverview": [
   R("I2CWriteSameData", "0x10", "0x43", "WAKE_UP=1 per reg_config/tm135.sv"),
   R("I2CWriteSameData", "0x57", "0x02", "EN_ATEST0=1 per reg_config/tm135.sv"),
   R("I2CWriteSameData", "0x5E", "0x0A", "ATEST0_MUX=10 -> BG_RES_DIV per reg_config/tm135.sv"),
 ],
 "variants": [],
 "evidence": [
   E_xlsx("OVERVIEW", "row 45 (Item=TM135, Trim=Y, Notes='TRIM_BG_RES_DIV')"),
   E_csv("project/DALI/input/DFT.csv", 'dftcsv', 'no TM135 record exists in DFT.csv'),
   E_sv("tm135.sv", "vbat=5V / 0x10=0x43 / 0x57=0x02 / 0x5E=0x0A / delay 1e-3"),
   E_meta("Trim_BG_RES_DIV"),
   E_testcpp("Trim_BG_RES_DIV", "(lines 3921-3987)"),
   E_testcpp("measure_bg_res_div", "(declared in sub.h; defined in sub.cpp around line 2978)"),
 ],
 "ambiguities": [
   "Step count: the DFT sources do not state the trim step count; 8 steps is taken from the test.cpp comment 'ASSY F1 bits 2-4'. The authoritative step definition lives in the TReg/EFUSE definition, which this task must not edit — flagged for t3/t4 to confirm.",
   "OVERVIEW ExpectValue=1 V vs 'de test' 0.9853 V: the 1 V figure is a target, not a measured limit; no tolerance exists in any DFT source.",
 ],
 "confidence": "high",
 "implementationState": {"presentInDebugTestCpp": True, "functionName": "Trim_BG_RES_DIV", "lines": "3921-3987"},
})

# ---------------------------------------------------------------- TM600
items.append({
 "tm": "TM600",
 "symbol": "TM600_RDSON_TEST",
 "symbolHintFromPlan": "RDSON_TEST_HS",
 "overviewItem": "TM600",
 "name": "HS_RDSON",
 "level": "BUBO",
 "description": "high side powerfet rdson — Rds,on=(PMID-SW)/ISW with a floating high-current force and a differential Kelvin sense across PMID-SW",
 "testType": ["normal", "high-current", "differential"],
 "testTypeNote": "floating high-current force + differential Kelvin sense + force-sense (four-wire) discipline; MV&MI per the DFT",
 "baseline": "missing-from-debug-test.cpp",
 "channels": [
   {"role": "floating force (high current)", "pins": ["PMID (High)", "SW (Low)"], "sense": "force a current between PMID and SW; per the .sv sources SW carries iset[sw,1A]"},
   {"role": "differential Kelvin sense", "pins": ["PMID", "SW"], "sense": "MV of the differential pair that the force path shares (Kelvin) — see conflict C-01 for the FV/FI role assignment"},
   {"role": "supply", "pins": ["VBAT", "BST-SW", "VDRV"], "sense": "none"},
   {"role": "bootstrap rail", "pins": ["BST", "SW"], "sense": "BST-SW must stay ~5 V while the HS FET is forced on"},
 ],
 "stimuli": [
   S("vset", "vbat", 3.5, "V", "100e-6", 0, "reg_config/tm600.sv (DFT.csv says 4.2 V while also declaring pmid=15 V — see conflicts)"),
   S("vset", "pmid", 5.0, "V", "100e-6", 0, "reg_config/tm600.sv vsvPMID=5 V"),
   S("vset", "bst_sw", 5.0, "V", "1e-3", 0, "reg_config/tm600.sv: the BST-SW differential rail is held at 5 V"),
   S("vset", "vdrv", 5.0, "V", "100e-6", 0, "reg_config/tm600.sv"),
   S("en_tm", "(none)", None, None, None, None, "reg_config/tm600.sv entertestmode()"),
   S("field", "(none)", None, None, None, None, "reg_config/tm600.sv field[(WAKE_UP,1)] + field[(D2A_BUBO_EN_FORCE_ON,1),(D2A_BUBO_TM_DIS_CLK,1),(D2A_BUBO_TM_HSON,1)]"),
   S("delay", "(none)", None, None, "1e-3", None, "reg_config/tm600.sv after the register writes"),
   S("iset", "sw", 1.0, "A", "1e-3", 0, "reg_config/tm600.sv iset[sw,1,1e-3,0] — force 1 A; the DFT.csv equivalent is iset[pmid2sw,1,1e-3,0] (25% vs 50% of the DFT.csv load, see C-01)"),
   S("delay", "(none)", None, None, "2e-3", None, "reg_config/tm600.sv after the current is applied"),
 ],
 "measurements": [
   M("MV", "PMID-SW", "V", "differential voltage across the high-side FET"),
   M("MI", "SW", "A", "current flowing through the high-side FET (R-VIR: RON must use measured V and measured I, not the programmed value)"),
   M("MV", "BST_SW", "V", "floating-source compliance monitor named by OVERVIEW Check"),
 ],
 "limits": [
   L(unit="mΩ", expression="ExpectValue=11 (OVERVIEW, Test=direct, Special='Y / 2 FLOAT')", sourceRank=1,
     note="OVERVIEW is the DFT intent source and the meta source of record."),
   L(unit="mΩ", expression="DFT.csv record 19 ExpectValue=10 (unit string 'mohm')", sourceRank=2,
     note="10 vs 11 mΩ — conflict C-01. No averaging or silent choice is permitted."),
 ],
 "sequence": [
   "Step 1 connect: floating-high-current + Kelvin pair relays, VBAT/BST-SW/VDRV caps, bootstrap pair held at 5 V",
   "Step 2 power on: VBAT=3.5 V, PMID=5 V, BST-SW=5 V, VDRV=5 V (BST must lead/swing with PMID so BST-SW stays positive)",
   "Step 3 registers: entertestmode(); WAKE_UP=1; D2A_BUBO_EN_FORCE_ON=1; D2A_BUBO_TM_DIS_CLK=1; D2A_BUBO_TM_HSON=1 (HS FET forced on); delay 1 ms",
   "Step 4 measure: apply iset 1 A into the PMID->SW loop, delay 2 ms, measure the differential V(PMID-SW) and the loop I, then RON = V/I x 1e3 mΩ",
   "Step 5 power down: keep the FET on while BST and PMID ramp down together (BST always leading by ~5 V); unified RELAY_OFF",
 ],
 "registerWritesFromOverview": [],
 "registerWritesFromRegConfig": [
   R("I2CWriteSameData", "0x10", "0x43", "WAKE_UP=1", "reg_config/tm600.sv (authoritative register sequence for TM600)"),
   R("I2CWriteSameData", "0x59", "0x20", "bit5=1", "reg_config/tm600.sv"),
   R("I2CWriteSameData", "0x5A", "0x02", "D2A_BUBO_TM_HSON=1 (HS FET on)", "reg_config/tm600.sv — CONFLICT C-03: DFT.csv writes 0x59=0x01 and 0x61=0x0B instead"),
   R("I2CWriteSameData", "0x61", "0x4B", "D2A_BUBO_EN_FORCE_ON=1 + D2A_BUBO_TM_DIS_CLK=1", "reg_config/tm600.sv — DFT.csv writes 0x61=0x0B here"),
 ],
 "highCurrentPlan": {
   "forceChannel": "floating current source between PMID and SW",
   "forceValue": "1 A (reg_config/tm600.sv iset[sw,1,1e-3,0]); DFT.csv alternative iset[pmid2sw,1,1e-3,0] — 25% vs 50% of the 4 A DFT.csv static operating point",
   "compliance": "UNKNOWN — neither tm600.sv nor the DFT sources state a clamp/compliance limit; the golden case uses SetClamp(50,50) = 50% x 1 V = 0.5 V (max measurable RON 500 mΩ). Must be fixed by t3/t4.",
   "thermalNote": "1 A pulses with a 2 ms settle; RON must be computed from measured V and I (R-VIR) and the pulse must stay short enough to avoid self-heating (L3-method/RDSON: 50-500 us pulses for characterisation).",
   "discharge": "No explicit discharge step exists in the DFT sources. Power-down must not leave the bootstrap capacitor charged above the FET's rails: ramp BST and PMID down together with BST leading, then drop VDRV, then unified RELAY_OFF (per the TM600 golden case).",
 },
 "variants": [],
 "evidence": [
   E_xlsx("OVERVIEW", "row 132 (Item=TM600, ExpectValue=11, Unit=mΩ, Test=direct, Special='Y 2 FLOAT', Notes='Rds,on=(PMID-SW)/ISW')",
          "OVERVIEW row 132 = spreadsheet row 132 (header on row 1); extracted via openpyxl"),
   E_csv("project/DALI/input/DFT.csv", 'dftcsv', 'CSV record 19 (Item=TM600, Function Name=RDSON_TEST, ShortName=HS_RDSON, ExpectValue=10, Unit=mohm, Type=MV&MI, Check=PMID-SW)'),
   E_csv("project/DALI/input/DFT_restored.csv", 'dftrestored', 'CSV record 19',
         'DFT_restored differs from DFT.csv: pmid=15 V, bst2sw=5 V, 0x58=0x00 + 0x10=0x43 + 0x59=0x01 + 0x61=0x0B, iset[pmid2sw,1,1e-3], ExpectValue=10, Unit=mΩ, Check=PMID-SW — see conflict C-05'),
   E_sv("tm600.sv", "full body: vbat=3.5/pmid=5/bst_sw=5/vdrv=5; 0x10=0x43; 0x59=0x20; 0x5A=0x02; 0x61=0x4B; delay 1e-3; iset[sw,1,1e-3]; delay 2e-3",
         'TM600 register sequence of record (matches the current BUBO bit map used by TM640/TM607-609)'),
   E_file("knowledge/references/L4-Golden-code/tm600-normal-highcurrent.cpp", 'golden600',
          'TM600_RDSON_TEST (139 lines)', 'golden case: staircase power-up with BST leading PMID by 5 V, FPVI floating force, SetClamp(50,50), RON = MVRET/MIRET x 1e3'),
   E_file("docs/PROGRESS.md", 'progress', 'lines 1106-1121 and 1182 and 1234',
          "TM600 HS_RDSON is recorded as an already produced test item with a floating high-current reference"),
   {'path': 'project/DALI/meta/dali_tm_meta.json', 'sha256': H['meta'],
    'locator': 'functions[*].functionName — search for TM600 returns 0 of 99 entries',
    'note': 'ABSENCE EVIDENCE: the derived registry has no TM600 entry'},
 ],
 "ambiguities": [
   "C-01: which physical pin carries the forced current (SW per tm600.sv vs PMID_SW per DFT.csv) and the role of the 2 FLOAT flag.",
   "C-03: two different register maps (tm600.sv vs DFT.csv).",
   "Control/compliance limit for the 1 A floating force is stated nowhere in the DFT sources.",
   "What 'Y / 2 FLOAT' in OVERVIEW Special means: two floating nodes, or a 2 A floating force? (10 WARN in the PROGRESS reference concern the FPVI/current-range choice, not the flag semantics.)",
 ],
 "confidence": "medium",
 "implementationState": {"presentInDebugTestCpp": False,
                         "note": "0 matches for TM600/RDSON in the 8878-line plaintext of ForCodexDebug/source/test.cpp; the highest DUT_API entries are TM1004-TM1100 then TM1205"},
})

# ---------------------------------------------------------------- TM601
items.append({
 "tm": "TM601",
 "symbol": "TM601_RDSON_TEST",
 "symbolHintFromPlan": "RDSON_TEST_LS",
 "overviewItem": "TM601",
 "name": "LS_RDSON",
 "level": "BUBO",
 "description": "low side powerfet rdson — Rds,on=(SW-PGND)/IPMID2SW with a floating force and differential Kelvin sense across the low-side FET",
 "testType": ["normal", "high-current", "differential"],
 "testTypeNote": "floating high-current force + differential Kelvin sense + force-sense (four-wire) discipline; MV&MI per the DFT",
 "baseline": "missing-from-debug-test.cpp",
 "channels": [
   {"role": "floating force (high current)", "pins": ["PMID (High)", "SW (Low)"], "sense": "reg_config/tm601.sv forces iset[pmid_sw,1,1e-3] between PMID and SW"},
   {"role": "differential Kelvin sense", "pins": ["SW", "PGND"], "sense": "MV of SW-PGND; the schematic owner must confirm the sense pair and its common-mode"},
   {"role": "supply", "pins": ["VBAT", "VDRV", "VBUS"], "sense": "none"},
 ],
 "stimuli": [
   S("vset", "vbat", 3.5, "V", "100e-6", 0, "reg_config/tm601.sv (DFT.csv says 4.2 V — conflict C-05)"),
   S("vset", "vdrv", 5.0, "V", "100e-6", 0, "reg_config/tm601.sv"),
   S("vset", "vbus", 5.0, "V", "100e-6", 0, "reg_config/tm601.sv (DFT.csv says pmid=9 V instead)"),
   S("en_tm", "(none)", None, None, None, None, "reg_config/tm601.sv entertestmode()"),
   S("field", "(none)", None, None, None, None, "reg_config/tm601.sv field[(WAKE_UP,1)] + field[(D2A_BUBO_EN_FORCE_ON,1),(D2A_BUBO_TM_DIS_CLK,1),(D2A_BUBO_TM_LSON,1)]"),
   S("delay", "(none)", None, None, "5e-3", None, "reg_config/tm601.sv delay 5e-3 before the current is applied (longer than TM600's 1 ms)"),
   S("iset", "pmid_sw", 1.0, "A", "1e-3", 0, "reg_config/tm601.sv iset[pmid_sw,1,1e-3,0]; DFT.csv instead uses iset[sw2pgnd,1,1e-6,0] (a 1 us ramp — see C-01/C-05)"),
   S("delay", "(none)", None, None, "2e-3", None, "reg_config/tm601.sv after the current is applied"),
 ],
 "measurements": [
   M("MV", "SW-PGND", "V", "differential voltage across the low-side FET"),
   M("MI", "PMID_SW", "A", "current through the low-side FET (R-VIR: use measured I, never the programmed value)"),
 ],
 "limits": [
   L(unit="mΩ", expression="ExpectValue=7.5 (OVERVIEW, Test=direct, no Special flag)", sourceRank=1,
     note="OVERVIEW/meta are the source of record."),
   L(unit="mΩ", expression="DFT.csv record 20 ExpectValue=8 (unit string 'mohm')", sourceRank=2,
     note="7.5 vs 8 mΩ — conflict C-01. No averaging or silent choice."),
 ],
 "sequence": [
   "Step 1 connect: floating force pair (PMID/SW) + Kelvin/SW-PGND sense pair + VBAT/VDRV caps",
   "Step 2 power on: VBAT=3.5 V, VDRV=5 V, VBUS=5 V",
   "Step 3 registers: entertestmode(); WAKE_UP=1; D2A_BUBO_EN_FORCE_ON=1; D2A_BUBO_TM_DIS_CLK=1; D2A_BUBO_TM_LSON=1 (LS FET forced on); delay 5 ms",
   "Step 4 measure: apply iset 1 A, delay 2 ms, measure V(SW-PGND) and the loop current, then RON = V/I x 1e3 mΩ",
   "Step 5 power down: reverse-order ramp-down with FET conduction maintained, then unified RELAY_OFF",
 ],
 "registerWritesFromOverview": [],
 "registerWritesFromRegConfig": [
   R("I2CWriteSameData", "0x10", "0x43", "WAKE_UP=1", "reg_config/tm601.sv (authoritative register sequence for TM601)"),
   R("I2CWriteSameData", "0x59", "0x20", "bit5=1", "reg_config/tm601.sv"),
   R("I2CWriteSameData", "0x5A", "0x01", "D2A_BUBO_TM_LSON=1 (LS FET on)", "reg_config/tm601.sv — CONFLICT C-03: DFT.csv writes 0x59=0x02 and 0x61=0x0B"),
   R("I2CWriteSameData", "0x61", "0x4B", "D2A_BUBO_EN_FORCE_ON=1 + D2A_BUBO_TM_DIS_CLK=1", "reg_config/tm601.sv"),
 ],
 "highCurrentPlan": {
   "forceChannel": "floating current source between PMID and SW, with the low-side FET forced on so the current returns through SW-PGND",
   "forceValue": "1 A (reg_config/tm601.sv iset[pmid_sw,1,1e-3]); DFT.csv alternative iset[sw2pgnd,1,1e-6]",
   "compliance": "UNKNOWN — no clamp/compliance value in tm601.sv or the DFT sources. t3/t4 must fix it.",
   "thermalNote": "LS-only conduction raises the die temperature more than the HS case for the same current; keep the pulse short (the golden discipline is a 2 ms settle at most) and compute RON from measured V and I.",
   "discharge": "No explicit discharge step in the DFT sources; the low-side FET must remain on while the sources are ramped down so SW does not float above VBUS.",
 },
 "variants": [],
 "evidence": [
   E_xlsx("OVERVIEW", "row 133 (Item=TM601, ExpectValue=7.5, Unit=mΩ, Test=direct, Notes='Rds,on=(SW-PGND)/IPMID2SW')"),
   E_csv("project/DALI/input/DFT.csv", 'dftcsv', 'CSV record 20 (Item=TM601, ShortName=LS_RDSON, ExpectValue=8, Unit=mohm, Type=MV&MI, Check=PGND-SW, Dynamic=iset[sw2pgnd,1,1e-6,0])'),
   E_csv("project/DALI/input/DFT_restored.csv", 'dftrestored', 'CSV record 20',
         'DFT_restored differs: pmid=9 V, 0x10=0x43 + 0x58=0x20 + 0x59=0x02 + 0x61=0x0B, iset[sw2pgnd,1,1e-6], ExpectValue=8, Unit=mΩ, Check=PGND-SW — see conflict C-05'),
   E_sv("tm601.sv", "full body: vbat=3.5/vdrv=5/vbus=5; 0x10=0x43; 0x59=0x20; 0x5A=0x01; 0x61=0x4B; delay 5e-3; iset[pmid_sw,1,1e-3]; delay 2e-3"),
   E_file("knowledge/references/L4-Golden-code/tm600-normal-highcurrent.cpp", 'golden600',
          'TM600_RDSON_TEST (139 lines)',
          'structure/golden for the force path; there is NO dedicated TM601/LS golden case in the knowledge tree (param_type_index.md records the TM601_LS_RDSON process draft as archived and non-golden)'),
   E_testcpp("(nearest sibling) TM640_BOOST_HS_OCP / TM607_BUCK_LS_ZCD", "(LS-side precedent, lines ~7503-7590 and the LS_ZCD golden)"),
   {'path': 'project/DALI/meta/dali_tm_meta.json', 'sha256': H['meta'],
    'locator': 'functions[*].functionName — search for TM601 returns 0 of 99 entries (TM607/TM608/TM609 are present)',
    'note': 'ABSENCE EVIDENCE: the derived registry has no TM601 entry'},
 ],
 "ambiguities": [
   "The sense and force pins disagree across sources: OVERVIEW 'SW-PGND / IPMID2SW', DFT.csv 'PGND-SW / iset[sw2pgnd]', reg_config/tm601.sv 'iset[pmid_sw]'. Resolve with the schematic owner (t2) before implementation.",
   "DFT.csv's LS row states the HSON field name and PGND-SW check (i.e. HS semantics) while asserting a low-side measurement — the row is self-contradictory.",
   "No LS golden case exists; TM601 must be derived from the TM600 golden with the LS topology, which requires the t2 schematic facts for the SW/PGND sense pair.",
   "Compliance/clamp value unknown (same as TM600).",
 ],
 "confidence": "medium",
 "implementationState": {"presentInDebugTestCpp": False, "note": "0 matches for TM601/RDSON in the plaintext of ForCodexDebug/source/test.cpp"},
})

# ---------------------------------------------------------------- TM1205
items.append({
 "tm": "TM1205",
 "symbol": "TM1205_TRX_BST_UV_GD",
 "symbolHint": "TM1205_TRX_BST_UV_GD",
 "overviewItem": "TM1205",
 "name": "TRX_BST_UV_GD",
 "level": "TRX",
 "description": "Test BST1-SW1 and BST2-SW2 UVLO thresholds (two floating differential pairs sharing one floating source, time-multiplexed)",
 "testType": ["toggle", "differential", "awg", "grouped"],
 "testTypeNote": "bootstrap BST-SW differential pair threshold (AWG dual sweep, negative domain) with two time-multiplexed paths sharing one floating source; the 'grouped' tag marks the two-path identity",
 "channels": [
   {"role": "supply", "pins": ["VBAT"], "sense": "none"},
   {"role": "floating differential ramp (path 1)", "pins": ["SW1 (High)", "BST1 (Low)"], "sense": "one floating channel across BST1-SW1; output is V(SW1)-V(BST1) = -|BST1-SW1|"},
   {"role": "floating differential ramp (path 2)", "pins": ["SW2 (High)", "BST2 (Low)"], "sense": "same floating channel re-routed to BST2-SW2"},
   {"role": "observer", "pins": ["DTEST0 -> nQON pad"], "sense": "logic toggle with K65_nQON_PU pull-up; DMUX_SEL 57 selects path 1, 58 selects path 2"},
 ],
 "stimuli": [
   S("vset", "vbat", 4.0, "V", "100e-6", 0, "OVERVIEW Code1 / reg_config/tm1205.sv"),
   S("ramp_up", "bst1_sw1", 4.0, "V", "1000e-6", 0, "OVERVIEW Code2 vset[bst1_sw1,4,1000e-6,0] — the modelled ramp is 4 V over 1 ms"),
   S("ramp_down", "bst1_sw1", 0.0, "V", "1000e-6", 0, "OVERVIEW Code2 vset[bst1_sw1,0,1000e-6,0]"),
   S("ramp_up", "bst2_sw2", 4.0, "V", "1000e-6", 0, "OVERVIEW Code2"),
   S("ramp_down", "bst2_sw2", 0.0, "V", "1000e-6", 0, "OVERVIEW Code2"),
   S("field_renew", "(none)", None, None, None, None, "Code1: wake_up=1 (twice) + field_renew[(D2A_OVRD_SEL,47),(ovrd_value,3)] + (D2A_OVRD_SEL,45),(3) + (D2A_OVRD_SEL,48),(3) + D2A_TRX_TM_BOOTGD_DEG_BYPASS=1; delay 1e-3"),
   S("field_renew", "(none)", None, None, None, None, "Code2: DMUX_EN=1 with DMUX_SEL=57 (path 1) then DMUX_SEL=58 (path 2)"),
 ],
 "measurements": [
   M("MV", "DTEST0", "V", "release and UVLO-trigger thresholds for BST1-SW1 and BST2-SW2; six parameters: BST1_UV_Rise/_Fall/_Hys and BST2_UV_Rise/_Fall/_Hys"),
 ],
 "limits": [L(unit="V", expression="OVERVIEW ExpectValue is EMPTY", sourceRank=1,
              note="No numeric limit exists for TM1205 in any DFT source (OVERVIEW, DFT.csv, meta all blank). The item name TRX_BST_UV_GD says 'UV', so the limits must come from the datasheet/spec — recorded as an open question.")],
 "sequence": [
   "cbite.SetOn(path-1 floating-pair relays + K13_VBAT_Cap + K65_nQON_PU, -1); delay 3 ms (BST-SW differential caps must NOT be closed: they would slow the ramp)",
   "floating source level 0, then VBAT=4 V on",
   "entertestmode(); WAKE_UP=1; D2A_OVRD_SEL 47/45/48 = 3; BOOTGD_DEG_BYPASS=1; delay 1 ms",
   "path 1: DMUX_SEL=57; rampv_capv 0 -> -4 V (BST1-SW1 0->4 V, TRIG_FALLING captures release) and -4 -> 0 V (4->0 V, TRIG_RISING captures the UVLO trigger); rise/fall = fabs(value); hys x1e3",
   "re-route with a second cbite.SetOn(...) for path 2, delay 3 ms, then DMUX_SEL=58 and repeat the dual sweep",
   "floating source back to 0, then power down with unified RELAY_OFF",
 ],
 "registerWritesFromOverview": [],
 "registerWritesFromRegConfig": [
   R("I2CWriteSameData", "0x10", "0x43", "wake_up=1", "reg_config/tm1205.sv"),
   R("I2CWriteSameData", "0x67", "0x2F", "D2A_OVRD_SEL=47", "reg_config/tm1205.sv"),
   R("I2CWriteSameData", "0x68", "0x30", "ovrd_value=3", "reg_config/tm1205.sv"),
   R("I2CWriteSameData", "0x67", "0x2D", "D2A_OVRD_SEL=45", "reg_config/tm1205.sv"),
   R("I2CWriteSameData", "0x68", "0x30", "ovrd_value=3", "reg_config/tm1205.sv"),
   R("I2CWriteSameData", "0x67", "0x30", "D2A_OVRD_SEL=48", "reg_config/tm1205.sv"),
   R("I2CWriteSameData", "0x68", "0x30", "ovrd_value=3", "reg_config/tm1205.sv"),
   R("I2CWriteSameData", "0x5C", "0x02", "D2A_TRX_TM_BOOTGD_DEG_BYPASS=1", "reg_config/tm1205.sv"),
   R("I2CWriteSameData", "0x56", "0x39", "DMUX_SEL=57 (path 1 BST1-SW1)", "reg_config/tm1205.sv"),
   R("I2CWriteSameData", "0x57", "0x08", "DMUX_EN=1", "reg_config/tm1205.sv"),
   R("I2CWriteSameData", "0x56", "0x3A", "DMUX_SEL=58 (path 2 BST2-SW2)", "reg_config/tm1205.sv"),
 ],
 "variants": [],
 "evidence": [
   E_xlsx("OVERVIEW", "row 241 (Item=TM1205, Level=TRX, Name=TRX_BST_UV_GD, Code1/Code2/Code3 carrying the OVRD and DMUX sequences)"),
   E_csv("project/DALI/input/DFT.csv", 'dftcsv', 'no TM1205 record exists in DFT.csv'),
   E_sv("tm1205.sv", "full body: vbat=4V; 0x10=0x43; 0x67/0x68 OVRD triples; 0x5C=0x02; 0x56=0x39 + 0x57=0x08; bst1_sw1 4V then 0V; 0x56=0x3A + 0x57=0x08; bst2_sw2 4V then 0V"),
   E_file("knowledge/references/L4-Golden-code/TM1205_TRX_BST_UV_GD.cpp", 'golden1205',
          'DUT_API TM1205_TRX_BST_UV_GD (112 lines)', 'dedicated golden case: negative-domain dual sweep, fabs() restore, per-path SetOn, DMUX re-select order'),
   E_file("knowledge/references/param_type_index.md", 'pmi',
          'RDSON row + the note that TM601_LS_RDSON is an archived non-golden process draft',
          'cited to establish that NO dedicated TM601 golden case exists'),
   E_meta("TM1205_TRX_BST_UV_GD"),
   E_testcpp("TM1205_TRX_BST_UV_GD", "(lines 8752-8877)"),
 ],
 "ambiguities": [
   "No ExpectValue or tolerance for TM1205 exists in OVERVIEW, DFT.csv or meta (all blank): the limits must come from an external spec that this workspace does not contain.",
   "OVERVIEW expresses the stimulus as a single-ended vset on bst1_sw1/bst2_sw2 (4 V / 1 ms) while the implementation and the golden case use one floating channel across each BST-SW pair in the negative domain; the two are electrically equivalent only if the source is floating.",
   "The 4 V ramp target is not stated as a threshold, only as a scan range.",
 ],
 "confidence": "high",
 "implementationState": {"presentInDebugTestCpp": True, "functionName": "TM1205_TRX_BST_UV_GD", "lines": "8752-8877"},
})

artifact = {
 "runId": RUN,
 "generatedAt": datetime.datetime.now().astimezone().isoformat(timespec='seconds'),
 "producedBy": "dft-expert (t1)",
 "scope": ["TM000", "TM001", "TM102", "TM103", "TM108", "TM109", "TM135", "TM600", "TM601", "TM1205"],
 "scopeNote": "Ten accepted TM bases. TM000_1, TM001_2, TM001_3, TM108_1 are grouped variants sharing a base and are recorded under items[].variants, not as separate scope entries.",
 "source": {
   "path": "project/DALI/Dali_testmode.xlsx",
   "sha256": H['xlsx'],
   "locator": "sheet=OVERVIEW rows 2-251 (header row 1); 14 in-scope rows for the 10 TM bases",
   "role": "authoritative DFT intent source of record; every consequential field below cites this sheet plus at least one corroborating source",
   "readPath": "python byte mode (DLP/TSZ-authorized plaintext); PowerShell Get-Content and grep only see ciphertext",
   "columnHeaders": ["Item", "Level", "Name", "Description", "ExpectValue", "Unit", "Test", "Special", "Purpose", "Trim", "Notes", "Code1", "Code2", "Code3", "Power", "Dynamic", "Check", "isCodeGen", "isRun", "Assign", "State AMS Validation", "State Bench Validation", "is CP test?", "CP comment", "State ATE Validation", "HELPER"],
   "sourceRanking": ["OVERVIEW (Dali_testmode.xlsx)", "per-TM reg_config/*.sv", "DFT.csv", "DFT_restored.csv", "dali_tm_meta.json (derived)", "D:/PROJECT6-DALI/ForCodexDebug/source/test.cpp (existing implementation)"],
   "secondaryIntentSource": {
     "path": "project/DALI/input/DFT.csv",
     "sha256": H['dftcsv'],
     "locator": "RFC4180 parse, 35 records (cells contain embedded newlines); header Item,Function Name,ShortName,ExpectValue,Unit,Trim,Record,Hardware_initial,Software_initial,Dynamic,Check,Type",
     "note": "row-per-TM variant of the same intent layer; conflicts with OVERVIEW are recorded in blockingDecisions",
   },
   "tertiarySources": [
     {"path": "project/DALI/input/DFT_restored.csv", "sha256": H['dftrestored'], "locator": "35 records",
      "note": "recovered copy of DFT.csv; differs from DFT.csv in the TM600/TM601 rows (size 16824 vs 16862 bytes)"},
     {"path": "project/DALI/meta/dali_tm_meta.json", "sha256": H['meta'], "locator": "99 functions",
      "note": "derived registry generated from OVERVIEW by gen_testitems_meta.py (corroborating only); contains no TM600/TM601 entry"},
     {"path": "D:/PROJECT6-DALI/ForCodexDebug/source/test.cpp", "sha256": H['testcpp'], "locator": "8878 lines; 105 DUT_API definitions",
      "note": "current implementation in the only writable tree; used here only as evidence of what already exists"},
     {"path": "docs/PROGRESS.md", "sha256": H['progress'], "locator": "TM600 sections (lines 1106-1121, 1182, 1234)",
      "note": "project history; records TM600 HS_RDSON as previously produced with a floating high-current path"},
     {"path": "knowledge/references/L4-Golden-code/tm600-normal-highcurrent.cpp", "sha256": H['golden600'],
      "locator": "DUT_API TM600_RDSON_TEST (139 lines)",
      "note": "declared unique correct TM600 case (param_type_index.md); the root-level TM600_*.cpp drafts and TM601_LS_RDSON.cpp are archived as non-golden"},
     {"path": "knowledge/references/L4-Golden-code/TM1205_TRX_BST_UV_GD.cpp", "sha256": H['golden1205'],
      "locator": "DUT_API TM1205_TRX_BST_UV_GD (112 lines)", "note": "dedicated TM1205 golden case"},
     {"path": "knowledge/references/L4-Golden-code/TM1205_TRX_BST_UV_GD.md", "sha256": H['golden1205md'],
      "locator": "diff-pair role decomposition (§2 polarity, §3 ramp-source cap exclusion, §4 timing)",
      "note": "md companion of the TM1205 golden case; cited for the negative-domain polarity and the per-path re-SetOn rules"},
   ],
   "readOutputs": [
     {"path": "team/artifacts/%s/dft-raw/overview-dft.json" % RUN, "locator": "14 in-scope OVERVIEW rows + DFT.csv/DFT_restored records"},
     {"path": "team/artifacts/%s/dft-raw/overview-dump.txt" % RUN, "locator": "human-readable dump of the same"},
     {"path": "team/artifacts/%s/dft-raw/DFT-full.json" % RUN, "locator": "full RFC4180 parse of DFT.csv (35 records)"},
     {"path": "team/artifacts/%s/dft-raw/DFT_restored-full.json" % RUN, "locator": "full RFC4180 parse of DFT_restored.csv (35 records)"},
     {"path": "team/artifacts/%s/dft-raw/csv-full-dump.txt" % RUN, "locator": "human-readable CSV dump + cross-file diff notes"},
     {"path": "team/artifacts/%s/dft-raw/meta-scope.json" % RUN, "locator": "11 in-scope meta entries"},
     {"path": "team/artifacts/%s/dft-raw/regconfig-scope.json" % RUN, "locator": "15 reg_config .sv bodies used as evidence"},
     {"path": "team/artifacts/%s/dft-raw/source-refs.json" % RUN, "locator": "per-file reference hits for RDSON/TM600/TM601/TM1205/... in both trees"},
     {"path": "team/artifacts/%s/dft-raw/testcpp-blocks.txt" % RUN, "locator": "extracted implementation blocks for the 8 present TMs plus 3 'NOT FOUND' verdicts"},
     {"path": "team/artifacts/%s/dft-raw/compact-dump.txt" % RUN, "locator": "compact meta + reg_config + PROGRESS cross-check"},
   ],
   "method": [
     "OVERVIEW is treated as the DFT intent source of record; DFT.csv / DFT_restored.csv / meta are corroborating sources.",
     "Every disagreement is recorded verbatim in blockingDecisions/conflicts; nothing was averaged, no source was silently made to agree with another.",
     "Presence/absence of each TM in test.cpp was verified by regex over the DLP plaintext (105 DUT_API definitions).",
     "Hash convention: sha256 of the on-disk bytes read through the python (DLP-authorized) channel.",
   ],
 },
 "items": items,
 "conflicts": [
   {"id": "C-01", "severity": "blocker", "topic": "TM600/TM601 RDSON limit and force-path identity",
    "sources": [
      {"source": "OVERVIEW (Dali_testmode.xlsx) rows 132-133", "value": "TM600 HS_RDSON ExpectValue=11 mΩ, Special='Y / 2 FLOAT', Rds,on=(PMID-SW)/ISW; TM601 LS_RDSON ExpectValue=7.5 mΩ, Rds,on=(SW-PGND)/IPMID2SW"},
      {"source": "DFT.csv records 19-20", "value": "TM600 ExpectValue=10 mohm with iset[pmid2sw,1,1e-3] and Check=PMID-SW; TM601 ExpectValue=8 mohm with iset[sw2pgnd,1,1e-6] and Check=PGND-SW"},
      {"source": "reg_config/tm600.sv / tm601.sv", "value": "TM600 forces iset[sw,1,1e-3]; TM601 forces iset[pmid_sw,1,1e-3]"}
    ],
    "impact": "The limit feeding the spec file and the pins carrying/exposing the 1 A force are both unresolved; implementing either choice silently would invalidate the other source.",
    "requiredDecision": "User/Captain ruling: (a) which ExpectValue is the limit (OVERVIEW 11/7.5 mΩ or DFT.csv 10/8 mΩ), and (b) which source pins carry the forced current and the Kelvin sense.",
    "mergePolicy": "no-average, no-silent-choice (project rule)"},
   {"id": "C-02", "severity": "high", "topic": "TM108/TM109 VAC PRST rising threshold",
    "sources": [
      {"source": "OVERVIEW rows 15/17 + meta", "value": "rising vth 4.4 V, hys 0.35 V"},
      {"source": "DFT.csv records 9-10", "value": "rising vth 4.15 V, hys 0.35 V"}
    ],
    "impact": "250 mV (5.7%) limit difference on two toggle thresholds; also DFT.csv record 10 ramps VAC3 instead of VAC2.",
    "requiredDecision": "Confirm which threshold is the spec limit; confirm the DFT.csv TM109 row is a copy/paste artifact.",
    "mergePolicy": "OVERVIEW is primary (ranking: OVERVIEW > DFT.csv); DFT.csv value retained verbatim as sourceRank 2"},
   {"id": "C-03", "severity": "high", "topic": "TM600/TM601 register map divergence",
    "sources": [
      {"source": "reg_config/tm600.sv", "value": "0x10=0x43, 0x59=0x20, 0x5A=0x02, 0x61=0x4B, iset[sw,1]"},
      {"source": "reg_config/tm601.sv", "value": "0x10=0x43, 0x59=0x20, 0x5A=0x01, 0x61=0x4B, iset[pmid_sw,1]"},
      {"source": "DFT.csv record 19", "value": "0x58=0x00, 0x10=0x43, 0x59=0x01, 0x61=0x0B"},
      {"source": "DFT.csv record 20", "value": "0x10=0x43, 0x58=0x20, 0x59=0x02, 0x61=0x0B"}
    ],
    "impact": "Two different register encodings for the same two functions. The .sv files agree with the present BUBO bit map (0x5A holds the HSON/LSON bit) used by TM640/TM607-609, whereas the DFT.csv rows appear to use an older map. Writing the wrong pair would configure the opposite FET.",
    "requiredDecision": "t4/t5 must take reg_config/tm600.sv + tm601.sv as the register authority (they are the compiled AMS sequences for exactly these TMs) and record the DFT.csv values as superseded — or escalate to the DFT owner if the CSV is claimed to be newer.",
    "mergePolicy": "evidence-based ranking: per-TM reg_config .sv > DFT.csv prose"},
   {"id": "C-04", "severity": "medium", "topic": "TM108/TM109 DMUX_SEL value",
    "sources": [
      {"source": "OVERVIEW rows 15/17 + reg_config/tm108.sv / tm109.sv", "value": "DMUX_SEL=22 for VAC1, DMUX_SEL=21 for VAC2 (0x56=0x16 / 0x56=0x15)"},
      {"source": "DFT.csv records 9-10 comments", "value": "DTEST0_MUX=23 for TM108 and DTEST0_MUX=22 for TM109"}
    ],
    "impact": "Selecting the wrong internal MUX path measures a different comparator.",
    "requiredDecision": "t3/t4 to confirm the DTEST0/DMUX mux map against the ATEST/DTEST map sheets.",
    "mergePolicy": "per-TM reg_config .sv ranks above the DFT.csv comment"},
   {"id": "C-05", "severity": "medium", "topic": "DFT.csv vs DFT_restored.csv differ for TM600/TM601",
    "sources": [
      {"source": "DFT.csv records 19-20", "value": "TM600 pmid=15 V, bst2sw=5 V, 0x58=0x00, 0x59=0x01, 0x61=0x0B, iset[pmid2sw,1,1e-3], ExpectValue=10, Unit='mohm'"},
      {"source": "DFT_restored.csv records 19-20", "value": "TM600 pmid=15 V, bst2sw=5 V, 0x58=0x00, 0x59=0x01, 0x61=0x0B, iset[pmid2sw,1,1e-3], ExpectValue=10, Unit='mΩ' — and TM601 pmid=9 V, 0x58=0x20, 0x59=0x02, 0x61=0x0B, iset[sw2pgnd,1,1e-6], ExpectValue=8, Unit='mΩ'"}
    ],
    "impact": "The two CSVs are not identical (different sha256, different size); only the TM601 unit/format differs materially, but the file pair must not be treated as interchangeable since the byte-level difference is real.",
    "requiredDecision": "Record both; use DFT.csv for quoting unless a later ruling prefers the restored copy.",
    "mergePolicy": "no-silent-choice; both recorded"},
   {"id": "C-06", "severity": "medium", "topic": "VAC_PLUG module state in TM000 vs TM001",
    "sources": [
      {"source": "OVERVIEW rows 2-3 (TM000/TM000_1)", "value": "expects the VAC_PLUG module OFF (base, 22uA) and ON (variant, 31.5u)"},
      {"source": "OVERVIEW row 5 (TM001_2)", "value": "expects shipmode with en_tm[] + SHIPMODE_EN=1"},
      {"source": "test.cpp TM000_IQ_STANDBY", "value": "the VAC_PLUG ON/OFF state is produced by writing register 0x07 (bit map inferred, not source-backed); TM001's t est.cpp does not implement AC1_GATE_ON at all"},
      {"source": "test.cpp TM001_2_IQ_SHIPMODE", "value": "closes K21_VAC_Cap while reg_config/tm001_2.sv does not mention the cap relay"}
    ],
    "impact": "The APORT/VAC_PLUG enable bits and the TM001 AC1_GATE_ON bit have no DFT-source-backed register map; a wrong bit yields a wrong quiescent-current limit compliance.",
    "requiredDecision": "t3/t4 to obtain the register bit map, or formally record these as inferred and mark the corresponding implementation as READ-BACKED (not source-backed).",
    "mergePolicy": "declared inference"},
 ],
 "blockingDecisions": [
   {"id": "BD-01", "conflict": "C-01", "question": "Which RDSON ExpectValue is the spec limit: OVERVIEW 11 mΩ (TM600) / 7.5 mΩ (TM601), or DFT.csv 10 mΩ / 8 mΩ?",
    "status": "open", "impact": "spec limits for the two new test items", "owner": "Captain / user"},
   {"id": "BD-02", "conflict": "C-01", "question": "Which pins carry the 1 A floating force and the Kelvin differential sense for TM600 and TM601?",
    "status": "open", "impact": "relay/path selection and the measured differential pair", "owner": "schematic-expert (t2) then setup-architect (t3)"},
   {"id": "BD-03", "conflict": "C-03", "question": "Which register map is authoritative for TM600/TM601: reg_config/tm600.sv+tm601.sv (0x59=0x20, 0x5A=0x02/0x01, 0x61=0x4B) or the DFT.csv rows (0x58/0x59/0x61)?",
    "status": "open", "impact": "which FET is forced on — wrong choice measures the opposite device",
    "owner": "test-strategy-architect (t4) with DFT-owner confirmation"},
   {"id": "BD-04", "conflict": "C-02", "question": "TM108/TM109 rising threshold: 4.4 V (OVERVIEW) or 4.15 V (DFT.csv)?",
    "status": "open", "impact": "toggle limit compliance", "owner": "Captain / user"},
   {"id": "BD-05", "conflict": "(none)", "question": "What is the force compliance/clamp limit for the TM600/TM601 1 A floating force? No source states it (the golden case uses 50% x 1 V = 0.5 V).",
    "status": "open", "impact": "protection of a milliohm-level DUT path; RON upper measurable bound", "owner": "setup-architect (t3)"},
   {"id": "BD-06", "conflict": "(none)", "question": "TM1205 has no ExpectValue/tolerance in ANY DFT source. What are the BST1-SW1/BST2-SW2 UVLO limits?",
    "status": "open", "impact": "TM1205 cannot be judged pass/fail without an external spec", "owner": "Captain / user"},
   {"id": "BD-07", "conflict": "(none)", "question": "Is TM600's OVERVIEW Special='Y / 2 FLOAT' declaring two floating nodes or a 2 A floating force? (The .sv forces 1 A; the DFT.csv static operating point implies 4 A.)",
    "status": "open", "impact": "force magnitude and resource arbitration (a single floating source is scarce)", "owner": "Captain / user"},
 ],
 "openQuestions": [
   "BD-01..BD-07 above are unresolved; they are the questions that block a source-traceable plan.",
   "TM000: no reg_config/tm000.sv exists, so the APORT/VAC_PLUG enable bit map used by test.cpp is an inference.",
   "TM001: no reg_config/tm001.sv and no DFT.csv row; AC1_GATE_ON is an explicit TODO in test.cpp.",
   "TM102: the acceptance plan's symbolHint (TM102_HSKP_LP_ATEST0) and the OVERVIEW Name (LP_VBG_BF) disagree.",
   "TM103: three different register/observation stories (OVERVIEW+sv, DFT.csv AMUX row, current implementation).",
   "TM108/TM109: is the observation pin INT or DTEST0/nQON? DFT.csv says INT; OVERVIEW/implementation use DTEST0 via nQON.",
   "TM108_1: the DMO/A observation path has no dedicated DFT parameter list and no implementation; is it in scope?",
   "TM135: trim step count (8) comes from a test.cpp comment, not from a DFT source; the TReg/EFUSE definition was not consulted (out of this task's boundary).",
   "TM600/TM601: neither appears in dali_tm_meta.json (99 functions). Whether the meta registry must be regenerated for the gate to close is a separate, unresolved question raised by the implementer's recon note (team/artifacts/<run-id>/implementer-recon.md §5).",
   "No numeric tolerance exists in any DFT source for TM000, TM001, TM102, TM108, TM109, TM135 or TM1205 limits; spec values/tolerances live outside this workspace's DFT layer.",
 ],
 "verification": {
   "schemaValidation": "to be run with scripts/validate_team_artifact.py dft-ir <this file>",
   "coverageCheck": "scope has 10 entries; items has 10 entries; each item has >=1 evidence entry",
   "absentFromDebugTestCpp": ["TM600", "TM601"],
   "presentInDebugTestCpp": ["TM000", "TM001", "TM102", "TM103", "TM108", "TM109", "TM135", "TM1205"],
   "metaRegistryHasEntry": ["TM000", "TM001", "TM102", "TM103", "TM108", "TM109", "TM135", "TM1205"],
   "metaRegistryMissingEntry": ["TM600", "TM601"],
   "dftCsvHasRecord": ["TM000", "TM103", "TM108", "TM109", "TM600", "TM601"],
   "dftCsvMissingRecord": ["TM001", "TM102", "TM135", "TM1205"],
   "develVsDebugIdentical": {"test.cpp": True, "sha256": H['testcpp'],
                              "verified": "both trees hashed in this session and by the implementer's recon; devel was not modified"},
 },
}

path = os.path.join(ROOT, 'team', 'artifacts', RUN, 'dft-ir.json')
with open(path, 'w', encoding='utf-8') as f:
    json.dump(artifact, f, ensure_ascii=False, indent=1)
print('wrote', path, os.path.getsize(path), 'bytes')
print('items:', len(artifact['items']), [i['tm'] for i in artifact['items']])
print('sha256:', sha256_file(path))
