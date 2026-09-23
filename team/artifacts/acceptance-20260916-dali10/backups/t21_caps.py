import sys,io,os,re
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
m=r'D:\PROJECT6-DALI\ForCodexDebug\source\SCH-Connect-Map.txt'
if not os.path.exists(m):
    import glob
    c=glob.glob(r'D:\PROJECT6-DALI\ForCodexDebug\**\SCH-Connect-Map.txt',recursive=True)
    print('search:',c[:3]); m=c[0] if c else None
if m:
    t=open(m,'rb').read().decode('utf-8-sig',errors='replace')
    print('using',m)
    for k in ['K44','K45','K57','K5_','VBUS_Cap','CAP_BST_SW']:
        hits=[l.strip() for l in t.split('\n') if k in l]
        print('  %-10s %d hit(s)'%(k,len(hits)))
        for h in hits[:2]: print('      ',h[:130])