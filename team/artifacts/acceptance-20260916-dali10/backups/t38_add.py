import sys,io,os,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'t38-acm-pin5-exposure.md')
t=open(p,'rb').read().decode('utf-8-sig')
old='## 1. The contradiction, stated exactly'
add=('## 0. THE DECISIVE DOCUMENTARY LINE (verified first-hand at `project/DALI/SCH-Connect-Map.txt`)\n\n'
 '```\n'
 'L672|   BST  [Kelvin]  需闭合: K48,K76\n'
 'L673|     F: S5_ACM200_FH5 -> K48(Relay-ON) -> K76(Relay-ON) -> BST_F\n'
 'L674|     S: S5_ACM200_SH5 -> K48(Relay-ON) -> K76(Relay-ON) -> BST_S\n'
 '```\n'
 'This is the **netlist stating the ACM200 path to BST in full**: the source is **pin 5** (`S5_ACM200_FH5`), and the\n'
 'required closures are **K48 and K76** with **no K109/K110 anywhere in the path**. Note the path *starts* at the\n'
 'ACM200 pin, so this row is about the excitation reaching BST — as distinct from `L42`/`L268`, whose paths start at\n'
 '**`S1_FPVIe_FH0`** (a measurement pin), which is why those rows list `K109/K110`.\n'
 'Two further corroborations from the same file: `L39` `CH0 High -> BST 需闭合: K46,K48,K76` (the FPVIe CH0-High\n'
 'route to the same node goes through `K46 -> K48 -> K76`, over the same two relays), and `L461`/`L536` where other\n'
 'sources (`S10_CH0_A`, `S8_QVM_CH0+`) reach BST through the identical `K46 -> K48 -> K76` chain. **`K48/K76` are the\n'
 'relays that carry anything to BST in this fixture**; `K109/K110` belong to the FPVIe-channel rows.\n\n'
 '**Also worth noting for t42:** `L775`/`L778` show the *same* pin 5 continuing `-> K48(Relay-NC) -> K49 -> SW1_F/SW2_F`,\n'
 'i.e. `K48` is a two-destination relay (BST when ON with `K76`, SW1/SW2 when NC). That is the same double-throw\n'
 'mechanism established for `K110`, and it means **`K48` being un-actuated silently routes pin 5 to SW1/SW2** rather\n'
 'than to BST — the identical dangling-drive pattern, one relay family over.\n\n')
if 'THE DECISIVE DOCUMENTARY LINE' not in t:
    t=t.replace(old,add+old)
    # correct the path reference in section 1's table row for the channel macro
    t=t.replace('the ACM200 *source*','the ACM200 *source* (pin 5, per `SCH-Connect-Map.txt:672-674`)')
    open(p,'wb').write(t.encode('utf-8'))
r=open(p,'rb').read()
print('addendum %d B / %s'%(len(r),hashlib.sha256(r).hexdigest()))
print('decisive section present:','THE DECISIVE DOCUMENTARY LINE' in r.decode('utf-8'))
print()
pay=os.path.join(d,'implementation-payload-TM600-TM601.cpp')
print('payload UNCHANGED:',os.path.getsize(pay),hashlib.sha256(open(pay,'rb').read()).hexdigest())