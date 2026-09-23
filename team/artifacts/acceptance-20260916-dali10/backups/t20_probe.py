import sys,io,os,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
probe=r'D:\PROJECT6-DALI\ForCodexDebug\source\__t20_probe.tmp'
try:
    with open(probe,'wb') as f: f.write(b'x')
    print('WRITE PROBE: OK')
    print('readback:',open(probe,'rb').read())
    os.remove(probe)
    print('cleaned up:',not os.path.exists(probe))
except Exception as e:
    print('WRITE PROBE: DENIED ->',type(e).__name__,e)
    print('file created?',os.path.exists(probe))