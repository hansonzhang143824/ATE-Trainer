import sys,io,os,json,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'implementation-manifest.json')
M=json.loads(open(p,'rb').read().decode('utf-8-sig'))
note=('Sampling choice, recorded because the frozen plan cannot be revised to state it precisely: the capture is MeasureVI(200, 5, '
 'FPVIe_MV_X10), i.e. 200 samples at a 5 us period = 1 ms. The count 200 is NOT golden-exclusive - the method library and the shared '
 'trim-measurement and board-check sources use a count of 200 but at a 10 us period (sub.cpp x4 and BoardCheck.cpp) - whereas the (200, 5) '
 'PAIR is golden-specific in this tree, because every TM-level call uses (50, 5). The 200-sample choice was made deliberately: heavier '
 'averaging for a 10 mV-class differential, and 200 x 5 us = 1 ms, which is what lets the 1 ms settle land the whole force at the 2 ms HARD CAP. '
 'It is correctness-neutral - it affects only noise and test time - and (50, 5) would be equally defensible on TM-level consistency grounds. '
 'No instrument/hardware validation is authorised, so this is a design disclosure, not a measured result.')
if not any('Sampling choice, recorded because' in x for x in M['limitations']):
    M['limitations'].append(note)
open(p,'wb').write((json.dumps(M,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
r=open(p,'rb').read()
print('manifest %d B / %s'%(len(r),hashlib.sha256(r).hexdigest()))
print('sampling note present:',any('Sampling choice, recorded because' in x for x in M['limitations']),'| limitations:',len(M['limitations']))