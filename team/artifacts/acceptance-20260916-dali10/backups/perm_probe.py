import sys,io,os,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
probe=r'D:\PROJECT6-DALI\ForCodexDebug\source\__t5_perm_probe.tmp'
try:
    with open(probe,'wb') as f: f.write(b'x')
    print('WRITE PROBE: OK')
    with open(probe,'rb') as f: print('readback:',f.read())
    os.remove(probe)
    print('probe removed:', not os.path.exists(probe))
except Exception as e:
    print('WRITE PROBE: DENIED ->',type(e).__name__,e)