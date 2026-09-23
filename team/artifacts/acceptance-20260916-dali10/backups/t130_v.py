import sys,io,os,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'review-handoff-note-plan-side.md')
b=open(p,'rb').read()
bom = b[:3]==b'\xef\xbb\xbf'
print('=== THEIR NOTE: does it carry the BOM axis they just taught me to check? ===')
print('  size=%d  BOM=%s  CRLF=%d  loneLF=%d'%(len(b),bom,b.count(b'\r\n'),b.count(b'\n')-b.count(b'\r\n')))
raw=hashlib.sha256(b).hexdigest()
lf=hashlib.sha256(b.replace(b'\r\n',b'\n')).hexdigest()
nb=b[3:] if bom else b
nobom=hashlib.sha256(nb.replace(b'\r\n',b'\n')).hexdigest()
print('  raw                          = %s'%raw[:32])
print('  lf_replace (BOM kept)        = %s  <-- what they published'%lf[:32])
print('  lf_replace + BOM stripped    = %s'%nobom[:32])
print('  => the three differ?', len({raw,lf,nobom})==3)
print()
print('  they published: raw b20ca356c8c7eae59172de34da65ae19... / lf_replace e15420e4d2ba3bd9995a287bd7a0f789...')
print('  my raw match      :', raw.startswith('b20ca356c8c7eae59172de34da65ae19'))
print('  my lf_replace match:', lf.startswith('e15420e4d2ba3bd9995a287bd7a0f789'))
print()
print('  => BOM axis is', 'MATERIAL for this file (must be declared)' if bom else 'IMMATERIAL for this file (absence should be stated)')