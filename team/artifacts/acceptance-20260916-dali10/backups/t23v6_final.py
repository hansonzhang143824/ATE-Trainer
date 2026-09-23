import sys,io,os,re,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
base=r'D:\Newtest\DSH\ATE-Coding-Plat'
d=os.path.join(base,'team','artifacts','acceptance-20260916-dali10')
p=os.path.join(d,'implementation-payload-TM600-TM601.cpp')
pay=open(p,'rb').read().decode('utf-8-sig'); r=open(p,'rb').read()
code=[l for l in pay.split('\n') if not l.strip().startswith('//')]
print('FINAL payload %d B / %s'%(len(r),hashlib.sha256(r).hexdigest()))
print('invariants: delay_ms(1)=%d delay_ms(2)=%d SetClamp=%d MeasureVI=%d ramp=%d bare126=%d ERROR_RES=%d literal9999=%d'%(
 sum(l.count('delay_ms(1)') for l in code),sum(l.count('delay_ms(2)') for l in code),
 sum(l.count('SetClamp(50, 50)') for l in code),sum(l.count('MeasureVI(200, 5, FPVIe_MV_X10)') for l in code),
 sum(l.count('rampi_capv')+l.count('rampv_capv') for l in code),sum(1 for l in code if ', 126,' in l),
 sum(l.count('ERROR_RES') for l in code),pay.count('9999')))
print('K44/K45/K5 in executable code:',sum(l.count('K44_Cap_SW2_BST2')+l.count('K45_Cap_SW1_BST1')+l.count('K5_VBUS_Cap') for l in code))
print('returns in code:',[l.strip() for l in code if 'return' in l],'| goto/break/continue:',sum(1 for l in code if re.search(r'\b(goto|break|continue|throw)\b',l)))
# rebuild sandbox + gates
tgt=os.path.join(r'D:\PROJECT6-DALI\ForCodexDebug','source','test.cpp')
cur=open(tgt,'rb').read().decode('utf-8-sig')
body=pay[pay.find('DUT_API int TM600_HS_RDSON'):]
s=cur.find('DUT_API int TM600_HS_RDSON'); pre=cur.rfind('\n//',0,s)
j=cur.find('DUT_API int TM601_LS_RDSON',s); e=cur.find('\nDUT_API int',j+10)
if e<0: e=len(cur)
patched=cur[:pre]+'\n'+body.rstrip('\n')+'\n'+(cur[e:] if e<len(cur) else '')
sbx=os.path.join(d,'gate-check-t21','source','test.cpp')
open(sbx,'w',encoding='utf-8',newline='').write(patched)
rb=open(sbx,'rb').read(); print('sandbox %d B / %s'%(len(rb),hashlib.sha256(rb).hexdigest()))