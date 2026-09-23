import sys,io,hashlib,re
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
p=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10\implementation-payload-TM600-TM601.cpp'
raw=open(p,'rb').read(); t=raw.decode('utf-8-sig')
print('payload bytes',len(raw),'sha256',hashlib.sha256(raw).hexdigest())
cl=[l for l in t.split('\n') if not l.strip().startswith('//')]
print('--- code-level relay numbers used in SetOn ---')
for m in re.finditer(r'cbite\.SetOn\(([^)]*)\)', t):
    print('   ',m.group(1).strip())
print('--- forbidden numbers 87-91 as literals in code:', [n for n in ('87','88','89','90','91') if re.search(r'\b'+n+r'\b',' '.join(cl))])
print('--- names 87-91 in code:', [n for n in ('K87','K88','K89','K90','K91') if any(n in l for l in cl)])
print('--- composite macros in code:', [n for n in ('K_FPVIH_TO_','K_FPVIL_TO_') if any(n in l for l in cl)])
print('--- delay_ms(2) count:',sum(l.count('delay_ms(2)') for l in cl))