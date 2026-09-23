"""
侦查 STS8300 Control 窗口结构 — 列出所有控件
用法: 先手动打开 Control 并登录，然后双击 run_spy.bat
"""
import pywinauto
import subprocess
import os
import time

ACCOTEST_DIR = r"C:\AccoTEST\AccoTEST System"

def print_tree(elem, indent=0):
    """递归打印控件树"""
    try:
        texts = []
        try: texts.append(elem.window_text())
        except: pass
        try: texts.append(elem.element_info.class_name)
        except: pass
        try: texts.append(f"id={elem.element_info.control_id}")
        except: pass
        try:
            rect = elem.rectangle()
            texts.append(f"({rect.left},{rect.top})-({rect.right},{rect.bottom})")
        except: pass

        line = "  " * indent + "|-- " + " | ".join(str(t) for t in texts if t)
        print(line)
    except:
        pass

    try:
        for child in elem.children():
            print_tree(child, indent + 1)
    except:
        pass


def start_control():
    env = os.environ.copy()
    env["PATH"] = ACCOTEST_DIR + ";" + env.get("PATH", "")
    subprocess.Popen([os.path.join(ACCOTEST_DIR, "control.exe")],
                     env=env, cwd=ACCOTEST_DIR,
                     creationflags=subprocess.CREATE_NEW_CONSOLE)
    time.sleep(5)


def spy():
    print("=" * 60)
    print("  STS8300 Window Spy")
    print("=" * 60)
    print()

    # 列出所有顶层窗口
    print("[All top-level windows]")
    print("-" * 40)
    for w in pywinauto.findwindows.find_windows():
        try:
            handle = w
            text = pywinauto.findwindows.find_window(handle=handle)
            print(f"  hwnd={handle}  title='{text}'")
        except:
            pass

    print()
    print("-" * 40)

    # 尝试找到 Control 窗口
    try:
        app = pywinauto.Application().connect(title_re=".*Control.*|.*Acco.*|.*STS.*|.*ACCO.*")
        dlg = app.top_window()
        print(f"\n[Found window: {dlg.window_text()}]")
        print(f"Class: {dlg.element_info.class_name}")
        print()
        print("=== Control Tree ===")
        print_tree(dlg)
    except Exception as e:
        print(f"\nControl window not found: {e}")
        print("Trying all visible windows...")
        for w in pywinauto.findwindows.find_windows():
            try:
                app = pywinauto.Application().connect(handle=w)
                dlg = app.top_window()
                title = dlg.window_text()
                if title:
                    print(f"\n=== {title} ===")
                    print_tree(dlg)
            except:
                pass

    print()
    input("Press Enter...")


if __name__ == "__main__":
    spy()
