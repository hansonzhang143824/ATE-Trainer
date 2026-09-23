import sys,io,os,re
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
base=r'D:\Newtest\DSH\ATE-Coding-Plat'
cm=os.path.join(base,'project','DALI','SCH-Connect-Map.txt')
t=open(cm,'rb').read().decode('utf-8-sig',errors='replace').split('\n')
print('=== every line mentioning SW (node-level) with needsClosed ===')
for i,l in enumerate(t):
    if re.search(r'\bSW\b|\bSW1\b|\bSW2\b',l) and ('需闭合' in l or 'Kelvin' in l or 'Relay' in l):
        print('  %4d: %s'%(i+1,l.strip()[:140]))
print()
print('=== K60 / K61 definitions and routes ===')
for i,l in enumerate(t):
    if re.search(r'\bK60\b|\bK61\b|\bK49\b',l): print('  %4d: %s'%(i+1,l.strip()[:140]))