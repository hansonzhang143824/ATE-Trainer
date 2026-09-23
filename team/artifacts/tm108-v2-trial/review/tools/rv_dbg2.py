import json, importlib.util, sys
spec=importlib.util.spec_from_file_location('rp', r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\tm108-v2-trial\review\tools\rv_patch.py')
# don't execute; read the source and exec only the PATCHES list
src=open(r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\tm108-v2-trial\review\tools\rv_patch.py','r',encoding='utf-8').read()
ns={}
head=src.split('# apply')[0]
head=head.replace("P = r'D:\\Newtest\\DSH\\ATE-Coding-Plat\\team\\artifacts\\tm108-v2-trial\\review\\t8-review-findings.json'","P=''")
exec(head, ns)
PAT=ns['PATCHES']
P=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\tm108-v2-trial\review\t8-review-findings.json'
base=open(P,'rb').read().decode('utf-8')
for i,(old,new) in enumerate(PAT):
    print('patch %d: new contains literal newline = %s ; count of dquote in new = %d' % (i, chr(10) in new, new.count('"')))
s=base
for i,(old,new) in enumerate(PAT):
    if s.count(old)!=1:
        print('patch %d anchor count %d -> stop' % (i, s.count(old))); break
    s=s.replace(old,new,1)
    try:
        json.loads(s)
        print('after patch %d: JSON OK' % i)
    except Exception as e:
        print('after patch %d: JSON FAIL -> %s' % (i, e))
        break
