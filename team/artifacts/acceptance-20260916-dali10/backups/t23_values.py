import sys,io,os,json,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
J=json.loads(open(os.path.join(d,'implementation-manifest.draft.json'),'rb').read().decode('utf-8-sig'))
ch=J['changes'][0]
pay=open(os.path.join(d,'implementation-payload-TM600-TM601.cpp'),'rb').read()
bk=open(os.path.join(d,'backups','test.cpp.before_TM600_TM601.bak'),'rb').read()
print('draft changes[0]:')
print('  payloadSha256 recorded:',ch['payloadSha256'])
print('  payload live          :',hashlib.sha256(pay).hexdigest())
print('  MATCH:',ch['payloadSha256']==hashlib.sha256(pay).hexdigest() and ch['payloadSize']==len(pay))
print('  beforeSha256 recorded :',ch['beforeSha256'])
print('  backup live           :',hashlib.sha256(bk).hexdigest())
print('  MATCH:',ch['beforeSha256']==hashlib.sha256(bk).hexdigest())
print('  afterSha256 field     :',repr(ch['afterSha256']))
print('  planRefs:',[x[:60] for x in ch['planRefs']])
print('  authorship:',J['authoredBy'])
print('  limitations:',len(J['limitations']))
print('  selfChecks exitCodes:',[sc['exitCode'] for sc in J['selfChecks']])