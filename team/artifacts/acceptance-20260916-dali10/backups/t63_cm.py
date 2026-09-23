import sys,io,os,json,hashlib,time
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
mp=os.path.join(d,'implementation-manifest.json')
r=open(mp,'rb').read(); M=json.loads(r.decode('utf-8-sig'))
print('manifest: %d B / %s @%s'%(len(r),hashlib.sha256(r).hexdigest(),time.strftime('%H:%M:%S',time.localtime(os.stat(mp).st_mtime))))
cm=M['handoffCitationRisk'].get('countingMethod','')
print()
print('=== current countingMethod ===')
print(' ',cm)
print()
print('=== does it already state the macro-expansion rule? ===')
for pat in ['macro','宏','alias','K_FPVIH_TO_BST_A','token']:
    print('  %-18s present: %s'%(pat, pat in cm))