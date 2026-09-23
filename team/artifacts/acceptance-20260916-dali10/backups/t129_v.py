import sys,io,os,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'implementation-payload-TM600-TM601.cpp'); b=open(p,'rb').read()
print('=== THEIR THIRD AXIS: BOM ===')
print('  BOM present:', b[:3]==b'\xef\xbb\xbf')
print()
print('  raw (BOM+CRLF kept)          = %s'%hashlib.sha256(b).hexdigest())
print('  lf  (CRLF->LF, BOM kept)     = %s'%hashlib.sha256(b.replace(b'\r\n',b'\n')).hexdigest())
nb=b[3:] if b[:3]==b'\xef\xbb\xbf' else b
print('  lf + BOM stripped            = %s  <-- their third value'%hashlib.sha256(nb.replace(b'\r\n',b'\n')).hexdigest())
print()
print('  they report lf+BOM-stripped = 3732d0fd33b2510d...')
print('  MATCH:', hashlib.sha256(nb.replace(b'\r\n',b'\n')).hexdigest().startswith('3732d0fd33b2510d'))
print()
print('  => three distinct values for one artefact => the kind NAME alone does not fix the convention.')