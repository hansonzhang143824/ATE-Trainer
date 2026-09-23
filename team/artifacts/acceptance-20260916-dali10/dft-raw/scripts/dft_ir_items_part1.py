# -*- coding: utf-8 -*-
"""Build team/artifacts/<run-id>/dft-ir.json (t1 deliverable) from extracted evidence.

Inputs are the raw extraction JSONs already written by the other _dft_* scripts
(single source of truth for hashes; this script re-reads the source files to hash them).
"""
import os, re, json, hashlib, sys, datetime
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

items = []

# ---------------------------------------------------------------- TM000
items.append({
 "tm": "TM000",
 "symbol": "TM000_IQ_STANDBY",
 "symbolHint": "TM000_IQ_STANDBY",
 "overviewItem": "TM000 (base) + TM000_1 (variant)",
 "name": "Iq_Standby",
 "level": "Top",
 "description": "Sleep Quiescent current, w/o VAC_PLUG module on (base) and w/i VAC_PLUG module on (variant)",
 "testType": ["normal", "grouped"],
 "testTypeNote": "low-current quiescent-current class; grouped identity = base TM000 + variant TM000_1",
 "channels": [{"role": "supply+measure", "pins": ["VBAT"], "sense": "MI (I(VBAT))"}],
 "stimuli": [
   S("vset", "vbat", 4.4, "V", "100e-6", 0, "OVERVIEW Code1; DFT.csv Hardware_initial agrees on 4.4 V, differs from meta 4.4 V (same)"),
   S("field", "(none)", None, None, None, None, "Code2: field[(VAC1_APORT_DET_ENABLE,0),(VAC2_APORT_DET_ENABLE,0),(VAC_SNK_DET_SEL,0)] for base; must be followed by an explicit register write (see variants)"),
   S("delay", "(none)", None, None, "10e-3", None, "Code3 delay[10e-3] before measuring I(VBAT)"),
 ],
 "measurements": [M("MI", "VBAT", "uA", "OVERVIEW Check=I(VBAT); per-site current after 10 ms settle")],
 "limits": [
   L(unit="uA", expression="ExpectValue='23 w/o digital iq.' (base, no numeric tolerance given)", sourceRank=1,
     note="OVERVIEW ExpectValue is prose with no tolerance; DFT.csv ExpectValue is EMPTY — no machine limit exists. 'de test' bench datapoint = 22uA (base) / 31.5u (variant); both are datapoints, not limits."),
 ],
 "sequence": [
   "cbite.SetOn(-1) (release; VBAT reaches the DUT through K8 default-NC)",
   "power VBAT (base: no VAC plug enabled; variant: VAC_PLUG module on)",
   "write the APORT detect register, delay 10 ms",
   "MeasureVI on VBAT, MI; log Iq_Standby / Iq_Standby_PLUG",
 ],
 "registerWritesFromOverview": [],
 "variants": [
   {"item": "TM000", "scopeKind": "base",
    "description": "Sleep Quiescent current w/o VAC_PLUG module on",
    "fieldDirective": "field[(VAC1_APORT_DET_ENABLE,0),(VAC2_APORT_DET_ENABLE,0),(VAC_SNK_DET_SEL,0)]",
    "benchDatapoint": "22uA", "expectValueProse": "23 w/o digital iq.",
    "implementationRegisterWrite": [R("I2CWriteSameData", "0x07", "0x00",
        "APORT all off", "bit map inferred in test.cpp and NOT confirmed against a reg_config file — TM000 has no reg_config/tm000.sv")],
    "evidence": [E_xlsx("OVERVIEW", "row 2 (Item=TM000)"),
                 E_csv("project/DALI/input/DFT.csv", 'dftcsv', 'CSV record 2 (Item=TM000, ShortName=IQ_Standby1_DSM)',
                       'DFT.csv uses a different short name (IQ_Standby1_DSM) and Check=VBAT/Type=MI'),
                 E_testcpp("TM000_IQ_STANDBY", "(lines 1350-1425)")]},
   {"item": "TM000_1", "scopeKind": "variant",
    "description": "Sleep Quiescent current w/i VAC_PLUG module on",
    "fieldDirective": "field[(VAC1_APORT_DET_ENABLE,1),(VAC2_APORT_DET_ENABLE,1),(VAC_SNK_DET_SEL,0)]",
    "benchDatapoint": "31.5u",
    "implementationRegisterWrite": [R("I2CWriteSameData", "0x07", "0x06", "bit1|bit2 APORT detect enable",
        "bit map inferred in test.cpp and NOT confirmed against a reg_config file")],
    "evidence": [E_xlsx("OVERVIEW", "row 3 (Item=TM000_1)"),
                 E_csv("project/DALI/input/DFT.csv", 'dftcsv', 'CSV record 3 (Item=TM000_1, ShortName=IQ_Standby2_DSM)'),
                 E_testcpp("TM000_IQ_STANDBY", "(merges TM000 and TM000_1 in one function, lines 1350-1425)")]},
 ],
 "groupedIdentity": "TM000_1 shares the TM000 base and is folded into the single function TM000_IQ_STANDBY (test.cpp:1350-1425). Parameter names: Iq_Standby, Iq_Standby_PLUG.",
 "evidence": [
   E_xlsx("OVERVIEW", "rows 2-3 (Item=TM000, TM000_1)"),
   E_csv("project/DALI/input/DFT.csv", 'dftcsv', 'CSV records 2-3', 'DFT.csv Hardware_initial is vbat=4.2 V while OVERVIEW is 4.4 V — see conflicts'),
   E_csv("project/DALI/input/DFT_restored.csv", 'dftrestored', 'CSV records 2-3 (identical to DFT.csv for TM000)'),
   E_meta("TM000_IQ_STANDBY"),
   E_testcpp("TM000_IQ_STANDBY", "(lines 1350-1425)"),
 ],
 "ambiguities": [
   "TM000 has no reg_config/*.sv file: the 0x07 bit map used by the current implementation (APORT enables) is an inference documented in the code, not a source fact.",
   "OVERVIEW 'ExpectValue' is prose ('23 w/o digital iq.') and DFT.csv leaves ExpectValue empty; no numeric limit with tolerance exists for this TM in any DFT source.",
   "Deterministic 'grouped' identity: TM000 == TM000_1 base+variant, but the DFT.csv names them IQ_Standby1_DSM / IQ_Standby2_DSM instead.",
 ],
 "confidence": "high",
 "implementationState": {"presentInDebugTestCpp": True, "functionName": "TM000_IQ_STANDBY", "lines": "1350-1425"},
})

