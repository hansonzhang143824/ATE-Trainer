import subprocess
import os
import sys
import time

def start_sts8300(project_path=None, pgs_file=None):
    """
    启动AccoTEST STS8300测试软件
    
    参数:
        project_path: 项目路径，包含测试文件（如 .pgs 文件）
        pgs_file: 要加载的 PGS 测试程序文件路径
    """
    accotest_dir = r"C:\AccoTEST\AccoTEST System"
    control_exe = os.path.join(accotest_dir, "control.exe")
    testui_exe = os.path.join(accotest_dir, "testui.exe")
    
    if not os.path.exists(control_exe):
        print(f"错误: 找不到 control.exe: {control_exe}")
        return False
    
    if not os.path.exists(testui_exe):
        print(f"警告: 找不到 testui.exe: {testui_exe}")
    
    env = os.environ.copy()
    env["PATH"] = accotest_dir + ";" + env["PATH"]
    
    if project_path:
        env["STS_PROJECT_PATH"] = project_path
    
    print("=" * 60)
    print("AccoTEST STS8300 启动脚本")
    print("=" * 60)
    print(f"AccoTEST 安装目录: {accotest_dir}")
    print(f"项目路径: {project_path or '未指定'}")
    print(f"PGS文件: {pgs_file or '未指定'}")
    print("-" * 60)
    
    try:
        print("正在启动 STS8300 控制程序...")
        process = subprocess.Popen(
            [control_exe],
            env=env,
            cwd=accotest_dir,
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
        
        print(f"STS8300 已启动，进程ID: {process.pid}")
        print("-" * 60)
        print("提示:")
        print("  1. STS8300启动后，通过UI加载测试程序(.pgs文件)")
        print("  2. 测试代码DLL需要放置在项目目录下")
        print("  3. Sts8200Interface.dll 将自动被加载")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"启动失败: {e}")
        return False

def start_sts8300_with_pgs(pgs_file):
    """
    启动STS8300并尝试加载指定的PGS文件
    
    参数:
        pgs_file: PGS测试程序文件路径
    """
    if not os.path.exists(pgs_file):
        print(f"错误: PGS文件不存在: {pgs_file}")
        return False
    
    accotest_dir = r"C:\AccoTEST\AccoTEST System"
    testui_exe = os.path.join(accotest_dir, "testui.exe")
    
    if not os.path.exists(testui_exe):
        print(f"错误: 找不到 testui.exe: {testui_exe}")
        return False
    
    env = os.environ.copy()
    env["PATH"] = accotest_dir + ";" + env["PATH"]
    
    print("=" * 60)
    print("AccoTEST STS8300 启动脚本 (带PGS文件)")
    print("=" * 60)
    print(f"AccoTEST 安装目录: {accotest_dir}")
    print(f"PGS文件: {pgs_file}")
    print("-" * 60)
    
    try:
        print("正在启动 STS8300 TestUI...")
        process = subprocess.Popen(
            [testui_exe, pgs_file],
            env=env,
            cwd=accotest_dir,
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
        
        print(f"STS8300 TestUI 已启动，进程ID: {process.pid}")
        print("-" * 60)
        print("提示:")
        print("  1. TestUI启动后将自动加载指定的PGS文件")
        print("  2. 测试代码DLL需要与PGS文件在同一目录")
        print("  3. Sts8200Interface.dll 将自动被加载")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"启动失败: {e}")
        return False

if __name__ == "__main__":
    project_path = r"D:\Newtest\STS8300"
    
    pgs_files = []
    if os.path.exists(project_path):
        for file in os.listdir(project_path):
            if file.endswith(".pgs"):
                pgs_files.append(os.path.join(project_path, file))
    
    if len(pgs_files) == 1:
        print(f"找到PGS文件: {pgs_files[0]}")
        start_sts8300_with_pgs(pgs_files[0])
    elif len(pgs_files) > 1:
        print("找到多个PGS文件:")
        for i, pgs in enumerate(pgs_files):
            print(f"  {i+1}. {pgs}")
        print("请手动选择要加载的PGS文件")
        start_sts8300(project_path)
    else:
        print("未找到PGS文件，启动STS8300主程序")
        start_sts8300(project_path)