# -*- coding: utf-8 -*-
"""List all visible windows with children - run when Power Off popup is visible"""
import win32gui, time

print("Scanning for popups...")
print("(Run this when the Power Off dialog is visible)")
print()

def scan(h,_):
    if not win32gui.IsWindowVisible(h): return
    t=win32gui.GetWindowText(h); c=win32gui.GetClassName(h)
    if t and len(t)>1:
        print(f"\n[Window] class='{c}' title='{t}' hwnd={h}")
        def child(ch,_2):
            ct=win32gui.GetWindowText(ch); cc=win32gui.GetClassName(ch)
            r=win32gui.GetWindowRect(ch)
            if ct or cc in ("TButton","TBitBtn","Button","TEdit","Edit","TComboBox","Static","TLabel"):
                print(f"  [Child] class='{cc}' text='{ct}' rect={r}")
        win32gui.EnumChildWindows(h,child,None)

win32gui.EnumWindows(scan, None)

print("\nDone.")
input()
