import sys,io,os,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
print('=== MY DELIVERY, final (path -> raw + lf_normalized, per the adopted format) ===')
for f in ['implementation-payload-TM600-TM601.cpp','implementation-manifest.json','APPLY-TM600-TM601.md']:
    p=os.path.join(d,f); b=open(p,'rb').read()
    print('  %s'%f)
    print('     size=%d  raw=%s'%(len(b),hashlib.sha256(b).hexdigest()[:24]))
    print('     lf_normalized=%s'%hashlib.sha256(b.replace(b'\r\n',b'\n')).hexdigest()[:24])
print()
p=os.path.join(d,'implementation-payload-TM600-TM601.cpp'); b=open(p,'rb').read()
print('FROZEN payload intact:', hashlib.sha256(b).hexdigest()=='66abc088ae6bd5f9b9d7201673003fc0be2450fd6f1f222c6a4a902cbe4f0cc4')
print('BOM:',b[:3]==b'\xef\xbb\xbf','| loneLF:',b.count(b'\n')-b.count(b'\r\n'),'| CRLF:',b.count(b'\r\n'))