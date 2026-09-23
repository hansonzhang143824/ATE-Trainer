import sys,io,os,json,hashlib,time
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
for n in ['implementation-manifest.json','review-handoff-note-plan-side.md','t40-tm601-bst-evidence.md','t50-payload-k76-evidence.md']:
    p=os.path.join(d,n)
    if os.path.exists(p):
        r=open(p,'rb').read(); print('  %-42s %6d B / %s @%s'%(n,len(r),hashlib.sha256(r).hexdigest()[:32],time.strftime('%H:%M:%S',time.localtime(os.stat(p).st_mtime))))
M=json.loads(open(os.path.join(d,'implementation-manifest.json'),'rb').read().decode('utf-8-sig'))
lg=M['handoffCitationRisk']['landingGate']
print()
print('=== my landingGate AS IT STANDS (does it still say t40+t42?) ===')
print('  status:',lg['status'][:120])
print('  gates :',lg['gates'])
print('  contractRevisionSeen:',lg.get('contractRevisionSeen'))
print('  history:',lg['gateHistoryNote'][:120])