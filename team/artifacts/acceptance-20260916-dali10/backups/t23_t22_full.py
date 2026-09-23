import sys,io,os,json
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
J=json.loads(open(os.path.join(d,'review','t22-fr001-findings.json'),'rb').read().decode('utf-8-sig'))
found={}
def walk(o):
    if isinstance(o,dict):
        if isinstance(o.get('id'),str) and o['id'].startswith('T22-'):
            found[o['id']]=o
        for v in o.values(): walk(v)
    elif isinstance(o,list):
        for v in o: walk(v)
walk(J)
for k in sorted(found):
    o=found[k]
    print('='*78)
    print('%s  severity=%s  verdict=%s'%(k,o.get('severity'),o.get('verdict')))
    for f in ('title','problem','finding','statement','evidence','recommendation','requiredFix','disposition','locators','locator'):
        if o.get(f) is not None:
            v=o[f]
            print('  %-16s %s'%(f, json.dumps(v,ensure_ascii=False)[:600] if not isinstance(v,str) else v[:600]))