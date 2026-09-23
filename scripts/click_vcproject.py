"""
点击 STS8300 Control 界面的 VC Project 按钮
用法: 先启动 Control 并登录, 然后 python click_vcproject.py
"""
import time
from pywinauto import Application

# 连接到已运行的 Control
app = Application(backend="win32").connect(
    title="AccoTEST System Control",
    class_name="8200 TESTER CONTROL"
)
dlg = app.window()

# 打印所有按钮（确认）
print("Buttons found:")
for btn in dlg.descendants():
    if btn.element_info.class_name == "TBitBtn":
        print(f"  {btn.window_text():20s}  id={btn.element_info.control_id}")

# 点击 VC Project
print("\nClicking 'VC Project'...")
vc = dlg.child_window(title="VC Project", class_name="TBitBtn")
vc.click()
print("Done.")
time.sleep(1)

# 点击 StationA (启动 TestUI)
print("Clicking 'StationA'...")
sta = dlg.child_window(title="StationA", class_name="TBitBtn")
sta.click()
print("Done.")
