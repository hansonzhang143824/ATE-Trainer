# -*- coding: utf-8 -*-
"""Mouse click + keyboard spy. Shows control under cursor + keypresses. ESC to exit."""
import win32gui, ctypes, time, sys

print("="*50)
print("Click + Keyboard Spy")
print("Click anywhere or type - see details below")
print("ESC to exit")
print("="*50)

last_pos = (0,0)

def get_control_at_point(x, y):
    hwnd = win32gui.WindowFromPoint((x, y))
    if not hwnd: return None, None
    parent = win32gui.GetAncestor(hwnd, 2)
    if not parent: parent = hwnd
    deepest = hwnd
    def walk(h, _):
        nonlocal deepest
        try:
            r = win32gui.GetWindowRect(h)
            if r[0] <= x <= r[2] and r[1] <= y <= r[3]: deepest = h
        except: pass
    try: win32gui.EnumChildWindows(parent, walk, None)
    except: pass
    return deepest, parent

def on_click(x, y):
    global last_pos
    if (x,y) == last_pos: return
    last_pos = (x,y)
    ctrl, root = get_control_at_point(x, y)
    print(f"\n>>> CLICK ({x},{y}):")
    if ctrl:
        ct = win32gui.GetWindowText(ctrl); cc = win32gui.GetClassName(ctrl)
        try: cr = win32gui.GetWindowRect(ctrl)
        except: cr = (0,0,0,0)
        print(f"    Control: [{cc}] '{ct}' hwnd={ctrl} rect={cr}")
    if root:
        rt = win32gui.GetWindowText(root); rc = win32gui.GetClassName(root)
        print(f"    Window:  [{rc}] '{rt}' hwnd={root}")

import keyboard as kb

def on_key(e):
    if e.event_type != 'down': return
    k = e.name
    print(f"  KEY: '{k}'  scan={e.scan_code}")

def on_mouse(e):
    if isinstance(e, kb.KeyboardEvent):
        on_key(e)
    elif hasattr(e, 'x') and hasattr(e, 'y'):
        if 'down' in str(getattr(e, 'event_type', '')):
            on_click(e.x, e.y)

kb.hook(on_key)
kb.add_hotkey('esc', lambda: sys.exit(0))

# Also hook mouse via pynput
from pynput.mouse import Listener
def on_click_pynput(x, y, button, pressed):
    if pressed: on_click(x, y)

m = Listener(on_click=on_click_pynput)
m.start()

print("Ready - click or type, ESC to quit")
kb.wait()
