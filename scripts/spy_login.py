# -*- coding: utf-8 -*-
"""侦查登录框所有子控件"""
try:
    import win32gui, time, os

    # Check control.exe running
    r = os.popen('tasklist /fi "imagename eq control.exe" /fo csv').read()
    if 'control.exe' not in r:
        print("Open STS8300 Control first!")
        input("Press Enter..."); exit(1)

    # Find login dialog
    login_hwnd = None
    def find_login(h, _):
        global login_hwnd
        if win32gui.IsWindowVisible(h) and win32gui.GetWindowText(h) == "AccoTEST System Login":
            login_hwnd = h
    win32gui.EnumWindows(find_login, None)

    if not login_hwnd:
        print("Login dialog not found!")
        input("Press Enter..."); exit(1)

    print(f"Login dialog: hwnd={login_hwnd}")
    print(f"Title: '{win32gui.GetWindowText(login_hwnd)}'")
    print(f"Class: '{win32gui.GetClassName(login_hwnd)}'")
    rect = win32gui.GetWindowRect(login_hwnd)
    print(f"Rect: {rect}")
    print()

    # ALL child controls (no filter)
    print("=== ALL child controls ===")
    def enum_all(h, _):
        t = win32gui.GetWindowText(h)
        c = win32gui.GetClassName(h)
        r = win32gui.GetWindowRect(h)
        print(f"  hwnd={h} class='{c}' text='{t}' rect=({r[0]},{r[1]})-({r[2]},{r[3]})")
    win32gui.EnumChildWindows(login_hwnd, enum_all, None)

    print("\nDone.")
except Exception as e:
    print(f"FATAL: {e}")
    import traceback
    traceback.print_exc()
finally:
    input("\nPress Enter...")
