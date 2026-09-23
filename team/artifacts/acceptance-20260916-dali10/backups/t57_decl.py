import sys,io,os,hashlib,time
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'implementation-payload-TM600-TM601.cpp')
r=open(p,'rb').read()
h=hashlib.sha256(r).hexdigest()
print('=== STANDALONE CONFIRMABLE FACT, measured now ===')
print('  path   : team/artifacts/acceptance-20260916-dali10/implementation-payload-TM600-TM601.cpp')
print('  size   : %d B'%len(r))
print('  sha256 : %s'%h)
print('  mtime  : %s'%time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(os.stat(p).st_mtime)))
print('  still frozen at 66abc088:', h=='66abc088ae6bd5f9b9d7201673003fc0be2450fd6f1f222c6a4a902cbe4f0cc4')
print()
print('=== the full version chain with who/why (for their ledger) ===')
for sz,hh,when,who,why in [
 (38147,'272667f3…','t29','me (ate-implementer)','K109/K110 added + TM601 per-function justification'),
 (39457,'2d0984d9…','19:55:59','me','t38: removed the TM601 dangling ACM drive'),
 (41797,'6034af71…','20:48:18','me','t50 union: added K48/K76, kept K109/K110 (captain-authorised)'),
 (42998,'c03632d9…','20:59:12','me','captain one-time unfreeze: REMOVED K109/K110, withdrew --check-extra disable'),
 (43806,'66abc088…','21:09:24','me','third comment item: two-case operational fact + superseded markers; then captain STOP-WRITING order froze it')]:
    print('  %-6d %-12s %-9s %-20s %s'%(sz,hh,when,who,why))