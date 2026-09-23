import sys
f=open(sys.argv[1],'r',encoding='utf-8')
c=f.read(); f.close()

# 1. After VC Project click, reduce 3s to 1s before file dialog
c=c.replace("real_click(vc); print(\"  Clicked\")\n    time.sleep(3); click_ok()",
            "real_click(vc); print(\"  Clicked\")\n    time.sleep(1); click_ok()")

# 2. After main window found, remove extra clicks - go straight to VC Project step
# Already fine since we removed the 5s sleep earlier

# 3. After login + PowerOff click, the main window polling already runs at 0.5s intervals - good

f=open(sys.argv[1],'w',encoding='utf-8')
f.write(c); f.close()
print('Speed patched')
