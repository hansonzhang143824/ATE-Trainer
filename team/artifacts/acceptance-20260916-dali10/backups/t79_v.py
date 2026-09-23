import sys,io,os,hashlib,time
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
n=os.path.join(d,'review-handoff-note-plan-side.md')
r=open(n,'rb').read(); t=r.decode('utf-8-sig'); h=hashlib.sha256(r).hexdigest()
print('=== CURRENT note ===')
print('  %d B / %s @%s'%(len(r),h,time.strftime('%H:%M:%S',time.localtime(os.stat(n).st_mtime))))
print('  they cite: 66,305 B / 968def24f97a70d13bbbebd543fb12b91170086765cc6d68bfbfe869c485deac @23:04:01')
print('  match:', h=='968def24f97a70d13bbbebd543fb12b91170086765cc6d68bfbfe869c485deac')
print()
print('=== their claimed counts ===')
print('  "is to become"              = %d (they say 1)'%t.count('is to become'))
print('  "{48,60,61,76,83}"          = %d (they say 6)'%t.count('{48,60,61,76,83}'))
print('  "L406" / "L412" in the rule = %d / %d  <- their rule text cites positional locators'%(t.count('L406'),t.count('L412')))
print()
print('=== content-locator test: can I find the correction block WITHOUT any line number? ===')
i=t.find('Correction (my own slip')
if i>0:
    ln=t[:i].count('\n')+1
    print('  found by content at line %d (line number is not needed to locate it)'%ln)
    print('  excerpt: %s'%t[i:i+150].replace('\n',' '))
print()
print('=== my last read vs theirs: which revision did I actually read? ===')
print('  I reported 64,670 B / 42ac6d36... @22:59:10 with the phrase at L509')
for sz,hh,ts,who in [(53537,'b6ac2ea3…','22:35:37','t4 says I read this'),
                     (54692,'674af1e1…','22:39:05','t4 now says I read this'),
                     (64670,'42ac6d36…','22:59:10','what I actually reported'),
                     (66305,'968def24…','23:04:01','current')]:
    print('   %6d  %-12s %s  <- %s'%(sz,hh,ts,who))