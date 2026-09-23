import sys,io,re,os
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
p=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10\implementation-payload-TM600-TM601.cpp'
t=open(p,'rb').read().decode('utf-8-sig')
code=[l for l in t.split('\n') if not l.strip().startswith('//')]
# show the measure block of TM600
start=None
for i,l in enumerate(t.split('\n')):
    if 'Step 4: Measure' in l and 'TM600' not in l:
        start=i; break
lines=t.split('\n')
for i,l in enumerate(lines):
    if 'FPVI0.SetClamp' in l:
        print('--- context around SetClamp (TM600 block) ---')
        for j in range(i-6,i+14):
            if 0<=j<len(lines): print('%5d: %s'%(j+1,lines[j].rstrip()[:120]))
        break
print()
print('=== checks ===')
print('delay_ms(2) in code:',sum(l.count('delay_ms(2)') for l in code))
print('any delay AFTER the MeasureVI and BEFORE FI=0?')
idx=[i for i,l in enumerate(code) if 'MeasureVI(200' in l]
for i in idx:
    nxt=code[i+1:i+3]
    print('   after MeasureVI:',[x.strip()[:80] for x in nxt])
print('any delay_ms/ delay_us >2ms in code (excluding 0):',[l.strip()[:70] for l in code if re.search(r'delay_(ms|us)\((?!0\))',l) and not re.search(r'delay_(ms|us)\(([12]|200|2000|100|10|50)\)',l)])
print('clamp re-issued per function:',sum(1 for l in code if 'SetClamp' in l))
print('samples in code:',sum(1 for l in code if 'MeasureVI(200, 5, FPVIe_MV_X10)' in l))