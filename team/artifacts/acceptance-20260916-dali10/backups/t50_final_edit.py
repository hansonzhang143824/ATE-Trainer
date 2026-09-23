import sys,io,os,re,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'implementation-payload-TM600-TM601.cpp')
r0=open(p,'rb').read(); h0=hashlib.sha256(r0).hexdigest()
print('OLD HASH (recorded before edit): %s  (%d B)'%(h0,len(r0)))
u=r0.decode('utf-8-sig').replace('\r\n','\n')
# --- the authorised edit: remove K109/K110 from the single TM600 SetOn ---
old='    cbite.SetOn(K83_BUSH0_PMID, K60_BUSL0_VCP, K61_ACM8_SW, K48_ACM5_AMP_REF, K76_ACM_BST, K109_BUSL1_PB0, K110_ACM18_BST, K13_VBAT_Cap, K85_CAP_PMID, K57_CAP_BST_SW, K126_V1P5_CAP, -1);'
new='    cbite.SetOn(K83_BUSH0_PMID, K60_BUSL0_VCP, K61_ACM8_SW, K48_ACM5_AMP_REF, K76_ACM_BST, K13_VBAT_Cap, K85_CAP_PMID, K57_CAP_BST_SW, K126_V1P5_CAP, -1);'
n=u.count(old); print('SetOn line matched:',n)
assert n==1, 'SetOn line not found exactly once'
u=u.replace(old,new)
# --- comment sync: replace the --check-extra / union rationale block ---
cs=u.find('    // SIDE EFFECT, REGISTERED: the union deliberately OVER-CLOSES')
ce=u.find('\n',u.find('// closed for safety. This limitation is registered in the t34 restriction list as required by t43.'))
print('comment block found:', cs>0 and ce>cs)
if cs>0 and ce>cs:
    newc=('    // t50 FINAL RULING (supersedes the union approach recorded above): the instrument is driven on\n'
 '    // CH5 of the ACM200, so this revision closes the **ch5 single route only** - K48_ACM5_AMP_REF +\n'
 '    // K76_ACM_BST. The earlier union (which also closed K109/K110) is NO LONGER applied: K109_BUSL1_PB0\n'
 '    // and K110_ACM18_BST have been REMOVED from this call.\n'
 '    // EVIDENCE ORDER FOR THE REMOVAL (strongest first):\n'
 '    //   1. PRODUCTION BEHAVIOUR (binding) - every deployed implementation that drives\n'
 '    //      SW12_U1REF_BST_ACM closes K48+K76; across the whole production tree K110_ACM18_BST and\n'
 '    //      K109_BUSL1_PB0 occur 0 times, so no shipped item closes them.\n'
 '    //   2. t42 independent review PASS (ACM200 pin attribution).\n'
 '    //   3. CONTRACT OWNER WITHDRAWAL - the owner agreed to the removal, and the contract owner\'s\n'
 '    //      earlier objection only existed because rev 25 was additive-only; rev 25 is now a\n'
 '    //      NARROWING revision, which removes that objection.\n'
 '    // K109/K110 belong to the CH18 route (S1_FPVIe_FL* -> K109 -> K110 -> BST per\n'
 '    // SCH-Connect-Map.txt:43/:269; the contract\'s relayChain labels them "S5_FH18"), NOT to ch5.\n'
 '    // Their disposition is now RULED: removed from this item.\n'
 '    // NO --check-extra DISABLE is needed any more: with a single ch5 route there is no deliberate\n'
 '    // over-closure, so that limitation recorded earlier in this comment is withdrawn.\n'
 '    // SW side unchanged (K60 + K61); K46 is still NOT added (it is the FPVIe0 high-side BUS pin).')
    u=u[:cs]+newc+u[ce:]
open(p,'wb').write(b'\xef\xbb\xbf'+u.encode('utf-8'))
r1=open(p,'rb').read(); h1=hashlib.sha256(r1).hexdigest()
print()
print('NEW HASH: %s  (%d B)'%(h1,len(r1)))
print('  delta: %+d B'%(len(r1)-len(r0)))