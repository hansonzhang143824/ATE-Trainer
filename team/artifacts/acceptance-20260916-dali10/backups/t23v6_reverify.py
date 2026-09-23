import sys,io,os,re,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'implementation-payload-TM600-TM601.cpp')
r=open(p,'rb').read(); u=r.decode('utf-8-sig'); L=u.split('\n')
code=[l for l in L if not l.strip().startswith('//')]
print('LIVE payload: %d B / %s'%(len(r),hashlib.sha256(r).hexdigest()))
print('(my last-turn value: 34788 B / f2e020bf64ab7384c9b547a8fd8a0f4cdda1b4595eed9a3d60a6bf3f9cbcc509)')
print()
print('F9-1 TM600 comment mentions TM601 inside TM600 function:')
s=[i for i,l in enumerate(L) if 'DUT_API int TM600_HS_RDSON' in l][0]
e=[i for i,l in enumerate(L) if 'DUT_API int TM601_LS_RDSON' in l][0]
hits=[(i+1,l.strip()[:110]) for i,l in enumerate(L[s:e],start=s) if 'TM601' in l and 'LS_RDSON' not in l]
print('   ',hits if hits else 'NONE')
print()
print('F9-2/3 formula lines:')
for i,l in enumerate(L):
    if 'rdson[site] =' in l or 'i_meas[site] > 0.1' in l: print('   %4d| %s'%(i+1,l.strip()[:125]))
print()
print('F9-3 ERROR_RES / 9999 in EXECUTABLE code:',sum(l.count('ERROR_RES') for l in code),sum(l.count('9999') for l in code))
print('.  ": 0.0" in executable code:',sum(1 for l in code if ': 0.0' in l))
print()
print('F9-4 range violations (FXVIe_PLUS_10V at non-zero):')
bad=[(i+1,l.strip()[:110]) for i,l in enumerate(code) if 'Set(FV,' in l and ', 0,' not in l and 'FPVIe_PLUS_10V' not in l and 'FXVIe_PLUS_10V' in l]
print('   ',bad if bad else 'NONE')
print()
print('K44/K45/K5 in executable code:',sum(l.count('K44_Cap_SW2_BST2')+l.count('K45_Cap_SW1_BST1')+l.count('K5_VBUS_Cap') for l in code))
print('inert-for-measurement string:',u.count('inert for the measurement'))
print('SETTLING IS NOT ANALYSED:',u.count('SETTLING IS NOT ANALYSED'))
print('BOM',r[:3]==b'\xef\xbb\xbf','| loneLF',r.count(b'\n')-r.count(b'\r\n'))