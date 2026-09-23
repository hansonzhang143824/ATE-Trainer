import sys,io,os,re,hashlib,time
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'t40-tm601-bst-evidence.md')
t=open(p,'rb').read().decode('utf-8-sig')
before=hashlib.sha256(open(p,'rb').read()).hexdigest()
# ① the approved one-line fact correction
old1='landing is BLOCKED pending t39+t40; the t38 removal is a PROPOSAL'
old2='t39 (contract owner) and t40 (rule-reviewer) independently judge whether TM601\'s 5 V must reach BST'
n=0
if 'pending t40 + t42' not in t:
    if old1 in t: t=t.replace(old1,'landing is BLOCKED pending t40 + t42; the t38 removal is a PROPOSAL'); n+=1
    if old2 in t:
        t=t.replace(old2,"t39 (contract owner, COMPLETE), t40 (rule-reviewer) and t42 (schematic-expert, ACM200 pin attribution) judge independently whether TM601's 5 V must reach BST and which ACM200 pin feeds the instrument"); n+=1
    # add the pin-5 conditional note to section 0 (same approved edits)
    t=t.replace('**⚠ ESCALATION-DEPENDENT CONCLUSIONS.**',
      ('**⚠ SCOPE OF THE OPEN QUESTIONS.** The landing gate is **t40 + t42** (t39, the contract owner, has completed). t42 '
       'attribution could change WHICH relays are required: see `t38-acm-pin5-exposure.md`, where `SCH-Connect-Map.txt:672-674` '
       'gives `BST [Kelvin] 需闭合: K48,K76` via `S5_ACM200_FH5` (pin 5), while the rows listing `K109/K110` start at the '
       'measurement pin `S1_FPVIe_FH0`. Under the pin-5 reading this item\'s removed drive would have needed `[48,76]` - and '
       '**neither is in TM601.relaySet**, so the removal conclusion holds under either reading.\n\n'
       '**⚠ ESCALATION-DEPENDENT CONCLUSIONS.**'),1); n+=1
    open(p,'wb').write(t.encode('utf-8'))
r=open(p,'rb').read()
print('edits applied:',n)
print('t40 evidence BEFORE: %s'%before)
print('t40 evidence NOW   : %d B / %s @%s'%(len(r),hashlib.sha256(r).hexdigest(),time.strftime('%H:%M:%S',time.localtime(os.stat(p).st_mtime))))
print('  -> captain asked me to recompute: %s'%('11,691/de6bb17f CONFIRMED (pre-edit)' if before.startswith('de6bb17f') else 'DIFFERS from de6bb17f'))
print("  pending t40 + t42 wording present:", 'pending t40 + t42' in r.decode('utf-8'))
print()
print("=== verify the captain's cited macro names in the deployed tree ===")
h=open(r'D:\PROJECT6-DALI\ForCodexDebug\source\StdAfx.h','rb').read().decode('utf-8-sig',errors='replace')
for pat in [r'#define\s+(K48_ACM5_AMP_REF)\s+(\d+)',r'#define\s+(K76_ACM_BST)\s+(\d+)',r'#define\s+(K_BST_ACM[A-Za-z0-9_]*)\s+([\d,]+)']:
    hits=re.findall(pat,h)
    print('  %-42s %s'%(pat[:40],hits if hits else 'NOT FOUND'))