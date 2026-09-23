# -*- coding: utf-8 -*-
"""Read VS status bar / Output window text to detect build status"""
import win32gui

# Find VS window
vs_hwnd = [None]
def find_vs(h,_):
    if win32gui.IsWindowVisible(h):
        t=win32gui.GetWindowText(h); c=win32gui.GetClassName(h)
        if "F68101" in t and (c.startswith("HwndWrapper") or c=="Ghost"):
            vs_hwnd[0]=h
win32gui.EnumWindows(find_vs,None)

if not vs_hwnd[0]:
    print("VS window not found!")
    input(); exit()

print("VS window: %s" % win32gui.GetWindowText(vs_hwnd[0]))
print()

# Find status bar and all text-containing children
print("=== Status bars and text controls ===")
def scan(h,_):
    t=win32gui.GetWindowText(h); c=win32gui.GetClassName(h)
    if t and len(t)>1:
        print("  [%s] '%s'" % (c, t))
    # Also look for status bar
    if c in ("msctls_statusbar32", "OleStatusBar", "WPF StatusBar"):
        print("  FOUND status bar: [%s]" % c)
        def scan_parts(ch,_2):
            pt=win32gui.GetWindowText(ch)
            if pt: print("    Part: '%s'" % pt)
        win32gui.EnumChildWindows(h, scan_parts, None)
win32gui.EnumChildWindows(vs_hwnd[0], scan, None)

print("\nDone.")
input()
