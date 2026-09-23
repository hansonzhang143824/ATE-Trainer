import sys,io,os,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
e=os.path.join(d,'t40-tm601-bst-evidence.md')
t=open(e,'rb').read().decode('utf-8-sig')
add=('## 0. STATUS AND PROVENANCE DISCIPLINE (read this first)\n\n'
 '**⚠ SEQUENCING DISCLOSURE.** t38 was executed **before** the captain forwarded the user\'s hold ruling ("落盘阻断", defer\n'
 't38 until the contract owner (t39) and rule-reviewer (t40) independently judge whether TM601\'s 5 V must reach BST). The\n'
 'removal below was therefore made **without waiting for those two determinations**. I am NOT reverting it, because a\n'
 'second unauthorised edit would compound the problem; the change is a **clean, self-contained deletion of three executable\n'
 'lines** and can be reverted by restoring them verbatim from the revision history in `t29-k110-evidence.md` section 6b if\n'
 'either determination concludes the drive must be completed instead. **Nothing has been landed**: the target tree still\n'
 'holds the t23 revision. Recorded so the captain can rule on it rather than discover it.\n\n'
 '**⚠ ESCALATION-DEPENDENT CONCLUSIONS.** Sections 1–3 below are my analysis. The two open questions the user reserved are:\n'
 '(i) **does TM601\'s 5 V need to reach BST?** and (ii) **is the dangling drive removed or completed?** My answer is "no / removed",\n'
 'but the user requires that judgement from **two independent parties**, so **treat my conclusion as a PROPOSAL pending t39 and t40**.\n\n'
 '### Fact / inference / unknown separation (required for the wiring claims)\n\n'
 '| Class | Statement | Basis |\n'
 '| --- | --- | --- |\n'
 '| **FACT (documentary)** | TM601 executed three ACM calls: 5 V drive, zero-return, RELAY_OFF | read from my own payload at the cited line numbers |\n'
 '| **FACT (documentary)** | TM601\'s SetOn closes no K109/K110 | same |\n'
 '| **FACT (documentary)** | `TM601.pinRouteTable` has no BST node; `TM601.relaySet` has neither 109 nor 110; `aliasResolution[3]` (bst2sw) `usedByTm` = TM600 and TM1205 only; the TM601 DFT row declares no `bst2sw` | read from `setup-contract.json` rev 24 and `DFT.csv` |\n'
 '| **FACT (documentary)** | the connect map records `S5_ACM200_FH18 -> K110(Relay-NC) -> PB0_F` (`:724`) and the S-side twin (`:725`); `:723` records `PB0_PWM1 需闭合: 无(默认导通)` | read from `SCH-Connect-Map.txt` |\n'
 '| **FACT (documentary)** | the part is a G6K-2G-Y DPDT **latching** relay whose NO-marked pins conduct when unpowered, so `(Relay-NC)` in the map denotes the **un-actuated** path | `knowledge/hardware/relays.md` L3-31 |\n'
 '| **INFERENCE (wiring, NOT bench-measured)** | therefore, with K110 un-actuated, the ACM200 S5 source follows **PB0_F/PB0_S** rather than BST | derived from the two documentary rows above; **no instrument measurement supports it** |\n'
 '| **INFERENCE (wiring, NOT bench-measured)** | consequently the t38 concern is **two-sided**: not only "BST never driven" but possibly "**PB0 driven instead**", since `:723` shows PB0_PWM1 is default-conducting | derived; the user records this as a *risk*, and I agree it is the more consequential direction |\n'
 '| **UNKNOWN** | whether PB0 carrying the ACM S5 source has any electrical consequence at the DUT (it may be a monitor pin with no load) | **not established by any source I hold**; requires bench or design confirmation |\n'
 '| **UNKNOWN** | whether the fixture hard-wires any ACM-to-BST path | the contract and connect map both require a relay closure, so no hard wire is documented — but a hard wire cannot be excluded from documents alone |\n\n'
 'Nothing in this document asserts a measured result. **A compile closed loop is not electrical sign-off.**\n\n')
anchor='## 1. CONCLUSION FIRST'
if 'STATUS AND PROVENANCE DISCIPLINE' not in t:
    t=t.replace(anchor, add+anchor)
    # also mark the conclusion as a proposal at the top of section 1
    t=t.replace('**Answer: No.** Under the current contract','**Answer: No. — PROPOSAL PENDING t39 AND t40** (see section 0). Under the current contract')
    open(e,'wb').write(t.encode('utf-8'))
r=open(e,'rb').read()
print('t40 evidence %d B / %s'%(len(r),hashlib.sha256(r).hexdigest()))
print('section 0 present:','STATUS AND PROVENANCE DISCIPLINE' in r.decode('utf-8'))
print('FACT/INFERENCE/UNKNOWN table present:','FACT (documentary)' in r.decode('utf-8'))