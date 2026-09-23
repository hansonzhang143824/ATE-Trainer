import sys,io,os,json,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'implementation-manifest.draft.json')
J=json.loads(open(p,'rb').read().decode('utf-8-sig'))
lim=('TM643_VBAT_LOOP_INDICTOR carries 2 relay-trace warnings that are PRE-EXISTING and are recorded here rather than '
 'fixed (captain ruling: recorded baseline deviation; no repair task in this run). Evidence: the function exists in '
 'backups/test.cpp.before_TM600_TM601.bak, its body is byte-unchanged by this work, and running the project gate against '
 'that pre-change copy produces warnings byte-identical to the ones from the post-change tree ("TM643_VBAT_LOOP_INDICTOR: '
 '静态供电 BST_SW 但未闭稳压电容 K57_CAP_BST_SW" and "... VBUS 但未闭稳压电容 K5_VBUS_Cap"). Severity: warning class only - '
 'the baseline\'s sole red gate was cbit, so TM643 never made the gate red. The function is out of this task\'s in-scope '
 'paths and must not be touched without a separately created task.')
if not any('TM643' in x for x in J['limitations']): J['limitations'].append(lim)
open(p,'wb').write((json.dumps(J,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
r=open(p,'rb').read()
print('draft %d B / %s valid=%s limitations=%d'%(len(r),hashlib.sha256(r).hexdigest(),bool(json.loads(r.decode('utf-8'))),len(J['limitations'])))
print('TM643 entry present:',any('TM643' in x for x in J['limitations']))