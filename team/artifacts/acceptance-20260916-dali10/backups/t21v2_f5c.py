import sys,io,os,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'implementation-payload-TM600-TM601.cpp')
u=open(p,'rb').read().decode('utf-8-sig').replace('\r\n','\n')
I=' '*8
def rep(old,new,label,expect=1):
    global u
    n=u.count(old); ok=(n==expect); print('  %-46s found=%d %s'%(label,n,'OK' if ok else 'SKIP'))
    if ok: u=u.replace(old,new)
o1=(I+'v_meas[site] = FPVI0.GetMeasResult(site, MVRET);     // measured differential V(PMID-SW)\n'
    +I+'i_meas[site] = fabs(FPVI0.GetMeasResult(site, MIRET));  // measured loop current\n'
    +I+'hs_rdson[site] = v_meas[site] / i_meas[site] * 1e3;  // mohm (R-VIR: measured / measured)')
n1=(I+'// F5 SIGN PREMISE: MVRET stays SIGNED (only MIRET is folded to a magnitude); with the derived\n'
    +I+'// -1 A command on TM601 the expected differential is negative, so a negative RDSON is the\n'
    +I+'// expected magnitude and a POSITIVE one is the polarity/fixture diagnostic.\n'
    +I+'// F5 DIVISION GUARD: dividing by a measured current of ~0 would yield inf/NaN and a bogus\n'
    +I+'// RDSON. The idiom follows existing project code (test.cpp:7884 if (iforce > 1e-6)) but uses a\n'
    +I+'// physically meaningful floor, not an epsilon: 0.1 A = 10% of the 1 A nominal force. The\n'
    +I+'// threshold is a PROVISIONAL engineering default (bench-signoff-required). Below the floor the\n'
    +I+'// item reports 0 mohm so an absent-force fault reads as zero current instead of inf/NaN.\n'
    +I+'v_meas[site] = FPVI0.GetMeasResult(site, MVRET);     // measured differential V(PMID-SW), SIGNED\n'
    +I+'i_meas[site] = fabs(FPVI0.GetMeasResult(site, MIRET));  // measured |loop current|\n'
    +I+'hs_rdson[site] = (i_meas[site] > 0.1) ? (v_meas[site] / i_meas[site] * 1e3) : 0.0;  // mohm')
rep(o1,n1,'TM600 formula + guard + sign premise')
o2=(I+'v_meas[site] = FPVI0.GetMeasResult(site, MVRET);     // measured differential V(SW-PGND)\n'
    +I+'i_meas[site] = fabs(FPVI0.GetMeasResult(site, MIRET));  // measured loop current\n'
    +I+'ls_rdson[site] = v_meas[site] / i_meas[site] * 1e3;  // mohm (R-VIR: measured / measured)')
n2=(I+'// F5 SIGN PREMISE: MVRET stays SIGNED (only MIRET is folded). TM601 forces the DERIVED -1 A\n'
    +I+'// because PGND sits on the HIGH terminal, so the expected differential is negative and the\n'
    +I+'// magnitude is expected negative; a POSITIVE reading is the polarity/fixture diagnostic.\n'
    +I+'// F5 DIVISION GUARD: same 0.1 A floor as TM600 (10% of nominal 1 A, PROVISIONAL and\n'
    +I+'// bench-signoff-required). Below the floor the item reports 0 mohm so an absent-force fault\n'
    +I+'// reads as zero current rather than an inf/NaN RDSON.\n'
    +I+'v_meas[site] = FPVI0.GetMeasResult(site, MVRET);     // measured differential V(SW-PGND), SIGNED\n'
    +I+'i_meas[site] = fabs(FPVI0.GetMeasResult(site, MIRET));  // measured |loop current|\n'
    +I+'ls_rdson[site] = (i_meas[site] > 0.1) ? (v_meas[site] / i_meas[site] * 1e3) : 0.0;  // mohm')
rep(o2,n2,'TM601 formula + guard + sign premise')
open(p,'wb').write(b'\xef\xbb\xbf'+u.replace('\n','\r\n').encode('utf-8'))
r=open(p,'rb').read(); v=r.decode('utf-8-sig'); code=[l for l in v.split('\n') if not l.strip().startswith('//')]
print()
print('payload %d B / %s'%(len(r),hashlib.sha256(r).hexdigest()))
print('guards:',sum(l.count('i_meas[site] > 0.1') for l in code),'| unguarded divides left:',sum(1 for l in code if 'rdson[site] = v_meas' in l))
print('BOM',r[:3]==b'\xef\xbb\xbf','| loneLF',r.count(b'\n')-r.count(b'\r\n'))