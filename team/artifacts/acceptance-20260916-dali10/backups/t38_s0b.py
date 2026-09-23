import sys,io,os,re,hashlib,time
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'t40-tm601-bst-evidence.md')
t=open(p,'rb').read().decode('utf-8-sig')
pay=os.path.join(d,'implementation-payload-TM600-TM601.cpp'); rp=open(pay,'rb').read()
ph=hashlib.sha256(rp).hexdigest()
fixes=[]
# (1) stale payload hash in the header -> current, by content key (no bare hash anchor)
o='**38,888 B / `f536c7e4896f272ca9b8dc2356cb557c622d4a4e387a61f32ed7beea08421ef0`** (BOM + CRLF, 0 lone LF).'
n=('**39,457 B / `%s`** (BOM + CRLF, 0 lone LF) — cited by CONTENT KEY, not by this hash alone: the file must contain\n'
   '`t29 PER-FUNCTION JUSTIFICATION` (\u00d71), **executable (comments stripped)** `K109_BUSL1_PB0` \u00d71 and `K110_ACM18_BST` \u00d71,\n'
   'and for this revision **executable `TM601 ACM Sets` = 0** with **`TM600 ACM Sets` = 10**. A hash quoted in a message is\n'
   'a point-in-time check; the content keys are the revision test.')%ph
if o in t: t=t.replace(o,n); fixes.append('header payload hash -> current + content keys')
# (2) the escalation paragraph still said "pending t39 and t40"
o2='so **treat my conclusion as a PROPOSAL pending t39 and t40**.'
if o2 in t: t=t.replace(o2,'so **treat my conclusion as a PROPOSAL pending t40 and t42**. t39 (contract owner) has COMPLETED; t42 (schematic-expert) remains, and its pin attribution can change which relays are required (see `t38-acm-pin5-exposure.md`).'); fixes.append('escalation line -> t40 and t42')
# (3) the second open question is now three
o3='(ii) **is the dangling drive removed or completed?**'
if o3 in t: t=t.replace(o3,'(ii) **is the dangling drive removed or completed?** and (iii) **which ACM200 pin feeds the instrument** (t42) - under the pin-5 reading the required set is `[48,76]`, not `[109,110]`.'); fixes.append('added question (iii)')
open(p,'wb').write(t.encode('utf-8'))
r=open(p,'rb').read(); s=r.decode('utf-8')
print('fixes applied:')
for f in fixes: print('   -',f)
print()
print('t40 evidence NOW: %d B / %s @%s'%(len(r),hashlib.sha256(r).hexdigest(),time.strftime('%H:%M:%S',time.localtime(os.stat(p).st_mtime))))
print('  stale f536c7e4 gone:', 'f536c7e4' not in s)
print('  "pending t39 and t40" gone:', 'pending t39 and t40' not in s)
print('  content keys in header:', 'CONTENT KEY' in s)
print('  t40 + t42 present:', 't40 + t42' in s)