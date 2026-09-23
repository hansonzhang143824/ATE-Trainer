import sys,io,os,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
print('=== THEIR OBSERVATION: my two own artefacts sit on opposite sides of "does the hash KIND matter?" ===')
for f in ['implementation-payload-TM600-TM601.cpp','implementation-manifest.json','APPLY-TM600-TM601.md']:
    p=os.path.join(d,f); b=open(p,'rb').read()
    raw=hashlib.sha256(b).hexdigest(); lf=hashlib.sha256(b.replace(b'\r\n',b'\n')).hexdigest()
    kind='CRLF+BOM' if b.count(b'\r\n') else 'pure LF'
    print('  %-40s %-10s raw==lf_norm: %s'%(f,kind,raw==lf))
print()
print('  => payload (CRLF) : the two hashes differ -> the KIND matters')
print('     manifest/APPLY (LF): they coincide      -> the kind is immaterial')
print('  => so a single-hash report would be ambiguous for the payload and fine for the others.')
print('     That is the concrete reason the dual form earns its place.')