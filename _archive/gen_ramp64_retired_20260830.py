# -*- coding: utf-8 -*-
r"""
Generate the 64 ramp-capture functions (4 types x 4 ramp sources x 4 cap sources)
for the Test_Method library in this script's own directory.

Replaces the previous 16-function set. Reads the existing files (DLP plaintext via
python), splices in the generated declarations/bodies, writes back through python
so the DLP-encrypted .h stays encrypted for authorized readers.

Run:  python -X utf8 gen_ramp64.py
"""
import os

BASE = os.path.dirname(os.path.abspath(__file__))
H_PATH = os.path.join(BASE, 'Test_Method.h')
CPP_PATH = os.path.join(BASE, 'Test_Method.cpp')

CRLF = b'\r\n'
TAB = b'\t'


def b(txt):
    return txt.encode('ascii')


# name, VRNG, IRNG, RELAY  (order = declaration order per type)
SOURCES = [
    ('ACM200',      'ACM200_VRNG',      'ACM200_IRNG',      'ACM200_RELAY_ON'),
    ('FOVIe',       'FOVIe_VRNG',       'FOVIe_IRNG',       'FOVIe_RELAY_ON'),
    ('FXVIe_PLUS',  'FXVIe_PLUS_VRNG',  'FXVIe_PLUS_IRNG',  'FXVIe_PLUS_RELAY_ON'),
    ('FPVIe',       'FPVIe_VRNG',       'FPVIe_IRNG',       'FPVIe_RELAY_ON'),
]


def meas(dev, src):
    """MeasureVI call for a given source (device name cap_res / ramp_res)."""
    if src == 'ACM200':
        return f'{dev}.MeasureVI(samples, interval, MEAS_AWG)'
    if src == 'FOVIe':
        return f'{dev}.MeasureVI(samples, interval, FOVIe_MI_X1, MEAS_AWG)'
    if src == 'FXVIe_PLUS':
        return f'{dev}.MeasureVI(samples, interval, FXVIe_PLUS_MI_X1, MEAS_AWG)'
    if src == 'FPVIe':
        return f'{dev}.MeasureVI(samples, interval, FPVIe_MV_X1, FPVIe_MI_X1, MEAS_AWG)'
    raise ValueError(src)


# name, cap_fv(bool), ramp_mode(FV/FI), cap_mode(FI/FV), cap_val,
# trig(VTrig/ITrig), recover(bool), cap_ret, ramp_ret
TYPES = [
    dict(name='rampv_capv', cap_fv=False, ramp_mode='FV', cap_mode='FI', cap_val='0',
         trig='VTrig', recover=False, cap_ret='MVRET', ramp_ret='MVRET'),
    dict(name='rampv_capi', cap_fv=True,  ramp_mode='FV', cap_mode='FV', cap_val='cap_fv_value',
         trig='ITrig', recover=False, cap_ret='MIRET', ramp_ret='MVRET'),
    dict(name='rampi_capv', cap_fv=False, ramp_mode='FI', cap_mode='FI', cap_val='0',
         trig='VTrig', recover=True,  cap_ret='MVRET', ramp_ret='MIRET'),
    dict(name='rampi_capi', cap_fv=True,  ramp_mode='FI', cap_mode='FV', cap_val='cap_fv_value',
         trig='ITrig', recover=True,  cap_ret='MIRET', ramp_ret='MIRET'),
]


def param_list(t, RAMP, RVR, RIR, CAP, CVR, CIR):
    parts = [f'{RAMP} ramp_res', f'{RVR} ramp_vrange', f'{RIR} ramp_irange',
             f'{CAP} cap_res', f'{CVR} cap_vrange', f'{CIR} cap_irange']
    if t['cap_fv']:
        parts.append('double cap_fv_value')
    parts += ['double start_point', 'double stop_point', 'double step', 'int interval',
              'double trig_level', 'TRIG_MODE trig_mode', 'double *result']
    return ', '.join(parts)


def decl(t, RAMP, RVR, RIR, CAP, CVR, CIR):
    return b(f'BOOL {t["name"]}({param_list(t, RAMP, RVR, RIR, CAP, CVR, CIR)});')


