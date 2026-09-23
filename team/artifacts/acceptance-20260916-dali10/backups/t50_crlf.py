import sys,io,os,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'implementation-payload-TM600-TM601.cpp')
r=open(p,'rb').read()
print('before: %d B  loneLF=%d  CRLF=%d  hash=%s'%(len(r),r.count(b'\n')-r.count(b'\r\n'),r.count(b'\r\n'),hashlib.sha256(r).hexdigest()))
v=r.decode('utf-8-sig').replace('\r\n','\n')          # normalise
out=b'\xef\xbb\xbf'+v.replace('\n','\r\n').encode('utf-8')
open(p,'wb').write(out)
r2=open(p,'rb').read()
print('after : %d B  loneLF=%d  CRLF=%d  hash=%s'%(len(r2),r2.count(b'\n')-r2.count(b'\r\n'),r2.count(b'\r\n'),hashlib.sha256(r2).hexdigest()))
print('  BOM:',r2[:3]==b'\xef\xbb\xbf','| loneLF==0:',(r2.count(b'\n')-r2.count(b'\r\n'))==0)