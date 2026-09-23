import sys,io,os,re
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
sch=open(r'D:\Newtest\DSH\ATE-Coding-Plat\project\DALI\SCH-Connect-Map.txt','rb').read().decode('utf-8-sig',errors='replace').split('\n')
print('=== verifying t4\'s cited SCH lines ===')
for ln in (42,43,268,269,270,672,673,674):
    print('  L%-4d %s'%(ln,sch[ln-1].strip()[:130]))
print()
print('=== verifying the deployed L6997 comment ===')
L=open(r'D:\PROJECT6-DALI\ForCodexDebug\source\test.cpp','rb').read().decode('utf-8-sig').split('\n')
print('  L6997| %s'%L[6996].strip()[:150])
print('  L7000| %s'%L[6999].strip()[:150])