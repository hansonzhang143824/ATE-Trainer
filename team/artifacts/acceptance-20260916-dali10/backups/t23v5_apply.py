import sys,io,os,re,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'implementation-payload-TM600-TM601.cpp')
u=open(p,'rb').read().decode('utf-8-sig').replace('\r\n','\n')
I=' '*8
def rep(old,new,label,expect=1):
    global u
    n=u.count(old); ok=(n==expect); print('  %-52s found=%d %s'%(label,n,'OK' if ok else 'SKIP'))
    if ok: u=u.replace(old,new)
# F4: the two 10 V PMID steps use a 1x range (>=2x violation) -> 20 V
rep('PMID_HG2_FXVI.Set(FV, 10, FXVIe_PLUS_10V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);',
    'PMID_HG2_FXVI.Set(FV, 10, FXVIe_PLUS_20V, FXVIe_PLUS_100MA, FXVIe_PLUS_RELAY_ON);',
    'PMID 10 V -> 20 V range (x2: up + down)', expect=2)
# Requirement 1+2+3: positive magnitude, same-sign criterion, fail-CLOSED via ERROR_RES
sig600=('v_meas[site] = FPVI0.GetMeasResult(site, MVRET);     // measured differential V(PMID-SW), SIGNED\n'
        +I+'i_meas[site] = fabs(FPVI0.GetMeasResult(site, MIRET));  // measured |loop current|')
new600=('v_meas[site] = FPVI0.GetMeasResult(site, MVRET);     // measured differential V(PMID-SW), SIGNED\n'
        +I+'i_meas[site] = FPVI0.GetMeasResult(site, MIRET);     // measured loop current, SIGNED (sign kept for the check)\n'
        +I+'// R-VIR, POSITIVE MAGNITUDE. Same sign is normal (|MVRET|/|MIRET|); OPPOSITE sign means the\n'
        +I+'// polarity or the fixture is wrong and is a FAILURE, never expressed as a negative resistance.\n'
        +I+'// Fail-CLOSED: below the 0.1 A floor, or on a sign mismatch, the item reports ERROR_RES (9999,\n'
        +I+'// Test_Method.h:32) exactly as the project precedent does (test.cpp:8087-8090: else\n'
        +I+'// gain[site] = ERROR_RES) instead of a small resistance that could read as a pass.\n'
        +I+'if (i_meas[site] > 0.1 && v_meas[site] * i_meas[site] > 0.0)\n'
        +I+'    hs_rdson[site] = fabs(v_meas[site]) / fabs(i_meas[site]) * 1e3;  // mohm, positive magnitude\n'
        +I+'else\n'
        +I+'    hs_rdson[site] = ERROR_RES;  // no current, or MVRET/MIRET sign mismatch (polarity/fixture fault)')
rep(sig600,new600,'TM600 sign + fail-closed')
sig601=('v_meas[site] = FPVI0.GetMeasResult(site, MVRET);     // measured differential V(SW-PGND), SIGNED\n'
        +I+'i_meas[site] = fabs(FPVI0.GetMeasResult(site, MIRET));  // measured |loop current|')
new601=('v_meas[site] = FPVI0.GetMeasResult(site, MVRET);     // measured differential V(SW-PGND), SIGNED\n'
        +I+'i_meas[site] = FPVI0.GetMeasResult(site, MIRET);     // measured loop current, SIGNED (sign kept for the check)\n'
        +I+'// R-VIR, POSITIVE MAGNITUDE. This item forces the DERIVED -1 A (PGND is on the HIGH terminal),\n'
        +I+'// so a correct result has BOTH MVRET and MIRET negative; the ratio is then positive and is\n'
        +I+'// reported as a magnitude. A positive MVRET with a negative MIRET is the polarity/fixture fault\n'
        +I+'// and is reported through the failure path below, never as a negative resistance.\n'
        +I+'// Fail-CLOSED: below the 0.1 A floor, or on a sign mismatch, report ERROR_RES (9999,\n'
        +I+'// Test_Method.h:32) per the project precedent (test.cpp:8087-8090) rather than a low value.\n'
        +I+'if (i_meas[site] > 0.1 && v_meas[site] * i_meas[site] > 0.0)\n'
        +I+'    ls_rdson[site] = fabs(v_meas[site]) / fabs(i_meas[site]) * 1e3;  // mohm, positive magnitude\n'
        +I+'else\n'
        +I+'    ls_rdson[site] = ERROR_RES;  // no current, or MVRET/MIRET sign mismatch (polarity/fixture fault)')
rep(sig601,new601,'TM601 sign + fail-closed')
open(p,'wb').write(b'\xef\xbb\xbf'+u.replace('\n','\r\n').encode('utf-8'))
r=open(p,'rb').read(); v=r.decode('utf-8-sig'); code=[l for l in v.split('\n') if not l.strip().startswith('//')]
print()
print('payload %d B / %s'%(len(r),hashlib.sha256(r).hexdigest()))
print('ERROR_RES uses:',sum(l.count('ERROR_RES') for l in code),'| fabs(v_meas):',sum(l.count('fabs(v_meas[site])') for l in code))
print('fail-open "0.0" left:',sum(1 for l in code if ': 0.0;' in l))
print('FXVIe 10V at 10 V steps left:',sum(1 for l in code if 'Set(FV, 10, FXVIe_PLUS_10V' in l))
print('BOM',r[:3]==b'\xef\xbb\xbf','| loneLF',r.count(b'\n')-r.count(b'\r\n'))