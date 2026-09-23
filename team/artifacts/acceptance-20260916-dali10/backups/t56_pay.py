import sys,io,os,hashlib,time,json
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'implementation-payload-TM600-TM601.cpp')
r=open(p,'rb').read()
print('=== payload: t4 asks about 66abc088 @21:09:24 ===')
print('  %d B / %s @%s'%(len(r),hashlib.sha256(r).hexdigest(),time.strftime('%H:%M:%S',time.localtime(os.stat(p).st_mtime))))
print('  matches t4: 43806 / 66abc088... @21:09:24 ->',hashlib.sha256(r).hexdigest()=='66abc088ae6bd5f9b9d7201673003fc0be2450fd6f1f222c6a4a902cbe4f0cc4')
print('  NOTE: t4 says I declared frozen at 2d0984d9/39,457 - that was the F2 freeze EARLIER in the run;')
print('        the current freeze is 66abc088, set by the captain at 21:09 after the authorised removal+comment work.')
print()
print('=== my verifiedCounts: does it still say K48=K76=0? (t4 flags this) ===')
M=json.loads(open(os.path.join(d,'implementation-manifest.json'),'rb').read().decode('utf-8-sig'))
vc=M['handoffCitationRisk']['landingGate']['verifiedCounts']
for k in ('payloadSha256','payloadSize','executableK48_ACM5_AMP_REF','executableK76_ACM_BST','executableK109_BUSL1_PB0','executableK110_ACM18_BST','executableK46'):
    print('  %-32s %s'%(k,vc.get(k)))
print('  -> K48/K76 are 1/1, NOT 0: already synced in my t55 edit')
print()
print('=== my t38-acm-pin5-exposure.md: does it still say "closes neither 48 nor 76"? ===')
q=os.path.join(d,'t38-acm-pin5-exposure.md'); t=open(q,'rb').read().decode('utf-8-sig')
print('  file %d B / %s'%(len(open(q,'rb').read()),hashlib.sha256(open(q,'rb').read()).hexdigest()))
for pat in ['closes neither','K48','K76']:
    print('  %-16s occurrences: %d'%(pat,t.count(pat)))