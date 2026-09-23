import sys,io,os,json,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'implementation-manifest.draft.json')
J=json.loads(open(p,'rb').read().decode('utf-8-sig'))
J['changes'][0]['payloadSha256']='444810dde99f79ed1ef1939bb1659d5769f547bfc1103e9b9187ee46f455675c'
J['changes'][0]['payloadSize']=35014
J['changes'][0]['repairNote']=J['changes'][0]['repairNote']+' rev2: the TM600 comment no longer names the companion item at all, and the ERROR_RES association is now literal (ERROR_RES = 9999) at both failure sites.'
open(p,'wb').write((json.dumps(J,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
r=open(p,'rb').read(); print('draft %d B / %s'%(len(r),hashlib.sha256(r).hexdigest()))
a=os.path.join(d,'t23-amendment-evidence.md'); ra=open(a,'rb').read()
print('evidence doc %d B / %s'%(len(ra),hashlib.sha256(ra).hexdigest()))
s=open(r'D:\PROJECT6-DALI\ForCodexDebug\source\test.cpp','rb').read()
print('target unchanged:',hashlib.sha256(s).hexdigest()=='3dbceb496d79d7d08631713b98e46c0c2ba6163eaf5356a87dded677e35ba479')