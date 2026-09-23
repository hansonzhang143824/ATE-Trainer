import sys,io,os,re
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
h=open(r'D:\PROJECT6-DALI\ForCodexDebug\source\StdAfx.h','rb').read().decode('utf-8-sig',errors='replace')
print('=== verify t4\'s "composite closure spans domains" claim ===')
for pat in [r'#define\s+(K_FPVIH_TO_BST_A)\s+([^\r\n/]*)',
            r'#define\s+(K_FPVIH_TO_PGND_A)\s+([^\r\n/]*)',
            r'#define\s+(K_FPVIL_TO_BST_B)\s+([^\r\n/]*)',
            r'#define\s+(K_FPVIL_TO_SW_A)\s+([^\r\n/]*)',
            r'#define\s+(K_BST_ACM)\s+([^\r\n/]*)']:
    for m in re.finditer(pat,h):
        print('  %-22s = %s'%(m.group(1),m.group(2).strip()))
print()
print('  => K_FPVIH_TO_BST_A mixes K46/K48/K76 (ACM-ish 48/76 + 46 the SW1 pin):')
print('     "BST takes ACM200, SW takes FPVIe[L]" = t4\'s corrected reading; the only suspect item is the BST-side 110.')