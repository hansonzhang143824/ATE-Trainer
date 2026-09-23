# -*- coding: utf-8 -*-
"""
STS8300 Deploy Agent - auto_sts8300.py
======================================
Full automation: Launch -> Login -> VC Project -> VS -> Build -> F5.
State detection (0-4) skips already-completed steps.

Usage:  python auto_sts8300.py [PGS_PATH] [PGS_NAME]
        Or double-click auto_sts8300.bat
"""
import subprocess, os, time, sys, ctypes, win32gui
from pynput.mouse import Button, Controller as Mouse
import input_guard

def main():
    ACCOTEST_DIR = r"C:\AccoTEST\AccoTEST System"
    CONTROL_EXE = os.path.join(ACCOTEST_DIR, "control.exe")
    WM_SETTEXT = 0x000C
    mouse = Mouse()

    # ---- PGS path/name ----
    if len(sys.argv) >= 3:
        PGS_PATH, PGS_NAME = sys.argv[1], sys.argv[2]
    else:
        PGS_PATH = input("Project path: ").strip() or r"D:\PROJECT5-BOSTON\P68101\F68101-V0P2"
        PGS_NAME = input("PGS filename: ").strip() or "F68101-FT.PGS"
    DLL_FILE = os.path.join(PGS_PATH, PGS_NAME.split("-")[0] + ".dll")
    print("  Path: %s\n  PGS:  %s\n  DLL:  %s" % (PGS_PATH, PGS_NAME, DLL_FILE))

    # ---- 屏蔽用户键鼠（ESC 中止），防止误触干扰自动化 ----
    input_guard.start()
    print(">> 键鼠已屏蔽，脚本模拟操作不受影响；按 ESC 可随时中止 <<")

    # ---- Utility functions ----
    def check_abort(stage=""):
        if input_guard.aborted():
            print("  !! 用户按下 ESC，中止自动化 (%s) !!" % stage)
            input_guard.stop()
            print(">> 键鼠屏蔽已解除 <<")
            sys.exit(1)
    def find_win(title):
        r = [None]
        def f(h, _):
            if win32gui.IsWindowVisible(h) and win32gui.GetWindowText(h) == title: r[0] = h
        win32gui.EnumWindows(f, None); return r[0]

    def find_child(parent, text=None, cls=None):
        r = [None]
        def f(h, _):
            if cls and win32gui.GetClassName(h) != cls: return
            if text and win32gui.GetWindowText(h) != text: return
            r[0] = h
        win32gui.EnumChildWindows(parent, f, None); return r[0]

    def real_click(hwnd):
        r = win32gui.GetWindowRect(hwnd)
        mouse.position = ((r[0] + r[2]) // 2, (r[1] + r[3]) // 2)
        time.sleep(0.2); mouse.click(Button.left)

    def click_ok():
        def f(h, _):
            if not win32gui.IsWindowVisible(h): return
            if win32gui.GetClassName(h) in ("#32770", "TMessageForm", "TForm", "TfmPower", "TfmLogin"):
                def g(ch, _2):
                    if win32gui.GetWindowText(ch) in ("OK", "Yes"): real_click(ch); print("  OK")
                win32gui.EnumChildWindows(h, g, None)
        win32gui.EnumWindows(f, None)

    def click_vs(h, _):
        if win32gui.IsWindowVisible(h):
            t = win32gui.GetWindowText(h); c = win32gui.GetClassName(h)
            if "F68101" in t and c.startswith("HwndWrapper"): real_click(h); print("  VS focused")

    def vs_open():
        r = [False]
        def f(h, _):
            if win32gui.IsWindowVisible(h):
                t = win32gui.GetWindowText(h); c = win32gui.GetClassName(h)
                if "F68101" in t and c.startswith("HwndWrapper"): r[0] = True
        win32gui.EnumWindows(f, None); return r[0]

    def get_vs_build_status():
        """Read VS status bar for build result (e.g. 'Build succeeded' / 'Build failed')."""
        r = [None]
        def find_main(h, _):
            if not win32gui.IsWindowVisible(h): return
            t = win32gui.GetWindowText(h); c = win32gui.GetClassName(h)
            if "F68101" in t and c.startswith("HwndWrapper"):
                def find_statusbar(ch, _2):
                    if win32gui.GetClassName(ch) == "msctls_statusbar32":
                        txt = win32gui.GetWindowText(ch)
                        if txt: r[0] = txt
                win32gui.EnumChildWindows(h, find_statusbar, None)
        win32gui.EnumWindows(find_main, None)
        return r[0]

    # ---- State detection (0=full, 4=F5 only) ----
    print("=" * 50); print("STS8300 Deploy"); print("=" * 50)
    dll_fresh = os.path.exists(DLL_FILE) and os.path.getmtime(DLL_FILE) > time.time() - 300
    state = 0
    if dll_fresh:              state = 4; print("[0] State 4: DLL fresh -> F5")
    elif vs_open():           state = 3; print("[0] State 3: VS open -> Build+F5")
    elif find_win("AccoTEST System Control"): state = 2; print("[0] State 2: Control open -> VC")
    elif find_win("AccoTEST System Login"):   state = 1; print("[0] State 1: Login open -> Login")
    else:                                     print("[0] State 0: Full flow")

    # ---- State 0: Launch ----
    if state <= 0:
        print("[1] Launch control.exe...")
        env = os.environ.copy(); env["PATH"] = ACCOTEST_DIR + ";" + env.get("PATH", "")
        subprocess.Popen([CONTROL_EXE], env=env, cwd=ACCOTEST_DIR,
                         creationflags=subprocess.CREATE_NEW_CONSOLE)
        for _ in range(40):
            time.sleep(0.5); check_abort("启动 control.exe")
            if find_win("AccoTEST System Login"): break

    # ---- State 0-1: Login ----
    if state <= 1:
        print("[2] Login...")
        login = find_win("AccoTEST System Login")
        if not login: print("ERROR: Login"); return
        combo = find_child(login, cls="Edit")   # Edit inside TComboBox (username)
        pw    = find_child(login, cls="TEdit")   # Password field
        btn   = find_child(login, text="Login")  # Login button
        import keyboard as kb
        if combo: real_click(combo); time.sleep(0.5)
        for ch in "admin": kb.press_and_release(ch); time.sleep(0.05)
        kb.press_and_release('enter')             # Select admin
        if pw: real_click(pw); time.sleep(0.3)
        kb.write("admin")                          # Type password
        if btn: real_click(btn)
        else: kb.press_and_release('enter')
        time.sleep(0.3); click_ok()                # Power Off popup

        print("[3] Main window...")
        for _ in range(20):
            time.sleep(0.5); check_abort("登录"); click_ok()
            if find_win("AccoTEST System Control"): break

    # ---- State 0-2: VC Project + PGS ----
    main = find_win("AccoTEST System Control")
    if not main: print("ERROR: Main window"); return

    if state <= 2:
        print("[4] VC Project...")
        vc = find_child(main, text="VC Project")
        if vc: real_click(vc)
        else: print("ERROR"); return
        time.sleep(1); click_ok()

        print("[5] Load PGS: " + PGS_NAME)
        import pyperclip
        pyperclip.copy(os.path.join(PGS_PATH, PGS_NAME))
        time.sleep(1)
        kb.press_and_release('alt+n'); time.sleep(0.3)   # Focus filename
        kb.press_and_release('ctrl+v'); time.sleep(0.5)  # Paste path
        kb.press_and_release('enter')                     # Open
        time.sleep(1); click_ok()

    # ---- State 0-3: Build ----
    if state <= 3:
        print("[6] Build...")
        time.sleep(8); click_ok()
        win32gui.EnumWindows(click_vs, None); time.sleep(1)
        old_mtime = os.path.getmtime(DLL_FILE) if os.path.exists(DLL_FILE) else 0
        import keyboard as kb2
        kb2.press_and_release('ctrl+shift+b')
        built = False
        for i in range(15):
            time.sleep(2); check_abort("compile"); click_ok()
            # Primary: DLL timestamp check
            if os.path.exists(DLL_FILE) and os.path.getmtime(DLL_FILE) > old_mtime + 1:
                print("  Build OK (%ds)" % ((i+1)*2)); built = True; break
            # Secondary: check VS status bar for failure text
            status = get_vs_build_status()
            if status and "failed" in status.lower():
                print("  VS Status: %s" % status)
                break
            print("  ...%ds" % ((i+1)*2))
        if not built:
            # One last status check for diagnostics
            status = get_vs_build_status()
            if status:
                print("  VS Status: %s" % status)
            print("  BUILD FAILED - check F68101.log for errors")
            input_guard.stop()
            print(">> keyboard/mouse unblocked <<")
            sys.exit(1)
        time.sleep(1)
    else:
        import keyboard as kb2

    # ---- State 0-4: F5 ----
    check_abort("F5 前")
    win32gui.EnumWindows(click_vs, None); time.sleep(0.5)
    kb2.press_and_release('f5')
    print("  F5 sent!\nDone.")
    input_guard.stop()
    print(">> 键鼠屏蔽已解除 <<")

if __name__ == "__main__":
    try:
        main()
    finally:
        input_guard.stop()
