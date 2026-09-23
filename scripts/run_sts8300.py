"""
STS8300 启动脚本 — 启动软件 + 载入工程 + 打开 VS Project
之后用户手动: 编译 -> Debug -> 单测
用法: 双击 run_sts8300.bat
"""
import subprocess
import os
import sys
import time

ACCOTEST_DIR = r"C:\AccoTEST\AccoTEST System"
CONTROL_EXE  = os.path.join(ACCOTEST_DIR, "control.exe")
TESTUI_EXE   = os.path.join(ACCOTEST_DIR, "testui.exe")
VCEDITOR_EXE = os.path.join(ACCOTEST_DIR, "Programming_UI.exe")
PGS_FILE     = r"D:\PROJECT5-BOSTON\P68101\F68101-V0P2\F68101-FT.pgs"

# ============================================================
def check():
    errors = []
    for name, path in [
        ("AccoTEST dir", ACCOTEST_DIR),
        ("control.exe", CONTROL_EXE),
        ("testui.exe",  TESTUI_EXE),
        ("PGS file",    PGS_FILE),
    ]:
        if not os.path.exists(path):
            errors.append(f"{name}: {path}")
    if errors:
        for e in errors:
            print(f"[ERROR] Not found: {e}")
        return False
    return True

def start():
    env = os.environ.copy()
    env["PATH"] = ACCOTEST_DIR + ";" + env.get("PATH", "")

    # [1] Control
    print("[1] Starting Control...")
    subprocess.Popen([CONTROL_EXE], env=env, cwd=ACCOTEST_DIR,
                     creationflags=subprocess.CREATE_NEW_CONSOLE)
    time.sleep(3)

    # [2] TestUI + PGS
    print("[2] Starting TestUI with PGS...")
    print(f"    {PGS_FILE}")
    subprocess.Popen([TESTUI_EXE, PGS_FILE], env=env, cwd=ACCOTEST_DIR,
                     creationflags=subprocess.CREATE_NEW_CONSOLE)
    time.sleep(2)

    # [3] VS Project editor
    if os.path.exists(VCEDITOR_EXE):
        print("[3] Opening VS Project editor...")
        subprocess.Popen([VCEDITOR_EXE], env=env, cwd=ACCOTEST_DIR,
                         creationflags=subprocess.CREATE_NEW_CONSOLE)
    else:
        print("[3] VS Project editor not found, skip")

    print()
    print("=" * 60)
    print("  STS8300 已启动")
    print("  请手动操作: 编译 -> Debug -> SingleTest")
    print("=" * 60)

# ============================================================
def main():
    print("=" * 60)
    print("  STS8300 Launcher")
    print("=" * 60)
    if not check():
        print("[FATAL] 环境检查失败")
        input("Press Enter...")
        sys.exit(1)
    start()
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
