import sys,io,os,re,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'implementation-payload-TM600-TM601.cpp')
r0=open(p,'rb').read(); h0=hashlib.sha256(r0).hexdigest()
print('OLD HASH (recorded): %s  (%d B)'%(h0,len(r0)))
u=r0.decode('utf-8-sig')
lines=u.split('\r\n') if '\r\n' in u else u.split('\n')
def idx(pred):
    return next(i for i,l in enumerate(lines) if pred(l))
i_t29=idx(lambda l:'// t29 FIX - BST EXCITATION PATH' in l)
i_t50=idx(lambda l:'// t50: SetOn is EXCLUSIVE' in l)
i_t43=idx(lambda l:'// t43 RULING (rule-reviewer' in l)
i_fin=idx(lambda l:'// t50 FINAL RULING (supersedes the union approach recorded above)' in l)
print('block indices: t29=%d t50=%d t43=%d final=%d'%(i_t29+1,i_t50+1,i_t43+1,i_fin+1))
# (a) prepend a SUPERSEDED marker to the t29 block, (b) to the t43 block
lines[i_t29]='    // [SUPERSEDED BY t50 - retained as history, NOT the operative rule] '+lines[i_t29].strip()
lines[i_t43]='    // [SUPERSEDED BY t50 FINAL RULING BELOW - retained as history, NOT the operative rule] '+lines[i_t43].strip()
# (c) insert the two-case operational fact immediately before the FINAL RULING block
op=['    // OPERATIONAL FACT (as instructed for t50; no mnemonic cited - knowledge/hardware/relays.md L31 is',
    '    // referenced 0 times here):',
    '    //   UN-ENERGISED: S5_ACM200_FH5 -> K48(Relay-NC) -> K49(Relay-NC) -> SW1_F/SW1_S',
    '    //                 (or K49(Relay-ON) -> SW2_F/SW2_S)   [SCH-Connect-Map.txt:775/:778]',
    '    //   K48 ENERGISED: S5_ACM200_FH5 -> K48(Relay-ON) -> K76(Relay-ON) -> BST_F/BST_S',
    '    //                 [SCH-Connect-Map.txt:673/:674]',
    '    // i.e. K48 is a steering relay for the ch5 source: un-actuated the source lands on the SW1/SW2',
    '    // phase nodes, actuated it is diverted to BST while the default SW1 path is broken.']
lines[i_fin:i_fin]=op
open(p,'wb').write(b'\xef\xbb\xbf'+'\r\n'.join(lines).encode('utf-8'))
r1=open(p,'rb').read()
print()
print('NEW HASH: %s  (%d B)  delta %+d'%(hashlib.sha256(r1).hexdigest(),len(r1),len(r1)-len(r0)))
v=r1.decode('utf-8-sig'); code=re.sub(r'//.*$','',v,flags=re.M)
print('  BOM:',r1[:3]==b'\xef\xbb\xbf','| loneLF:',r1.count(b'\n')-r1.count(b'\r\n'))
print('  two-case fact present:', 'UN-ENERGISED' in v and 'K48 ENERGISED' in v)
print('  SUPERSEDED markers:', v.count('[SUPERSEDED BY t50'))
print('  executable K48=%d K76=%d K109=%d K110=%d K46=%d'%(code.count('K48_ACM5_AMP_REF'),code.count('K76_ACM_BST'),code.count('K109_BUSL1_PB0'),code.count('K110_ACM18_BST'),code.count('K46')))
print('  9-item SetOn:', [l.strip()[:150] for l in code.split('\r\n') if 'cbite.SetOn(' in l and 'K83_BUSH0_PMID' in l][:1])