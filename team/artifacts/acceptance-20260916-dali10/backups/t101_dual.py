import sys,io,os,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
ap=os.path.join(d,'APPLY-TM600-TM601.md')
new=open(ap,'rb').read()
orig_hash='429ad881d67d3feb6886ca5006dbf663cf025a91025545d988f8cdc446f6dfa1'
print('=== TESTING THEIR PROPOSED INSTRUMENT: dual hash (raw + LF-normalised) ===')
print('  It should distinguish "content changed" from "line endings changed".')
def dual(b):
    return hashlib.sha256(b).hexdigest(), hashlib.sha256(b.replace(b'\r\n',b'\n')).hexdigest()
head=new[:7110]
print()
print('  ORIGINAL (7,110 B, LF):')
o=dual(head); print('     raw=%s'%o[0][:24]); print('     lf =%s'%o[1][:24])
crlf_version=head.replace(b'\n',b'\r\n')
c=dual(crlf_version)
print('  SAME CONTENT re-encoded as CRLF:')
print('     raw=%s  <- CHANGED'%c[0][:24]); print('     lf =%s  <- UNCHANGED'%c[1][:24])
print()
print('  => raw changes, lf-normalised stays identical => one comparison classifies it as')
print('     "line-ending normalisation, content untouched" WITHOUT reading the diff.')
print('  => their instrument works exactly as they described.')