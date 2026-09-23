import sys,io,os,difflib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
a=open(os.path.join(d,'implementation-payload-TM600-TM601.cpp'),'rb').read().decode('utf-8-sig')
b=open(os.path.join(d,'implementation-payload-TM600-TM601.pulse2ms-variant.cpp'),'rb').read().decode('utf-8-sig')
la=[l for l in a.split('\n') if not l.strip().startswith('//')]
lb=[l for l in b.split('\n') if not l.strip().startswith('//')]
diff=[l for l in difflib.unified_diff(la,lb,lineterm='',n=0) if l.startswith(('+','-')) and not l.startswith(('+++','---'))]
print('CODE-line differences between delivered payload and variant:')
for l in diff: print('  ',l[:120])
print('total',len(diff))