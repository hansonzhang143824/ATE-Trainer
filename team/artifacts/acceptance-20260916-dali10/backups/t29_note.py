import sys,io,os,json,re
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
M=json.loads(open(r'D:\Newtest\DSH\ATE-Coding-Plat\project\DALI\meta\dali_tm_meta.json','rb').read().decode('utf-8-sig'))
for e in M['functions']:
    if e.get('functionName')=='TM601_LS_RDSON':
        s=json.dumps(e,ensure_ascii=False)
        i=s.find('VBUS')
        j=s.rfind('"',0,i-400)
        print('=== the t26 note (full text) ===')
        print(s[max(0,i-1200):i+900].replace('\\n','\n')[:2200])