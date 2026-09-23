import sys,io,os,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'implementation-payload-TM600-TM601.cpp')
u=open(p,'rb').read().decode('utf-8-sig')
print('=== current force lines (code) ===')
for i,l in enumerate(u.split('\n')):
    if 'Set(FI, 1.0' in l: print('  %d: %s'%(i+1,l.strip()[:120]))
old600='    FPVI0.Set(FI, 1.0, FPVIe_1V, FPVIe_2A, FPVIe_RELAY_ON);  // 1 A into PMID->SW, ramp 1 ms'
new600=('    // Sign derivation (captain ruling, contract signConventionFinding step3): step1 alias direction\n'
        '    // pmid2sw = PMID->SW; step2 instrument terminals = HIGH->PMID (K83), LOW->SW (K60,K61);\n'
        '    // step3 assumed convention positive FI drives current OUT of the HIGH terminal => +1 A gives\n'
        '    // the DFT literal PMID->SW. The convention itself is U11 bring-up verification, not an\n'
        '    // established fact (no header or manual in this workspace states it).\n'
        '    FPVI0.Set(FI, 1.0, FPVIe_1V, FPVIe_2A, FPVIe_RELAY_ON);   // +1 A (DFT literal), ramp 1 ms')
old601='    FPVI0.Set(FI, 1.0, FPVIe_1V, FPVIe_2A, FPVIe_RELAY_ON);  // 1 A into SW->PGND, ramp 1 us'
new601=('    // Sign derivation (captain ruling, contract signConventionFinding step3): step1 alias direction\n'
        '    // sw2pgnd = SW->PGND; step2 instrument terminals = HIGH->PGND (K154,K155), LOW->SW (K60,K61);\n'
        '    // step3 with PGND on the HIGH terminal the commanded sign is the OPPOSITE of the DFT literal,\n'
        '    // so -1 A (DERIVED, not +1 A). MIRET is read through fabs(), so the magnitude is unaffected.\n'
        '    // U11 bring-up check: confirm the conducting device is the one BD-03 enables (0x5A=0x01 LS),\n'
        '    // that |MVRET|/|MIRET| lands near 7.5 mohm (not a ~0.6-0.7 V body-diode drop), and that\n'
        '    // |MIRET| matches the programmed value; if the driven device is wrong, flip the sign FOR THIS\n'
        '    // ITEM ONLY with hardware evidence (never a-priori).\n'
        '    FPVI0.Set(FI, -1.0, FPVIe_1V, FPVIe_2A, FPVIe_RELAY_ON);  // -1 A (derived), ramp 1 us')
n1=u.count(old600); n2=u.count(old601)
print('TM600 line matches:',n1,'| TM601 line matches:',n2)
if n1==1 and n2==1:
    u=u.replace(old600,new600).replace(old601,new601)
    open(p,'wb').write(b'\xef\xbb\xbf'+(u.replace('\r\n','\n').replace('\n','\r\n')).encode('utf-8'))
    print('applied')
raw=open(p,'rb').read(); v=raw.decode('utf-8-sig'); code=[l for l in v.split('\n') if not l.strip().startswith('//')]
print('payload %d B BOM=%s loneLF=%d'%(len(raw),raw[:3]==b'\xef\xbb\xbf',raw.count(b'\n')-raw.count(b'\r\n')))
print('sha256',hashlib.sha256(raw).hexdigest())
print('code FI lines:',[l.strip()[:70] for l in code if 'Set(FI, ' in l and 'RELAY_ON' in l])