import sys,io,os,re,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'implementation-payload-TM600-TM601.cpp')
u=open(p,'rb').read().decode('utf-8-sig')
def rep(old,new,label,expect=1):
    global u
    n=u.count(old); ok=(n==expect)
    print('  %-56s found=%d %s'%(label,n,'OK' if ok else 'SKIP'))
    if ok: u=u.replace(old,new)
    return ok
# F4: ACM divider step 10 V -> 20 V range (both occurrences are the same 10 V staircase step,
# one on the way up and one on the way down: same setpoint, same minimum compliant range)
rep('SW12_U1REF_BST_ACM.Set(FV, 10, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);',
    'SW12_U1REF_BST_ACM.Set(FV, 10, ACM200_20V, ACM200_100MA, ACM200_RELAY_ON);',
    'ACM 10 V -> 20 V range (x2: up + down staircase)', expect=2)
# F5: division guard + sign premise, in both functions
old_formula='''    v_meas[site] = FPVI0.GetMeasResult(site, MVRET);     // measured differential V(PMID-SW)
    i_meas[site] = fabs(FPVI0.GetMeasResult(site, MIRET));  // measured loop current
    hs_rdson[site] = v_meas[site] / i_meas[site] * 1e3;  // mohm (R-VIR: measured / measured)'''
new_formula='''    // F5 SIGN PREMISE: MVRET is kept SIGNED (only MIRET is folded to a magnitude). With the
    // derived -1 A command on TM601 the differential is expected NEGATIVE; a negative RDSON is
    // therefore the expected magnitude, and a POSITIVE one is the polarity/fixture diagnostic.
    // F5 DIVISION GUARD: dividing by a measured current of ~0 would produce inf/NaN and a bogus
    // RDSON. The guard follows the existing project idiom (test.cpp:7884, if (iforce > 1e-6))
    // but uses a physically meaningful floor rather than an epsilon: 0.1 A = 10% of the 1 A
    // nominal force. The threshold is a PROVISIONAL engineering default, bench-signoff-required.
    // When the floor is not met LS_RDSON reports the measured current alone (0 mohm), which makes
    // an absent-magnitude fault unambiguous instead of silently emitting inf/NaN.
    v_meas[site] = FPVI0.GetMeasResult(site, MVRET);     // measured differential V(PMID-SW), SIGNED
    i_meas[site] = fabs(FPVI0.GetMeasResult(site, MIRET));  // measured |loop current|
    hs_rdson[site] = (i_meas[site] > 0.1) ? (v_meas[site] / i_meas[site] * 1e3) : 0.0;  // mohm'''
rep(old_formula,new_formula,'TM600 formula + guard + sign premise')
old601='''    v_meas[site] = FPVI0.GetMeasResult(site, MVRET);     // measured differential V(SW-PGND)
    i_meas[site] = fabs(FPVI0.GetMeasResult(site, MIRET));  // measured loop current
    ls_rdson[site] = v_meas[site] / i_meas[site] * 1e3;  // mohm (R-VIR: measured / measured)'''
new601='''    // F5 SIGN PREMISE: MVRET stays SIGNED. TM601 forces the DERIVED -1 A (PGND sits on the HIGH
    // terminal), so the expected differential is NEGATIVE and the RDSON magnitude is therefore
    // expected to be negative; a POSITIVE reading is the polarity/fixture diagnostic, not success.
    // F5 DIVISION GUARD: same 0.1 A floor as TM600 (10% of nominal 1 A, PROVISIONAL and
    // bench-signoff-required). Below the floor the item reports 0 mohm so that an absent-force
    // fault is visible as a zero-current condition rather than an inf/NaN RDSON.
    v_meas[site] = FPVI0.GetMeasResult(site, MVRET);     // measured differential V(SW-PGND), SIGNED
    i_meas[site] = fabs(FPVI0.GetMeasResult(site, MIRET));  // measured |loop current|
    ls_rdson[site] = (i_meas[site] > 0.1) ? (v_meas[site] / i_meas[site] * 1e3) : 0.0;  // mohm'''
rep(old601,new601,'TM601 formula + guard + sign premise')
open(p,'wb').write(b'\xef\xbb\xbf'+u.replace('\r\n','\n').replace('\n','\r\n').encode('utf-8'))
r=open(p,'rb').read(); v=r.decode('utf-8-sig'); code=[l for l in v.split('\n') if not l.strip().startswith('//')]
print()
print('payload %d B / %s'%(len(r),hashlib.sha256(r).hexdigest()))
print('guards in code:',sum(l.count('i_meas[site] > 0.1') for l in code))
print('ACM 10V at 10 V steps left:',sum(1 for l in code if 'Set(FV, 10, ACM200_10V' in l))
print('FXVIe 10V at 15/9 left:',sum(1 for l in code if re.search(r'Set\(FV, (15|9), FXVIe_PLUS_10V',l)))