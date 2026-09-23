import sys,io,os,glob,hashlib,json,time
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
print('=== test-plan* now (one pass, python plaintext) ===')
for p in sorted(glob.glob(os.path.join(d,'test-plan*.json'))):
    r=open(p,'rb').read()
    rev=''
    if os.path.basename(p)=='test-plan.json':
        try: rev=str(json.loads(r.decode('utf-8-sig')).get('revision'))[:60]
        except: rev='(parse)'
    print('  %-22s %8d B %s %s mtime=%s'%(os.path.basename(p),len(r),hashlib.sha256(r).hexdigest()[:16],rev,time.strftime('%H:%M:%S',time.localtime(os.path.getmtime(p)))))
print()
print('=== my payloads now ===')
for n in ['implementation-payload-TM600-TM601.cpp','implementation-payload-TM600-TM601.pulse2ms-variant.cpp']:
    r=open(os.path.join(d,n),'rb').read()
    print('  %-58s %6d B %s'%(n,len(r),hashlib.sha256(r).hexdigest()))
print()
print("captain's payload claim: 14077 B / af521e72... -> compare with the 13121 B/2cd1ee72 predecessor")
print()
print('=== target untouched? ===')
s=open(r'D:\PROJECT6-DALI\ForCodexDebug\source\test.cpp','rb').read()
print('  test.cpp %d B %s  baseline=%s'%(len(s),hashlib.sha256(s).hexdigest(),hashlib.sha256(s).hexdigest()=='5c9cb3f9339f6db373afcff7504ef6b34924a4ca3042b5926cb612c819ac3317'))