import sys,io,os,json,hashlib,glob
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
print('=== t22 review artefacts ===')
for p in sorted(glob.glob(os.path.join(d,'review','t22*'))):
    r=open(p,'rb').read(); print('  %-46s %7d B %s'%(os.path.basename(p),len(r),hashlib.sha256(r).hexdigest()[:16]))
fp=os.path.join(d,'review','t22-fr001-findings.json')
if os.path.exists(fp):
    J=json.loads(open(fp,'rb').read().decode('utf-8-sig'))
    print()
    print('=== t22 findings (ids, verdicts, severities) ===')
    def walk(o):
        if isinstance(o,dict):
            if 'id' in o and ('verdict' in o or 'severity' in o or 'disposition' in o):
                print('  %-10s sev=%-8s verdict=%-14s %s'%(str(o.get('id'))[:10],str(o.get('severity'))[:8],str(o.get('verdict') or o.get('disposition'))[:14],str(o.get('problem') or o.get('finding') or '')[:90]))
            for v in o.values(): walk(v)
        elif isinstance(o,list):
            for v in o: walk(v)
    walk(J)