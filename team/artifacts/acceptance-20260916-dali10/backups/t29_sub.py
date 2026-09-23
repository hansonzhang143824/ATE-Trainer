import sys,io,os,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'t29-k110-evidence.md')
t=open(p,'rb').read().decode('utf-8-sig')
old='with the two evidence points I had supplied'
if 'contract line-number substitution' not in t:
    add=('> **Locator substitution, flagged not hidden.** The task and review addendum cite contract `L145` and `L1897`.\n'
     '> Those are line numbers in the reviewer\'s contract excerpt; the artefact this payload actually references is the\n'
     '> JSON `setup-contract.json`, where I verified the same authorities **by path and value** —\n'
     '> `tmDeltas.TM600.pinRouteTable./BST/…CH0 Low.needsClosed = [109,110,138,139,145,146]`,\n'
     '> `/BST/…CH1 Low.needsClosed = [109,110]`, `aliasFlatTable[3].relayPath = "K110_ACM18_BST -> K61_ACM8_SW"`,\n'
     '> and `aliasResolution[3].resolution.relayChain` naming `K110_ACM18_BST` "SetOn (ACM200 S5_FH18 -> BST)".\n'
     '> I did **not** assert `L145`/`L1897` as verified because I could not confirm those line numbers in my copy —\n'
     '> the semantic authorities are identical, the citation form is not.\n\n')
    t=t.replace('## 2b. PER-FUNCTION JUSTIFICATION', add+'## 2b. PER-FUNCTION JUSTIFICATION')
    open(p,'wb').write(t.encode('utf-8'))
r=open(p,'rb').read()
print('evidence doc %d B / %s'%(len(r),hashlib.sha256(r).hexdigest()))
print('substitution note present:','Locator substitution, flagged not hidden' in r.decode('utf-8'))
pay=os.path.join(d,'implementation-payload-TM600-TM601.cpp'); rp=open(pay,'rb').read()
print('payload %d B / %s'%(len(rp),hashlib.sha256(rp).hexdigest()))