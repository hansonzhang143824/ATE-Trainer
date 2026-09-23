import sys,io,os,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
# 1) tighten the payload comment with the latching-relay nuance
p=os.path.join(d,'implementation-payload-TM600-TM601.cpp')
u=open(p,'rb').read().decode('utf-8-sig').replace('\r\n','\n')
old=('    // Closing K109/K110 here would therefore be an unmotivated relay actuation on a rail the item does not use.\n')
new=('    // Closing K109/K110 here would therefore be an unmotivated relay actuation on a rail the item does not use.\n'
 '    // Relay-contact nuance (knowledge/hardware/relays.md L3-31): K110 is a G6K-2G-Y DPDT LATCHING relay whose\n'
 '    // pins 2 and 7 are marked NO yet CONDUCT when unpowered ("默认 2-3 通、6-7 通"; the file warns this is the\n'
 '    // opposite of a spring relay). So the connect-map notation "K110(Relay-NC)" denotes the UN-ACTUATED path,\n'
 '    // i.e. K110(Relay-NC) -> PB0 is the state with K110 NOT set. Actuating K110 (SetOn) switches COM1 to pin 4\n'
 '    // and COM2 to pin 5, which is the leg that continues to BST_F. Hence: not actuated -> PB0, actuated -> BST.\n')
n=u.count(old); print('payload comment anchor matched:',n)
if n==1:
    u=u.replace(old,new)
    open(p,'wb').write(b'\xef\xbb\xbf'+u.replace('\n','\r\n').encode('utf-8'))
r=open(p,'rb').read()
print('payload %d B / %s'%(len(r),hashlib.sha256(r).hexdigest()))
# 2) add the same nuance to the evidence doc
e=os.path.join(d,'t40-tm601-bst-evidence.md')
t=open(e,'rb').read().decode('utf-8-sig')
anchor='## 4. A self-contradiction this exposed in my own artefact'
add=('## 3b. Relay-contact nuance (checked against the terminal diagram, not assumed)\n\n'
 'The terminal diagram `knowledge/hardware/relays.md` L3-31 documents the part as a **G6K-2G-Y, a DPDT\n'
 'LATCHING relay**, and states: *"默认 2-3 通、6-7 通；通电 3-4 通、6-5 通"* with the explicit warning\n'
 '*"磁保持继电器：标注 NO 的脚在默认无电时闭合，NC 脚在通电后才闭合。与普通弹簧继电器直觉相反！"*\n\n'
 'So the connect-map notation **`K110(Relay-NC)` means the UN-ACTUATED path** (it is the map\'s way of marking\n'
 'predicates that do not require a SetOn), not "a normally-closed contact" in the spring-relay sense. Reading it\n'
 'correctly: with `K110` **not** actuated the ACM200 S5 source follows `S5_ACM200_FH18 -> K110(Relay-NC) -> PB0_F`\n'
 '(`:724`) and never reaches BST; **actuating `K110`** moves COM1 to pin 4 / COM2 to pin 5, which is the leg that\n'
 'continues to `BST_F`. Conclusion **unchanged and confirmed by the diagram**: the drive is dangling unless `K110`\n'
 'is closed — and for TM601 nothing requires that, so the drive is removed.\n\n'
 'This nuance also retro-explains the negative-list rule: the same part type makes `K87/K88/K89` *conducting while\n'
 'un-actuated*, which is exactly why the rule is "never add them to the required-on set" rather than "force them open".\n\n')
if 'Relay-contact nuance' not in t:
    t=t.replace(anchor,add+anchor); open(e,'wb').write(t.encode('utf-8'))
rr=open(e,'rb').read()
print('evidence %d B / %s'%(len(rr),hashlib.sha256(rr).hexdigest()))