# ---------------------------------------------------------------- TM001
items.append({
 "tm": "TM001",
 "symbol": "TM001_IIN_SUSPEND",
 "symbolHint": "TM001_IIN_SUSPEND",
 "overviewItem": "TM001 (base) + TM001_2 + TM001_3 (variants sharing the TM001 base)",
 "name": "Iin_Suspend",
 "level": "Top",
 "description": "Operation Quiescent current (base). TM001_2 = Shipmode Iq; TM001_3 = Iq_Operation (noted 'Covered by bench test.')",
 "testType": ["normal", "grouped"],
 "testTypeNote": "low-current quiescent-current class; grouped identity = base TM001 + variants TM001_2/TM001_3",
 "channels": [{"role": "supply+measure", "pins": ["VBAT"], "sense": "MI (I(VBAT))"},
              {"role": "supply", "pins": ["VAC1"], "sense": "not measured (variants only)"}],
 "stimuli": [
   S("vset", "vbat", 3.7, "V", "100e-6", 0, "OVERVIEW Code1"),
   S("en_tm", "(none)", None, None, None, None, "Code2 en_tm[] — entertestmode() before any register write"),
   S("field", "(none)", None, None, None, None, "Code2 field[(WAKE_UP,1),(AC1_GATE_ON,1)]"),
   S("delay", "(none)", None, None, "10e-3", None, "Code3 delay[10e-3] then '// Check IQ from VBAT'"),
 ],
 "measurements": [M("MI", "VBAT", "uA", "OVERVIEW Check=I(VBAT)")],
 "limits": [
   L(unit="uA", expression="no numeric limit in any DFT source; bench datapoint 'de test'=1.118mA (base)", sourceRank=1,
     note="OVERVIEW ExpectValue empty, DFT.csv ExpectValue empty. 1.118 mA is a bench datapoint. Note the unit inconsistency: OVERVIEW Unit=uA but the datapoint is 1.118 mA."),
 ],
 "sequence": [
   "cbite.SetOn(-1); VBAT supply",
   "entertestmode(); set WAKE_UP=1 (and AC1_GATE_ON=1 per DFT)",
   "delay 10 ms, MeasureVI(VBAT) MI",
 ],
 "registerWritesFromOverview": [],
 "variants": [
   {"item": "TM001", "scopeKind": "base", "description": "Operation Quiescent current",
    "fieldDirective": "field[(WAKE_UP,1),(AC1_GATE_ON,1)]",
    "implementationRegisterWrite": [R("I2CWriteSameData", "0x10", "0x43", "WAKE_UP=1",
                                        "test.cpp carries an explicit TODO: AC1_GATE_ON bit position is unknown and NOT written")],
    "evidence": [E_xlsx("OVERVIEW", "row 4 (Item=TM001)"), E_testcpp("TM001_IIN_SUSPEND", "(lines 1425-1478)")]},
   {"item": "TM001_2", "scopeKind": "variant", "description": "Shipmode iq.",
    "fieldDirective": "field[(SHIPMODE_EN,1)] then vset[vac1,0]; delay[60e-3]",
    "implementationRegisterWrite": [R("I2CWriteSameData", "0x29", "0x01", "SHIPMODE_EN=1",
                                        "matches reg_config/tm001_2.sv; test.cpp does NOT close K21_VAC_Cap (it opens it) — see conflicts")],
    "evidence": [E_xlsx("OVERVIEW", "row 5 (Item=TM001_2)"), E_sv("tm001_2.sv", "I2CWriteSameData(DEV_ADDR,0x29,0x01)"),
                 E_testcpp("TM001_2_IQ_SHIPMODE", "(lines 1478-1538)")]},
   {"item": "TM001_3", "scopeKind": "variant", "description": "Iq_Operation — OVERVIEW Notes: 'Covered by bench test.'",
    "fieldDirective": "(none in OVERVIEW)",
    "evidence": [E_xlsx("OVERVIEW", "row 6 (Item=TM001_3)"), E_testcpp("TM001_3_IQ_OPERATION", "(lines 1538-1591)")]},
 ],
 "groupedIdentity": "TM001_2 (Iq_Shipmode) and TM001_3 (Iq_Operation) share the TM001 base; the acceptance scope names only TM001, and there is no TM001_1 variant in OVERVIEW.",
 "evidence": [
   E_xlsx("OVERVIEW", "rows 4-6 (Item=TM001, TM001_2, TM001_3)"),
   E_csv("project/DALI/input/DFT.csv", 'dftcsv', 'no TM001 record exists in DFT.csv (35 records: TM000, TM000_1, TM100, TM101, TM103, TM105, TM106, TM108, TM109, ... )',
         'TM001 is in scope but has NO DFT.csv row — OVERVIEW is the only intent source'),
   E_meta("TM001_IIN_SUSPEND"), E_meta("TM001_2_IQ_SHIPMODE"), E_meta("TM001_3_IQ_OPERATION"),
   E_testcpp("TM001_IIN_SUSPEND", "(lines 1425-1478)"),
 ],
 "ambiguities": [
   "TM001 has no DFT.csv row and no reg_config/tm001.sv; the WAKE_UP register mapping is not source-backed.",
   "AC1_GATE_ON register/bit is an explicit open TODO inside test.cpp:1425-1478 (not resolved by any DFT source in this workspace).",
   "OVERVIEW Unit=uA but the only numeric bench datapoint is 1.118 mA.",
   "TM001_2's DFT.cfg (Code1 vset[vac1,5] with en_tm, Code2 SHIPMODE_EN then vset[vac1,0]) matches reg_config/tm001_2.sv, but the current test.cpp implementation instead closes K21_VAC_Cap — a possible divergence to confirm with the schematic owner.",
 ],
 "confidence": "medium",
 "implementationState": {"presentInDebugTestCpp": True, "functionName": "TM001_IIN_SUSPEND", "lines": "1425-1478"},
})

