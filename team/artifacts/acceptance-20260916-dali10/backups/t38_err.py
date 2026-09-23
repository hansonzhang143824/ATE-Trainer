import sys,io,os,json,hashlib,re
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
u=open(os.path.join(d,'implementation-payload-TM600-TM601.cpp'),'rb').read().decode('utf-8-sig')
naive=[l for l in u.split('\n') if not l.strip().startswith('//')]
proper=re.sub(r'//.*$','',u,flags=re.M).split('\n')
print('=== naive (line-leading strip) vs proper (inline strip) ===')
for k in ['ERROR_RES','delay_ms(1)','K126_V1P5_CAP','K57_CAP_BST_SW','K109_BUSL1_PB0','K110_ACM18_BST']:
    a=sum(l.count(k) for l in naive); b=sum(l.count(k) for l in proper)
    print('  %-18s naive=%d  proper=%d  %s'%(k,a,b,'DIFFERS' if a!=b else ''))
print()
print('  => ERROR_RES differed because the inline comment text "// ERROR_RES = 9999" survived a line-leading-only strip.')
p=os.path.join(d,'implementation-manifest.json')
M=json.loads(open(p,'rb').read().decode('utf-8-sig'))
mc=M['handoffCitationRisk']['authoritativeCurrentValues'][0]['mustContain']
M['handoffCitationRisk']['authoritativeCurrentValues'][0]['mustContain']=[x.replace('ERROR_RES = 4','ERROR_RES = 2') for x in mc]
M['handoffCitationRisk']['countingMethod']=('Counts use the PROPER comment strip: re.sub(r"//.*$","",text,flags=re.M) - inline trailing comments removed, not merely '
 'lines that begin with //. A line-leading-only strip leaves text like "// ERROR_RES = 9999" counted and over-reports ERROR_RES as 4 instead of 2; that '
 'near-miss is recorded because the same over-count would silently inflate any executable-code criterion.')
open(p,'wb').write((json.dumps(M,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
r=open(p,'rb').read()
print('manifest %d B / %s'%(len(r),hashlib.sha256(r).hexdigest()))
print('ERROR_RES key now:',[x for x in M['handoffCitationRisk']['authoritativeCurrentValues'][0]['mustContain'] if 'ERROR_RES' in x])