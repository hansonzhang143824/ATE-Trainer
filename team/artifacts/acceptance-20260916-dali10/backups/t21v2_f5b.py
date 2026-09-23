import sys,io,os,re,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'implementation-payload-TM600-TM601.cpp')
raw=open(p,'rb').read().decode('utf-8-sig')
u=raw.replace('\r\n','\n')
def rep(old,new,label,expect=1):
    global u
    n=u.count(old); ok=(n==expect)
    print('  %-54s found=%d %s'%(label,n,'OK' if ok else 'SKIP'))
    if ok: u=u.replace(old,new)
    return ok
o1='''    v_meas[site] = FPVI0.GetMeasResult(site, MVRET);     // measured differential V(PMID-SW)
    i_meas[site] = fabs(FPVI0.GetMeasResult(site, MIRET));  // measured loop current
    hs_rdson[site] = v_meas[site] / i_meas[site] * 1e3;  // mohm (R-VIR: measured / measured)'''
n1='''    // F5 SIGN PREMISE: MVRET is kept SIGNED (only MIRET is folded to a magnitude). With the
    // derived -1 A command on TM601 the differential is expected NEGATIVE, so a negative RDSON is
    // the expected magnitude and a POSITIVE one is the polarity/fixture diagnostic.
    // F5 DIVISION GUARD: dividing by a measured current of ~0 would yield inf/NaN and a bogus
    // RDSON. The guard follows the existing project idiom (test.cpp:7884, if (iforce > 1e-6)) but
    // uses a physically meaningful floor rather than an epsilon: 0.1 A = 10% of the 1 A nominal
    // force. The threshold is a PROVISIONAL engineering default, bench-signoff-required. Below the
    // floor the item reports 0 mohm, so an absent-force fault is visible as a zero-current
    // condition instead of a silent inf/NaN.
    v_meas[site] = FPVI0.GetMeasResult(site, MVRET);     // measured differential V(PMID-SW), SIGNED
    i_meas[site] = fabs(FPVI0.GetMeasResult(site, MIRET));  // measured |loop current|
    hs_rdson[site] = (i_meas[site] > 0.1) ? (v_meas[site] / i_meas[site] * 1e3) : 0.0;  // mohm'''
rep(o1,n1,'TM600 formula + guard')
o2='''    v_meas[site] = FPVI0.GetMeasResult(site, MVRET);     // measured differential V(SW-PGND)
    i_meas[site] = fabs(FPVI0.GetMeasResult(site, MIRET));  // measured loop current
    ls_rdson[site] = v_meas[site] / i_meas[site] * 1e3;  // mohm (R-VIR: measured / measured)'''
n2='''    // F5 SIGN PREMISE: MVRET stays SIGNED. TM601 forces the DERIVED -1 A (PGND sits on the HIGH
    // terminal), so the expected differential is NEGATIVE and the magnitude is therefore expected
    // to be negative; a POSITIVE reading is the polarity/fixture diagnostic, not success.
    // F5 DIVISION GUARD: same 0.1 A floor as TM600 (10% of nominal 1 A, PROVISIONAL,
    // bench-signoff-required). Below the floor the item reports 0 mohm so an absent-force fault is
    // visible as a zero-current condition rather than an inf/NaN RDSON.
    v_meas[site] = FPVI0.GetMeasResult(site, MVRET);     // measured differential V(SW-PGND), SIGNED
    i_meas[site] = fabs(FPVI0.GetMeasResult(site, MIRET));  // measured |loop current|
    ls_rdson[site] = (i_meas[site] > 0.1) ? (v_meas[site] / i_meas[site] * 1e3) : 0.0;  // mohm'''
rep(o2,n2,'TM601 formula + guard')
open(p,'wb').write(b'\xef\xbb\xbf'+u.replace('\n','\r\n').encode('utf-8'))
r=open(p,'rb').read(); v=r.decode('utf-8-sig'); code=[l for l in v.split('\n') if not l.strip().startswith('//')]
print()
print('payload %d B / %s'%(len(r),hashlib.sha256(r).hexdigest()))
print('guards:',sum(l.count('i_meas[site] > 0.1') for l in code),'| old unguarded divides left:',sum(1 for l in code if re.search(r'=\s*v_meas\[site\] / i_meas\[site\]',l)))
print('BOM',r[:3]==b'\xef\xbb\xbf','loneLF',r.count(b'\n')-r.count(b'\r\n'))