# ---------------------------------------------------------------- TM102
items.append({
 "tm": "TM102",
 "symbol": "TM102_HSKP_LP_ATEST0",
 "symbolHint": "TM102_HSKP_LP_ATEST0",
 "overviewItem": "TM102",
 "name": "LP_VBG_BF",
 "level": "HSKP",
 "description": "low power bg_buf (ATEST0 voltage measurement via VDM)",
 "testType": ["normal"],
 "channels": [{"role": "supply", "pins": ["VBAT"], "sense": "none"},
              {"role": "test-pad", "pins": ["VDM"], "sense": "MV (V(ATEST0) observed on the VDM pad, i.e. V(VDM))"}],
 "stimuli": [
   S("vset", "vbat", 4.0, "V", "100e-6", 0, "OVERVIEW Code1 / reg_config/tm102.sv / DFT.csv Hardware_initial (4.2 V in DFT.csv — see conflicts)"),
   S("vset", "vdm", 1.2, "V", "100e-6", 0, "Code2: pre-charge the external pad before connecting the DUT output (OVERVIEW Notes: weak drive capability, the external pin must be powered first)"),
   S("en_tm", "(none)", None, None, None, None, "Code2 en_tm[]"),
   S("field", "(none)", None, None, None, None, "Code2 field[(EN_ATEST0,1),(ATEST0_MUX,2)]"),
   S("vset_off", "vdm", None, None, None, None, "Code2 vset_off[vdm] — release VDM so the DUT drives the pad (FI=0 high-Z)"),
   S("delay", "(none)", None, None, "1e-3", None, "Code3 delay[1e-3]"),
 ],
 "measurements": [M("MV", "ATEST0", "V", "measured on the VDM pad after the source is released to high-Z")],
 "limits": [L(unit="V", expression="ExpectValue=1.27 (nominal, no tolerance given)", sourceRank=1,
              note="OVERVIEW ExpectValue=1.27 numeric; 'de test' bench datapoint = 1.178 V.")],
 "sequence": ["connect (K13_VBAT_Cap closed for a stable supply; VDM reaches the DUT through K59 default-NC)",
              "VBAT=4 V on",
              "entertestmode(); pre-charge VDM=1.2 V; EN_ATEST0=1 + ATEST0_MUX=2; release VDM (FI,0)",
              "delay 1 ms; MeasureVI; MVRET"],
 "registerWritesFromOverview": [
   R("I2CWriteSameData", "0x57", "0x02", "EN_ATEST0=1 (per reg_config/tm102.sv)"),
   R("I2CWriteSameData", "0x5E", "0x02", "ATEST0_MUX=2 -> LP_VBG_BF (per reg_config/tm102.sv)"),
 ],
 "variants": [],
 "evidence": [
   E_xlsx("OVERVIEW", "row 9 (Item=TM102)"),
   E_csv("project/DALI/input/DFT.csv", 'dftcsv', 'no TM102 record exists in DFT.csv (TM100/TM101/TM103 are present, TM102 is not)'),
   E_sv("tm102.sv", "ramp_vsrc_val(4,100e-6) / vdm=1.2V / 0x57=0x02 / 0x5E=0x02 / vset_off[vdm] / delay 1e-3"),
   E_meta("TM102_HSKP_LP_ATEST0"),
   E_testcpp("TM102_HSKP_LP_ATEST0", "(lines 1722-1785)"),
 ],
 "ambiguities": [
   "The acceptance-plan symbolHint is TM102_HSKP_LP_ATEST0 but the OVERVIEW Name is LP_VBG_BF (the parameter name used by test.cpp / meta is LP_VBG_BF). Symbol vs parameter naming must be fixed by the test-plan stage.",
   "OVERVIEW ExpectValue=1.27 V has no tolerance in any DFT source.",
 ],
 "confidence": "high",
 "implementationState": {"presentInDebugTestCpp": True, "functionName": "TM102_HSKP_LP_ATEST0", "lines": "1722-1785"},
})

