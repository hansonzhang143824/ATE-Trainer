# -*- coding: utf-8 -*-
"""
input_guard.py — 自动化执行期间屏蔽用户键鼠输入
================================================
原理:
  低级钩子 (WH_KEYBOARD_LL / WH_MOUSE_LL) 拦截所有"真实"键鼠输入。
  脚本自己用 SendInput (pynput / keyboard 库) 发出的模拟输入带
  LLKHF_INJECTED / LLMHF_INJECTED 标志，直接放行，不受影响。

唯一例外:
  用户按下 ESC → 置中止标志 (aborted() == True)。
  自动化主循环在安全点检测到后退出，输入屏蔽随之解除。

用法:
    import input_guard
    input_guard.start()
    try:
        ...                     # 自动化代码
        if input_guard.aborted():
            ...                 # 安全退出
    finally:
        input_guard.stop()

注意:
  - 钩子装在本模块创建的守护线程里，脚本退出/崩溃时钩子自动销毁，
    不会残留屏蔽状态。
  - Ctrl+Alt+Del 属于安全注意序列，Windows 不允许任何程序屏蔽。
"""
import ctypes
import threading
from ctypes import wintypes

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

WH_KEYBOARD_LL = 13
WH_MOUSE_LL = 14
WM_KEYDOWN = 0x0100
WM_SYSKEYDOWN = 0x0104
WM_QUIT = 0x0012
VK_ESCAPE = 0x1B
LLKHF_INJECTED = 0x10   # KBDLLHOOKSTRUCT.flags: 事件由 SendInput 注入
LLMHF_INJECTED = 0x01   # MSLLHOOKSTRUCT.flags: 事件由 SendInput 注入


class KBDLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [("vkCode", wintypes.DWORD),
                ("scanCode", wintypes.DWORD),
                ("flags", wintypes.DWORD),
                ("time", wintypes.DWORD),
                ("dwExtraInfo", ctypes.c_size_t)]


class MSLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [("pt", wintypes.POINT),
                ("mouseData", wintypes.DWORD),
                ("flags", wintypes.DWORD),
                ("time", wintypes.DWORD),
                ("dwExtraInfo", ctypes.c_size_t)]


# 64 位下 WPARAM/LPARAM 都是指针宽度，不能用 wintypes 里可能为 32 位的定义
HOOKPROC = ctypes.WINFUNCTYPE(ctypes.c_ssize_t,
                              ctypes.c_int,
                              ctypes.c_size_t,   # WPARAM
                              ctypes.c_ssize_t)  # LPARAM

user32.SetWindowsHookExW.restype = ctypes.c_void_p
user32.SetWindowsHookExW.argtypes = [ctypes.c_int, HOOKPROC,
                                     ctypes.c_void_p, wintypes.DWORD]
user32.CallNextHookEx.restype = ctypes.c_ssize_t
user32.CallNextHookEx.argtypes = [ctypes.c_void_p, ctypes.c_int,
                                  ctypes.c_size_t, ctypes.c_ssize_t]

_abort_event = threading.Event()
_started_event = threading.Event()
_hook_thread = None
_thread_id = None
_hook_handles = []

# 回调引用必须常驻，防止被 GC 回收后钩子崩溃
_kb_proc_ref = None
_mouse_proc_ref = None


def _kb_proc(nCode, wParam, lParam):
    """键盘钩子：放行注入输入；真实输入全部吞掉；ESC 置中止标志。"""
    if nCode == 0:  # HC_ACTION
        kb = ctypes.cast(lParam, ctypes.POINTER(KBDLLHOOKSTRUCT)).contents
        if not (kb.flags & LLKHF_INJECTED):
            if kb.vkCode == VK_ESCAPE and wParam in (WM_KEYDOWN, WM_SYSKEYDOWN):
                _abort_event.set()
            return 1  # 吞掉真实按键（包括 ESC，避免误触 VS/对话框）
    return user32.CallNextHookEx(None, nCode, wParam, lParam)


def _mouse_proc(nCode, wParam, lParam):
    """鼠标钩子：放行注入输入；真实鼠标移动/点击全部吞掉。"""
    if nCode == 0:
        ms = ctypes.cast(lParam, ctypes.POINTER(MSLLHOOKSTRUCT)).contents
        if not (ms.flags & LLMHF_INJECTED):
            return 1
    return user32.CallNextHookEx(None, nCode, wParam, lParam)


def _hook_loop():
    """钩子安装线程：低级钩子的回调在本线程消息循环里分发。"""
    global _thread_id
    _thread_id = kernel32.GetCurrentThreadId()
    hmod = kernel32.GetModuleHandleW(None)
    h_kb = user32.SetWindowsHookExW(WH_KEYBOARD_LL, _kb_proc_ref, hmod, 0)
    h_ms = user32.SetWindowsHookExW(WH_MOUSE_LL, _mouse_proc_ref, hmod, 0)
    _hook_handles.extend([h_kb, h_ms])
    if not h_kb or not h_ms:
        print("!! input_guard: 钩子安装失败（可能被安全软件拦截），"
              "自动化将继续运行但输入未屏蔽 !!")
    _started_event.set()

    msg = wintypes.MSG()
    while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) > 0:
        user32.TranslateMessage(ctypes.byref(msg))
        user32.DispatchMessageW(ctypes.byref(msg))

    for h in _hook_handles:
        if h:
            user32.UnhookWindowsHookEx(ctypes.c_void_p(h))


def start():
    """开始屏蔽用户键鼠输入（ESC 除外，ESC = 中止信号）。"""
    global _hook_thread, _kb_proc_ref, _mouse_proc_ref
    if _hook_thread is not None:
        return
    _kb_proc_ref = HOOKPROC(_kb_proc)
    _mouse_proc_ref = HOOKPROC(_mouse_proc)
    _abort_event.clear()
    _hook_thread = threading.Thread(target=_hook_loop, daemon=True,
                                    name="input_guard")
    _hook_thread.start()
    _started_event.wait(5)


def stop():
    """解除屏蔽。脚本正常退出、异常退出、ESC 中止时都会走到。"""
    global _hook_thread, _thread_id
    if _hook_thread is None:
        return
    if _thread_id:
        user32.PostThreadMessageW(wintypes.DWORD(_thread_id),
                                  WM_QUIT, 0, 0)
    _hook_thread.join(5)
    _hook_thread = None
    _thread_id = None


def aborted():
    """用户是否按下了 ESC。"""
    return _abort_event.is_set()
