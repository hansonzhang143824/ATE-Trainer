import sys,io,os,json,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'implementation-manifest.draft.json')
J=json.loads(open(p,'rb').read().decode('utf-8-sig'))
lim=('TM643_VBAT_LOOP_INDICTOR — 2 relay-trace warnings, RECORDED BASELINE DEVIATION (captain ruling: not fixed in this run, '
 'no repair task created). Evidence of pre-existence: the function is present in backups/test.cpp.before_TM600_TM601.bak; its '
 'body is byte-unchanged by this work; and running the project gate against that pre-change copy yields warnings byte-identical '
 'to those from the post-change tree ("TM643_VBAT_LOOP_INDICTOR: 静态供电 BST_SW 但未闭稳压电容 K57_CAP_BST_SW" and the VBUS/'
 'K5_VBUS_Cap counterpart). Severity: warning class only — the baseline sole red gate was cbit, so TM643 never made the gate red. '
 'Locators: SCH-Connect-Map.txt:904 (SW 稳压 needsClosed K57) and :915 (VBUS 稳压 needsClosed K5). The function is outside this '
 'task in-scope paths and must not be touched without a separately created task.')
key='RECORDED BASELINE DEVIATION'
if not any(key in x for x in J['limitations']):
    J['limitations'].append(lim)
    print('appended dedicated TM643 deviation entry')
open(p,'wb').write((json.dumps(J,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
r=open(p,'rb').read(); J2=json.loads(r.decode('utf-8'))
print('draft %d B / %s'%(len(r),hashlib.sha256(r).hexdigest()))
print('limitations:',len(J2['limitations']),'| dedicated entry present:',any(key in x for x in J2['limitations']))