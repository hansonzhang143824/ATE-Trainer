# -*- coding: utf-8 -*-
try:
    import sys, os, time

    # Check control.exe
    result = os.popen('tasklist /fi "imagename eq control.exe" /fo csv').read()
    print(result.strip())

    # Test 1: pywinauto find_windows
    print("\n=== Test 1: pywinauto.findwindows.find_windows() ===")
    from pywinauto import findwindows
    try:
        hwnds = findwindows.find_windows()
        print(f"  Result: {len(hwnds)} handles")
        for h in hwnds[:10]:
            try:
                n = findwindows.find_window(handle=h)
                print(f"  '{n}'")
            except:
                pass
    except Exception as e:
        print(f"  ERROR: {e}")

    # Test 2: pywinauto Desktop
    print("\n=== Test 2: Desktop(backend='win32').windows() ===")
    try:
        from pywinauto import Desktop
        d = Desktop(backend="win32")
        ws = d.windows()
        print(f"  Result: {len(ws)} windows")
        for w in ws[:10]:
            try:
                print(f"  '{w.window_text()}'")
            except:
                pass
    except Exception as e:
        print(f"  ERROR: {e}")

    # Test 3: win32gui
    print("\n=== Test 3: win32gui.EnumWindows ===")
    try:
        import win32gui
        visible = []
        def cb(h, _):
            if win32gui.IsWindowVisible(h):
                t = win32gui.GetWindowText(h)
                if t and len(t.strip()) > 1:
                    visible.append((h, t, win32gui.GetClassName(h)))
        win32gui.EnumWindows(cb, None)
        print(f"  Visible with title: {len(visible)}")
        for h, t, c in visible[:20]:
            print(f"  hwnd={h} class='{c}' '{t}'")
    except Exception as e:
        print(f"  ERROR: {e}")

    print("\nDone.")

except Exception as e:
    print(f"FATAL: {e}")
    import traceback
    traceback.print_exc()
finally:
    input("\nPress Enter to exit...")
