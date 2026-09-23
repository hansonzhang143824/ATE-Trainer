import sys,io,os,re
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
t=open(os.path.join(d,'review-handoff-note-plan-side.md'),'rb').read().decode('utf-8-sig').split('\n')
print('=== is the OPERATIVE sentence (the one the READING NOTE points to) where they say? ===')
ri=[i for i,l in enumerate(t) if 'READING NOTE' in l][0]
print('  READING NOTE at L%d.'%(ri+1))
# find the nearest preceding "{48,60,61,76,83}" sentence
for j in range(ri-1,max(0,ri-30),-1):
    if '{48,60,61,76,83}' in t[j]:
        print('  nearest preceding operative sentence with the correct set is at L%d (i.e. %d lines above):'%(j+1,ri-j))
        print('   ',t[j].strip()[:180]); print('   ',t[j+1].strip()[:180] if j+1<len(t) else '')
        break
print()
print('=== so: does the READING NOTE point at the right place? ===')
print('  the note says "the operative sentence is the one immediately above"')
print('  L%d (immediately above) = %s'%(ri, t[ri-1].strip()[:150]))
print('  is that the correct-set sentence?', '{48,60,61,76,83}' in t[ri-1])
print()
print('=== and their claim of "occurs exactly once" against the file ===')
print('  "is to become" total = %d  (L532 the note itself, L536 the quotation)'%sum(1 for l in t if 'is to become' in l))