# ---------------------------------------------------------------- TM103
items.append({
 "tm": "TM103",
 "symbol": "TM103_HSKP_LP_HR_0P5U",
 "symbolHint": "TM103_HSKP_LP_HR_0P5U",
 "overviewItem": "TM103",
 "name": "LP_HR_0P5U",
 "level": "HSKP",
 "description": "IBP 0.5UA HR (ATEST0 current measurement through the VDM force path)",
 "testType": ["normal"],
 "testTypeNote": "static MV on the ATEST0/VDM pad; ATEST-mux class",
 "channels": [{"role": "supply", "pins": ["VBAT"], "sense": "none"},
              {"role": "force+measure", "pins": ["VDM"], "sense": "MI (I(ATEST0) is measured as the current the VDM source must supply at 1 V)"}],
 "stimuli": [
   S("vset", "vbat", 4.0, "V", "100e-6", 0, "OVERVIEW Code1 / reg_config/tm103.sv (DFT.csv says 4.2 V — see conflicts)"),
   S("en_tm", "(none)", None, None, None, None, "Code2 en_tm[]"),
   S("field", "(none)", None, None, None, None, "Code2 field[(EN_ATEST0,1),(ATEST0_MUX,4)]"),
   S("vset", "vdm", 1.0, "V", "100e-6", 0, "Code2 vset[vdm,1] — VDM is the forcing pin; I(ATEST0) is the measured quantity"),
   S("delay", "(none)", None, None, "1e-3", None, "Code3 delay[1e-3]"),
 ],
 "measurements": [M("MI", "ATEST0", "uA", "I(VDM) == I(ATEST0); the forced voltage is 1 V and the measured current is the DUT's IBP_HR current")],
 "limits": [L(unit="uA", expression="ExpectValue=0.5", sourceRank=1,
              note="OVERVIEW 0.5 uA, DFT.csv 0.5 uA (agree); 'de test' bench datapoint 0.5uA. No tolerance given.")],
 "sequence": ["connect (K13_VBAT_Cap; VDM through K59 default-NC)",
              "VBAT=4 V on", "entertestmode(); EN_ATEST0=1 + ATEST0_MUX=4",
              "VDM=1 V FV, 10 uA range (smallest), MeasureVI -> MIRET", "power down in three steps"],
 "registerWritesFromOverview": [
   R("I2CWriteSameData", "0x57", "0x02", "EN_ATEST0=1 (per reg_config/tm103.sv)"),
   R("I2CWriteSameData", "0x5E", "0x04", "ATEST0_MUX=4 -> IBP_HR_0.5UA (per reg_config/tm103.sv)"),
 ],
 "variants": [],
 "evidence": [
   E_xlsx("OVERVIEW", "row 10 (Item=TM103)"),
   E_csv("project/DALI/input/DFT.csv", 'dftcsv', 'CSV record 6 (Item=TM103, ShortName=LP_HR_0P5U, ExpectValue=0.5, Unit=uA, Check=AMUX, Type=MI)',
         'DFT.csv says Hardware_initial vset[vbat,4.2] + vset[amux,1] and writes 0x56=0x22 for field[(EN_ATEST0,1),(ATEST0_MUX,4)] — a DIFFERENT register pair from reg_config/tm103.sv'),
   E_sv("tm103.sv", "vbat=4V / 0x57=0x02 / 0x5E=0x04 / vdm=1V / delay 1e-3"),
   E_meta("TM103_HSKP_LP_HR_0P5U"),
   E_testcpp("TM103_HSKP_LP_HR_0P5U", "(lines 1795-1853)"),
 ],
 "ambiguities": [
   "DFT.csv observes ATEST0 through an AMUX pin (vset[amux,1]) while OVERVIEW+reg_config observe it through VDM; the pin carrying ATEST0 is therefore source-dependent and must be settled by the schematic owner (t2/t3).",
   "DFT.csv's register directive 0x56=0x22 does not match reg_config/tm103.sv's 0x57=0x02 + 0x5E=0x04.",
 ],
 "confidence": "high",
 "implementationState": {"presentInDebugTestCpp": True, "functionName": "TM103_HSKP_LP_HR_0P5U", "lines": "1795-1853"},
})
print('part 1 built:', len(items))
globals()['_ITEMS'] = items
