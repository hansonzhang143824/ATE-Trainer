import sys,io,os,hashlib,json,time
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
print('=== current hashes (measured now, exact paths) ===')
for n in ['implementation-manifest.json','implementation-payload-TM600-TM601.cpp','t29-k110-evidence.md']:
    p=os.path.join(d,n); r=open(p,'rb').read()
    print('  %-40s %6d B / %s'%(n,len(r),hashlib.sha256(r).hexdigest()))
print()
print("  t4 cites manifest as 39167 B / 216a2e37... (that was two revisions ago)")
M=json.loads(open(os.path.join(d,'implementation-manifest.json'),'rb').read().decode('utf-8'))
print('  manifest keys include handoffCitationRisk:','handoffCitationRisk' in M)
print('  planGaps statusUpdate mentions v21:','RESOLVED IN-PLAN BY t27/v21' in json.dumps(M,ensure_ascii=False))
print('  reviewStatus present:','reviewStatus' in M)