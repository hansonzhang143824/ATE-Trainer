import sys,io,os,re,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'implementation-payload-TM600-TM601.cpp')
u=open(p,'rb').read().decode('utf-8-sig').replace('\r\n','\n')
I=' '*8
old=(I+'// F5 SIGN PREMISE (TM600 ONLY): this item forces the DFT literal +1 A with PMID on the HIGH\n'
 +I+'// terminal, so a correct measurement has BOTH MVRET and MIRET positive; the ratio is positive\n'
 +I+'// and is reported as a positive magnitude in mohm. (The derived -1 A case belongs to TM601 and\n'
 +I+'// is documented in that function only.)\n')
new=(I+'// F5 SIGN PREMISE (this function only): the force is the DFT literal +1 A with the high terminal\n'
 +I+'// on PMID, so a correct measurement has BOTH MVRET and MIRET positive; the ratio is positive and\n'
 +I+'// is reported as a positive magnitude in milliohm. The mirrored force direction used by the\n'
 +I+'// companion low-side item is described in that function alone, not here.\n')
n=u.count(old); print('TM600 comment block found:',n)
if n==1: u=u.replace(old,new)
# make the 9999 association literal and explicit in the executable-adjacent line
o2=I+'hs_rdson[site] = ERROR_RES;  // no current, or MVRET/MIRET sign mismatch (polarity/fixture fault)'
n2=(I+'hs_rdson[site] = ERROR_RES;  // ERROR_RES = 9999; no current (|I| <= 0.1 A), or an MVRET/MIRET\n'
    +I+'                             // sign mismatch, i.e. reverse polarity or a fixture fault')
print('TM600 ERROR_RES line found:',u.count(o2))
if u.count(o2)==1: u=u.replace(o2,n2)
o3=I+'ls_rdson[site] = ERROR_RES;  // no current, or MVRET/MIRET sign mismatch (polarity/fixture fault)'
n3=(I+'ls_rdson[site] = ERROR_RES;  // ERROR_RES = 9999; no current (|I| <= 0.1 A), or an MVRET/MIRET\n'
    +I+'                             // sign mismatch, i.e. reverse polarity or a fixture fault')
print('TM601 ERROR_RES line found:',u.count(o3))
if u.count(o3)==1: u=u.replace(o3,n3)
open(p,'wb').write(b'\xef\xbb\xbf'+u.replace('\n','\r\n').encode('utf-8'))
r=open(p,'rb').read(); v=r.decode('utf-8-sig'); L=v.split('\n')
s=[i for i,l in enumerate(L) if 'DUT_API int TM600_HS_RDSON' in l][0]
e=[i for i,l in enumerate(L) if 'DUT_API int TM601_LS_RDSON' in l][0]
print()
print('payload %d B / %s'%(len(r),hashlib.sha256(r).hexdigest()))
print('TM600 block mentions TM601 now:',[l.strip()[:90] for l in L[s:e] if 'TM601' in l and 'LS_RDSON' not in l] or 'NONE')
print('literal 9999 occurrences:',v.count('9999'))
print('ERROR_RES in executable code:',sum(1 for l in v.split('\n') if not l.strip().startswith('//') and 'ERROR_RES' in l))
print('BOM',r[:3]==b'\xef\xbb\xbf','| loneLF',r.count(b'\n')-r.count(b'\r\n'))