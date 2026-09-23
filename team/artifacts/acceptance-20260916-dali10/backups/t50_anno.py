import sys,io,os,re,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
u=open(os.path.join(d,'implementation-payload-TM600-TM601.cpp'),'rb').read().decode('utf-8-sig')
print('=== does the payload annotate the --check-extra limitation (t43 §4 requirement)? ===')
print('  mentions --check-extra:', '--check-extra' in u)
print('  mentions the union/over-close rationale:', ('union' in u.lower() or 'both' in u.lower()))
print('  mentions ch5 vs ch18 UNKNOWN:', ('ch5' in u or 'channel 5' in u))
print()
print('=== so t43 §4 requires adding that annotation to the payload comment ===')
# add it now (required by the ruling)
old='    // released by exclusivity anyway (it is still listed below because this revision retains the pair).'
new=('    // released by exclusivity anyway (it is still listed below because this revision retains the pair).\n'
 '    // t43 RULING (rule-reviewer, review/t43-...md, 7,439 B / d4c3835437a41c9f1bee7b15c2d381da69c99ceacd0503f5f6dbb0f1023e90a7):\n'
 '    // which ACM200 channel feeds BST - ch5 (K48+K76) or ch18 (K110 as the contract relayChain spells\n'
 '    // out, "S5_FH18") - is UNKNOWN(c) and needs the contract owner or bench evidence. The SAFE minimal\n'
 '    // fix, which this payload implements, is the UNION: close the ch5 BST branch (K48_ACM5_AMP_REF +\n'
 '    // K76_ACM_BST) IN ADDITION TO the contract-literal branch (K109/K110/K61). Neither branch alone is\n'
 '    // safe: omitting K48/K76 leaves BST unreachable if ch5 is right, and DELETING K110 breaks the chain\n'
 '    // if ch18 is right. The union is safe under both readings because the two branches arrive on the same\n'
 '    // BST net (K76.S1.5 and K110.S1.5 both sit on BST_F_S1).\n'
 '    // SIDE EFFECT, REGISTERED: the union deliberately OVER-CLOSES, so the "--check-extra" gate (which\n'
 '    // flags extra closures) MUST NOT be enabled for this revision - it would red-flag the branch that is\n'
 '    // closed for safety. This limitation is registered in the t34 restriction list as required by t43.')
if '--check-extra' not in u:
    n=u.count(old); print('  anchor matched:',n)
    if n==1:
        u=u.replace(old,new)
        open(os.path.join(d,'implementation-payload-TM600-TM601.cpp'),'wb').write(b'\xef\xbb\xbf'+u.replace('\r\n','\n').replace('\n','\r\n').encode('utf-8'))
r=open(os.path.join(d,'implementation-payload-TM600-TM601.cpp'),'rb').read(); v=r.decode('utf-8-sig'); code=re.sub(r'//.*$','',v,flags=re.M)
print()
print('payload %d B / %s'%(len(r),hashlib.sha256(r).hexdigest()))
print('  --check-extra now annotated:','--check-extra' in v)
print('  invariants: d1=%d d2=%d clamp=%d meas=%d K126=%d ERR=%d K57=%d K109=%d K110=%d K48=%d K76=%d K46=%d'%(
 code.count('delay_ms(1)'),code.count('delay_ms(2)'),code.count('SetClamp(50, 50)'),code.count('MeasureVI(200, 5, FPVIe_MV_X10)'),
 code.count('K126_V1P5_CAP'),code.count('ERROR_RES'),code.count('K57_CAP_BST_SW'),
 code.count('K109_BUSL1_PB0'),code.count('K110_ACM18_BST'),code.count('K48_ACM5_AMP_REF'),code.count('K76_ACM_BST'),code.count('K46')))
print('  SetOn calls:',code.count('cbite.SetOn('),'| BOM',r[:3]==b'\xef\xbb\xbf','| loneLF',r.count(b'\n')-r.count(b'\r\n'))