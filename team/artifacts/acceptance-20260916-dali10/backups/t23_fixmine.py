import sys,io,os,re,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
# 1) input-confirmation table row 3 still says SetClamp(50,50)->delay_ms(2)->MeasureVI
p=os.path.join(d,'t5-input-confirmation.md'); t=open(p,'rb').read().decode('utf-8-sig')
o='`Set(FI,±1.0,FPVIe_1V,FPVIe_2A,FPVIe_RELAY_ON)` → `SetClamp(50,50)` → **`delay_ms(1)`**'
print('row3 form present:',o in t)
if o not in t:
    # find the actual row 3 text
    for i,l in enumerate(t.split('\n')):
        if 'verbatim call form' in l: print('  row3 line:',l[:260])
# 2) HASH-AUDIT: mark the schematic-ir value as historical (file has been rebuilt)
h=os.path.join(d,'HASH-AUDIT.md'); ht=open(h,'rb').read().decode('utf-8-sig')
if 'ad9859e9' in ht:
    ht=ht.replace('ad9859e9','ad9859e9 (SUPERSEDED — this figure was already historical when first quoted; see the standing warning at the top of this file)')
    open(h,'wb').write(ht.encode('utf-8'))
    print('HASH-AUDIT.md: marked ad9859e9 as superseded')
for n in ['t5-input-confirmation.md','HASH-AUDIT.md']:
    q=os.path.join(d,n); r=open(q,'rb').read()
    print('  %-32s %6d B %s'%(n,len(r),hashlib.sha256(r).hexdigest()))