import sys,io,os,json,hashlib,time
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
ap=os.path.join(d,'APPLY-TM600-TM601.md')
r=open(ap,'rb').read()
print('=== the CRLF mistake I introduced ===')
print('  original style was pure LF (0 CRLF / 101 lone LF); after my append: %d CRLF / %d lone LF'%(r.count(b'\r\n'),r.count(b'\n')-r.count(b'\r\n')))
print('  => I normalised every existing line. Restoring pure LF (original style).')
txt=r.decode('utf-8-sig')
fixed=txt.replace('\r\n','\n').encode('utf-8')
open(ap,'wb').write(fixed)
r2=open(ap,'rb').read()
print()
print('=== AFTER FIX ===')
print('  %d B / %s'%(len(r2),hashlib.sha256(r2).hexdigest()))
print('  CRLF=%d loneLF=%d  (original was 0/101 -> now LF-preserved)'%(r2.count(b'\r\n'),r2.count(b'\n')-r2.count(b'\r\n')))
print('  reader rule present:', 'READER RULE' in r2.decode('utf-8'))
# verify the pre-existing content is byte-identical to the original except for the appended section
orig=open(os.path.join(d,'backups','APPLY-BEFORE-APPEND.tmp'),'rb') if os.path.exists(os.path.join(d,'backups','APPLY-BEFORE-APPEND.tmp')) else None
# update manifest to the corrected hash
mp=os.path.join(d,'implementation-manifest.json')
M=json.loads(open(mp,'rb').read().decode('utf-8-sig'))
for e in M['handoffCitationRisk']['authoritativeCurrentValues']:
    if e['artefact']=='APPLY-TM600-TM601.md':
        e['size']=len(r2); e['sha256']=hashlib.sha256(r2).hexdigest()
        e['mtime']=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(os.stat(ap).st_mtime))
open(mp,'wb').write((json.dumps(M,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
mr=open(mp,'rb').read()
print()
print('=== manifest re-synced ===')
print('  %d B / %s'%(len(mr),hashlib.sha256(mr).hexdigest()))
for e in json.loads(mr.decode('utf-8'))['handoffCitationRisk']['authoritativeCurrentValues']:
    print('    %-38s %7d B / %s'%(e['artefact'],e['size'],e['sha256'][:16]))