import sys,io,os,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'t29-k110-evidence.md')
t=open(p,'rb').read().decode('utf-8-sig')
add=('## 2b. PER-FUNCTION JUSTIFICATION (captain-mandated: no silent single-place edit)\n\n'
 '### TM600 — closes K109 **and** K110\n\n'
 '| Authority | Requires | Locator |\n| --- | --- | --- |\n'
 '| `tmDeltas.TM600.pinRouteTable./BST/…CH0 Low` | `[109,110,138,139,145,146]` | contract rev 24 |\n'
 '| `tmDeltas.TM600.pinRouteTable./BST/…CH1 Low` | `[109,110]` | contract rev 24 |\n'
 '| `tmDeltas.TM600.relaySet` | contains **109** and **110** | contract rev 24 |\n'
 '| `aliasResolution[3]` (bst2sw) `relayChain` | `K110_ACM18_BST` "SetOn (ACM200 S5_FH18 -> BST)" | contract rev 24 |\n'
 '| `aliasFlatTable[3].relayPath` | `K110_ACM18_BST -> K61_ACM8_SW` | contract rev 24 |\n'
 '| Connect map CH0 route | `CH0 Low -> BST 需闭合: K109,K110,K138,K139,K145,K146` | `SCH-Connect-Map.txt:42`; path at `:43` |\n'
 '| Connect map CH1 route | `CH1 Low -> BST 需闭合: K109,K110` | `:268`; path at `:269`/`:270` |\n\n'
 '### TM601 — does **NOT** close K109/K110, and this is a finding from the contract, not an omission\n\n'
 '| Authority | Finding | Locator |\n| --- | --- | --- |\n'
 '| `tmDeltas.TM601.pinRouteTable` | node set is SW, PGND, PMID, VBUS, VBAT, VDRV, V1P5, AGND — **there is no BST node at all**, so the item declares no BST route and no BST `needsClosed` | contract rev 24 |\n'
 '| `tmDeltas.TM601.relaySet` | `[3,7,60,61,83,86,130,132,133,134,135,136,137,138,139,140,141,142,143,144,145,146,154,155]` — **contains neither 109 nor 110**, whereas TM600\'s set contains both | contract rev 24 |\n'
 '| `tmDeltas.TM601.ateStimulus` | `{vbat 4.2 V, pmid 9 V, vdrv 5 V}` only; **no bst2sw stimulus**, and `bst2sw` occurs **0** times in the whole TM601 delta | contract rev 24 |\n'
 '| `tmDeltas.TM601` text | its single "BST" string is the register field `D2A_BUBO_TM_LSON`, **not a powered rail** | contract rev 24 |\n'
 '| Connect map | the BST routes (`:42`/`:43`, `:268`/`:269`) are channel routes; this item drives SW (`:174`) and PGND (`:156`) and reaches no BST pin | `SCH-Connect-Map.txt` |\n\n'
 '**Why the distinction is physical, not pedantic:** the ACM200 bootstrap source only reaches BST when K110 is'
 ' closed — `S5_ACM200_FH18 -> K110(Relay-NC) -> PB0_F` (`:724`), `SH18 -> K110(NC) -> PB0_S` (`:725`), versus the'
 ' BST path `K109(ON) -> K110(ON) -> BST_F` (`:43`). TM601 never drives that rail, so actuating K109/K110 there would'
 ' be an unmotivated relay closure — exactly what the minimal-endpoint rule forbids — rather than a repair.\n\n'
 '### Minimal-endpoint discipline (verified item by item)\n\n'
 '(a) **Only contract-authorised relays added.** No relay outside TM600\'s `relaySet` and the BST `needsClosed` sets was'
 ' introduced: the closure is exactly `K109_BUSL1_PB0` + `K110_ACM18_BST` on the TM600 list, both of which are in'
 ' `tmDeltas.TM600.relaySet` and in the route table.\n'
 '(b) **No negative-list relay touched.** Executable-code check: `K87`/`K88`/`K89`/`K131`/`K132`/`K133` appear **nowhere**'
 ' in either SetOn list (those are the Relay-NC default-conducting parts and must stay un-actuated).\n'
 '(c) **No composite macro.** `K_FPVIH_TO_BST_B` and `K_FPVIL_TO_SW_B` occur **0** times in executable code, consistent'
 ' with ruling (ii) recording that route as unrealisable.\n\n')
anchor='## 3. Negative-list and composite-macro checks'
if 'PER-FUNCTION JUSTIFICATION' not in t:
    t=t.replace(anchor, add+anchor)
    open(p,'wb').write(t.encode('utf-8'))
r=open(p,'rb').read()
print('evidence doc %d B / %s'%(len(r),hashlib.sha256(r).hexdigest()))
print('per-function section present:','PER-FUNCTION JUSTIFICATION' in r.decode('utf-8'))
pay=os.path.join(d,'implementation-payload-TM600-TM601.cpp'); rp=open(pay,'rb').read()
print('payload %d B / %s'%(len(rp),hashlib.sha256(rp).hexdigest()))