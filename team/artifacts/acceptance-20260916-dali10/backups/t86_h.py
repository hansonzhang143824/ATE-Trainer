import sys,io,os,hashlib,time
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
n=os.path.join(d,'review-handoff-note-plan-side.md')
r=open(n,'rb').read()
print('=== careful hash inspection ===')
print('  size on disk : %d B'%len(r))
print('  they claim   : 81,800 B')
print('  size equal?  :', len(r)==81800)
raw=hashlib.sha256(r).hexdigest()
print('  raw sha256   : %s'%raw)
print('  they claim   : c82bd1a44e11d6dc8082ac043ab73d999ce51711ee82bda713f68ad05654e5b5')
print('  equal?       :', raw=='c82bd1a44e11d6dc8082ac043ab73d999ce51711ee82bda713f68ad05654e5b5')
print()
print('=== could it be a normalisation difference? try variants ===')
variants={
 'as-is (bytes)':r,
 'strip BOM':r[len(b"\xef\xbb\xbf"):] if r[:3]==b'\xef\xbb\xbf' else r,
 'LF-normalised':r.replace(b'\r\n',b'\n'),
 'CRLF-normalised':r.replace(b'\r\n',b'\n').replace(b'\n',b'\r\n'),
 'utf-16le encode of text':r.decode('utf-8-sig').encode('utf-16-le'),
 'utf-8 no BOM of decoded text':r.decode('utf-8-sig').encode('utf-8'),
}
for k,v in variants.items():
    hh=hashlib.sha256(v).hexdigest()
    print('  %-28s %s %s'%(k,hh[:32],'<== MATCH' if hh=='c82bd1a44e11d6dc8082ac043ab73d999ce51711ee82bda713f68ad05654e5b5' else ''))
print()
print('=== mtime + the key content their anchor is supposed to describe ===')
print('  mtime: %s'%time.strftime('%H:%M:%S',time.localtime(os.stat(n).st_mtime)))
print('  "twice by design":',open(n,encoding='utf-8-sig').read().count('twice by design'))