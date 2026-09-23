import sys,io,os,re,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'implementation-payload-TM600-TM601.cpp')
u=open(p,'rb').read().decode('utf-8-sig').replace('\r\n','\n')
before=hashlib.sha256(open(p,'rb').read()).hexdigest()
old='    cbite.SetOn(K83_BUSH0_PMID, K60_BUSL0_VCP, K61_ACM8_SW, K109_BUSL1_PB0, K110_ACM18_BST, K13_VBAT_Cap, K85_CAP_PMID, K57_CAP_BST_SW, K126_V1P5_CAP, -1);'
n=u.count(old); print('TM600 SetOn matched:',n)
assert n==1
new=('    // t50: SetOn is EXCLUSIVE - it closes ONLY the relays listed here and releases every other relay\n'
 '    // (knowledge/sources/cbite-qtmue.md:80-81 "All unspecified pins are set OFF"; :92-93 the trap: two\n'
 '    // separate SetOn calls release the first one\'s closures; the DALI precedent is TM109/110, merged into a\n'
 '    // single call at :96). Therefore THIS single call IS the item\'s complete explicit closed set, and any\n'
 '    // relay the item needs must appear here - omitting one is not "leaving it alone", it forces it OFF.\n'
 '    // The defect corrected here was exactly that: the BST source leg (K48_ACM5_AMP_REF + K76_ACM_BST) was\n'
 '    // absent, so ch5 could only reach PB0/SW1/SW2 (SCH-Connect-Map.txt:775/:778) and never BST (:673).\n'
 '    // K46 is deliberately NOT added: it sits on the FPVIe0 high-side BUS path (the TM641/TM643 shape), not\n'
 '    // on the ACM200 ch5 source path. K49 and K110 need no explicit handling - after K48 energises, its\n'
 '    // COM moves to the NC contact that feeds K76, and the default throw feeding K49 is opened; K110 is\n'
 '    // released by exclusivity anyway (it is still listed below because this revision retains the pair).\n'
 '    cbite.SetOn(K83_BUSH0_PMID, K60_BUSL0_VCP, K61_ACM8_SW, K48_ACM5_AMP_REF, K76_ACM_BST, K109_BUSL1_PB0, K110_ACM18_BST, K13_VBAT_Cap, K85_CAP_PMID, K57_CAP_BST_SW, K126_V1P5_CAP, -1);')
u=u.replace(old,new)
open(p,'wb').write(b'\xef\xbb\xbf'+u.replace('\n','\r\n').encode('utf-8'))
r=open(p,'rb').read(); v=r.decode('utf-8-sig'); code=re.sub(r'//.*$','',v,flags=re.M)
L=v.split('\n')
print('payload %s -> %d B / %s'%(before[:12],len(r),hashlib.sha256(r).hexdigest()))
print()
print('=== invariants (proper strip) ===')
for k,exp in [('delay_ms(1)',6),('delay_ms(2)',0),('SetClamp(50, 50)',2),('MeasureVI(200, 5, FPVIe_MV_X10)',2),('K126_V1P5_CAP',2),('ERROR_RES',2),('K57_CAP_BST_SW',2),('K109_BUSL1_PB0',1),('K110_ACM18_BST',1)]:
    g=sum(l.count(k) for l in code.split('\n')); print('  %-32s %d (expect %d) %s'%(k,g,exp,'OK' if g==exp else 'MISMATCH'))
print('  K48=%d K76=%d K46=%d (K46 must be 0)'%(sum(l.count('K48_ACM5_AMP_REF') for l in code.split('\n')),sum(l.count('K76_ACM_BST') for l in code.split('\n')),sum(l.count('K46') for l in code.split('\n'))))
print('  SetOn calls total:',sum(l.count('cbite.SetOn(') for l in code.split('\n') if 'cbite.SetOn(' in l))
print('  BOM',r[:3]==b'\xef\xbb\xbf','loneLF',r.count(b'\n')-r.count(b'\r\n'))