def body(t, RAMP, RVR, RIR, CAP, CVR, CIR, RREL, CREL):
    L = []
    a = L.append
    a(b(f'BOOL Test_Method::{t["name"]}({param_list(t, RAMP, RVR, RIR, CAP, CVR, CIR)})'))
    a(b'{')
    a(TAB + b'if (interval < 10)\treturn FALSE;')
    a(TAB + b'if (step == 0)\treturn FALSE;')
    a(b'')
    a(TAB + b'int samples;')
    a(TAB + b'double pat[MAX_SAMPLES];')
    a(TAB + b'samples = (int)step;')
    if t['ramp_mode'] == 'FV':
        a(TAB + b(f'ramp_res.Set(FV, start_point, ramp_vrange, ramp_irange, {RREL});'))
    else:  # rampi: 3-step start on every ramp source
        a(TAB + b(f'ramp_res.Set(FV, 0, ramp_vrange, ramp_irange, {RREL});'))
        a(TAB + b(f'ramp_res.Set(FI, 0, ramp_vrange, ramp_irange, {RREL});'))
        a(TAB + b(f'ramp_res.Set(FI, start_point, ramp_vrange, ramp_irange, {RREL});// set start ramp point'))
    a(TAB + b(f'cap_res.Set({t["cap_mode"]}, {t["cap_val"]}, cap_vrange, cap_irange, {CREL});'))
    a(TAB + b'delay_ms(1);')
    a(TAB + b'STSAWGCreateRampData(&pat[0], samples, 1, start_point, stop_point);')
    a(TAB + b'ramp_res.AwgClear();')
    a(TAB + b(f'ramp_res.AwgLoader("awg", {t["ramp_mode"]}, ramp_vrange, ramp_irange, pat, samples);'))
    a(TAB + b'ramp_res.AwgSelect("awg", 0, samples - 1, samples - 1, interval);')
    a(TAB + b(f'cap_res.SetMeas{t["trig"]}(trig_level, trig_mode);'))
    a(b'')
    a(TAB + b'if (!START_DELAY)')
    a(TAB + TAB + b'delay_ms(START_DELAY);')
    a(b'')
    a(TAB + b(meas('ramp_res', RAMP)) + b';')
    a(TAB + b(meas('cap_res', CAP)) + b';')
    a(b'')
    a(TAB + b'STSEnableAWG(&ramp_res);')
    a(TAB + b'STSEnableMeas(&ramp_res, &cap_res);')
    if t['recover']:
        a(TAB + b'STSAWGRun();')
        a(TAB + b'//STSAWGRunTriggerStop(&cap_res, &ramp_res, &cap_res);')
    else:
        a(TAB + b'STSAWGRunTriggerStop(&cap_res, &ramp_res, &cap_res);')
    a(TAB + b'delay_us(TRIG_DELAY);')
    if t['recover']:
        a(TAB + b(f'ramp_res.Set(FI, 0, ramp_vrange, ramp_irange, {RREL});// current recover to 0A'))
    a(b'')
    a(TAB + b'int Trig_Point[SITE_NUM];')
    a(TAB + b'SERIAL{')
    a(TAB + TAB + b(f'Trig_Point[SITE] = (int)cap_res.GetMeasResult(SITE, {t["cap_ret"]}, TRIG_RESULT);'))
    a(TAB + TAB + b'if (((Trig_Point[SITE]) > 2) && ((Trig_Point[SITE]) < samples - 2)){')
    a(TAB + TAB + TAB + b(f'result[SITE] = ramp_res.GetMeasResult(SITE, {t["ramp_ret"]}, Trig_Point[SITE] - 1);'))
    a(TAB + TAB + b'}')
    a(TAB + TAB + b'else {')
    a(TAB + TAB + TAB + b'result[SITE] = ERROR_RES;')
    a(TAB + TAB + b'}')
    a(TAB + b'}')
    a(b'')
    a(TAB + b'return TRUE;')
    a(b'}')
    return CRLF.join(L)


# order: type -> ramp source -> cap source
all_decls = []
all_bodies = []
for t in TYPES:
    for RAMP, RVR, RIR, RREL in SOURCES:
        for CAP, CVR, CIR, CREL in SOURCES:
            all_decls.append(decl(t, RAMP, RVR, RIR, CAP, CVR, CIR))
            all_bodies.append(body(t, RAMP, RVR, RIR, CAP, CVR, CIR, RREL, CREL))

assert len(all_decls) == 64 and len(all_bodies) == 64, (len(all_decls), len(all_bodies))

# ---------------- assemble Test_Method.h ----------------
with open(H_PATH, 'rb') as f:
    orig_h = f.read()

c_start = orig_h.index(b'class Test_Method {')
r_start = orig_h.index(b'\tBOOL rampv_capv(')
c_end = orig_h.index(b'};', c_start)

h_pre = orig_h[:r_start]
h_post = orig_h[c_end:]

decl_block = b''
for d in all_decls:
    decl_block += TAB + d + CRLF

matrix_comment = (b'\t// ---- ramp capture library: 4 types x 4 ramp sources x 4 cap sources = 64 funcs ----\r\n'
                  b'\t// ---- rampv_*: FV ramp; rampi_*: FI ramp(3-step start); *_capv: FI=0 + VTrig; *_capi: FV=cap_fv_value + ITrig ----\r\n')

new_h = h_pre + matrix_comment + decl_block + h_post

with open(H_PATH, 'wb') as f:
    f.write(new_h)

# ---------------- assemble Test_Method.cpp ----------------
with open(CPP_PATH, 'rb') as f:
    orig_cpp = f.read()

m = orig_cpp.index(b'BOOL Test_Method::rampv_capv')
cpp_pre = orig_cpp[:m]

body_block = b''
for i, bd in enumerate(all_bodies):
    if i:
        body_block += CRLF + CRLF
    body_block += bd

new_cpp = cpp_pre.rstrip(CRLF) + CRLF + CRLF + body_block + CRLF

with open(CPP_PATH, 'wb') as f:
    f.write(new_cpp)

print('OK: 64 decls written to .h, 64 bodies written to .cpp')
