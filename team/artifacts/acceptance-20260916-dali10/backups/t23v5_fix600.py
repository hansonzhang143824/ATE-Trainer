import sys,io,os,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'implementation-payload-TM600-TM601.cpp')
u=open(p,'rb').read().decode('utf-8-sig').replace('\r\n','\n')
I=' '*8
old=('// F5 SIGN PREMISE: MVRET stays SIGNED (only MIRET is folded to a magnitude); with the derived\n'
 +I+'// -1 A command on TM601 the expected differential is negative, so a negative RDSON is the\n'
 +I+'// expected magnitude and a POSITIVE one is the polarity/fixture diagnostic.\n'
 +I+'// F5 DIVISION GUARD: dividing by a measured current of ~0 would yield inf/NaN and a bogus\n'
 +I+'// RDSON. The idiom follows existing project code (test.cpp:7884 if (iforce > 1e-6)) but uses a\n'
 +I+'// physically meaningful floor, not an epsilon: 0.1 A = 10% of the 1 A nominal force. The\n'
 +I+'// threshold is a PROVISIONAL engineering default (bench-signoff-required). Below the floor the\n'
 +I+'// item reports 0 mohm so an absent-force fault reads as zero current instead of inf/NaN.\n')
new=(I+'// F5 SIGN PREMISE (TM600 ONLY): this item forces the DFT literal +1 A with PMID on the HIGH\n'
 +I+'// terminal, so a correct measurement has BOTH MVRET and MIRET positive; the ratio is positive\n'
 +I+'// and is reported as a positive magnitude in mohm. (The derived -1 A case belongs to TM601 and\n'
 +I+'// is documented in that function only.)\n'
 +I+'// F5 DIVISION GUARD: dividing by a measured current of ~0 would yield inf/NaN and a bogus\n'
 +I+'// RDSON. The idiom follows existing project code (test.cpp:8087-8090) but uses a physically\n'
 +I+'// meaningful floor, not an epsilon: 0.1 A = 10% of the 1 A nominal force, a PROVISIONAL\n'
 +I+'// engineering default (bench-signoff-required). The failure path below reports ERROR_RES, NOT a\n'
 +I+'// zero or small value, so an absent-force or wrong-polarity condition fails closed.\n')
n=u.count(old); print('misplaced block found:',n)
if n==1:
    u=u.replace(old,new)
    open(p,'wb').write(b'\xef\xbb\xbf'+u.replace('\n','\r\n').encode('utf-8'))
r=open(p,'rb').read(); v=r.decode('utf-8-sig'); L=v.split('\n')
code=[l for l in L if not l.strip().startswith('//')]
print('payload %d B / %s'%(len(r),hashlib.sha256(r).hexdigest()))
s=[i for i,l in enumerate(L) if 'DUT_API int TM600_HS_RDSON' in l][0]
e=[i for i,l in enumerate(L) if 'DUT_API int TM601_LS_RDSON' in l][0]
print('TM600 block still mentions TM601:',[l.strip()[:80] for l in L[s:e] if 'TM601' in l and 'LS_RDSON' not in l])
print('invariants: delay_ms(1)=%d delay_ms(2)=%d SetClamp=%d MeasureVI=%d ramp=%d bare126=%d ERROR_RES=%d'%(
 sum(l.count('delay_ms(1)') for l in code),sum(l.count('delay_ms(2)') for l in code),
 sum(l.count('SetClamp(50, 50)') for l in code),sum(l.count('MeasureVI(200, 5, FPVIe_MV_X10)') for l in code),
 sum(l.count('rampi_capv')+l.count('rampv_capv') for l in code),
 sum(1 for l in code if ', 126,' in l),sum(l.count('ERROR_RES') for l in code)))
print('BOM',r[:3]==b'\xef\xbb\xbf','| loneLF',r.count(b'\n')-r.count(b'\r\n'))