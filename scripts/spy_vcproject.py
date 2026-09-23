# -*- coding: utf-8 -*-
"""侦查 "打开" 文件对话框"""
try:
    import win32gui, ctypes, time

    # Find the Open dialog
    hwnd = None
    def find_dlg(h, _):
        global hwnd
        if win32gui.IsWindowVisible(h):
            t = win32gui.GetWindowText(h)
            c = win32gui.GetClassName(h)
            if c == "#32770" and ("打开" in t or "Open" in t):
                hwnd = h
    win32gui.EnumWindows(find_dlg, None)

    if not hwnd:
        # Try to find the PGS selection window specifically
        def find_any(h, _):
            if win32gui.IsWindowVisible(h):
                t = win32gui.GetWindowText(h)
                c = win32gui.GetClassName(h)
                if t and len(t) > 1:
                    print(f"  class='{c}' title='{t}'")
        print("Open dialog not found. All visible windows:")
        win32gui.EnumWindows(find_any, None)
    else:
        t = win32gui.GetWindowText(hwnd)
        c = win32gui.GetClassName(hwnd)
        r = win32gui.GetWindowRect(hwnd)
        print(f"Found: class='{c}' title='{t}' hwnd={hwnd} rect={r}")
        print()
        print("=== All child controls ===")
        def enum_child(ch, _):
            ct = win32gui.GetWindowText(ch)
            cc = win32gui.GetClassName(ch)
            cr = win32gui.GetWindowRect(ch)
            print(f"  hwnd={ch} [{cc}] '{ct}' rect=({cr[0]},{cr[1]},{cr[2]},{cr[3]})")
        win32gui.EnumChildWindows(hwnd, enum_child, None)

    print("\nDone.")
except Exception as e:
    print(f"FATAL: {e}")
    import traceback
    traceback.print_exc()
finally:
    input("\nPress Enter...")
