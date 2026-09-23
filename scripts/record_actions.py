"""
录制鼠标键盘操作 → 保存到文件 → 回放
F8: 开始/停止录制  ESC: 退出
"""
import json, time, sys
import keyboard as kb
from pynput import mouse

events = []
recording = False
start_time = 0
_last_key_time = 0  # debounce

def add_event(typ, **kwargs):
    t = round(time.time() - start_time, 3)
    e = {"type": typ, "time": t}
    e.update(kwargs)
    events.append(e)

def on_click(x, y, button, pressed):
    global recording
    if not recording: return
    action = "DOWN" if pressed else "UP"
    add_event("click", x=x, y=y, button=str(button), pressed=pressed)
    print(f"[{time.time()-start_time:.1f}s] {action} {button} ({x},{y})")

def on_key(e):
    global recording, _last_key_time
    if not recording: return

    t = time.time() - start_time
    # debounce (keyboard sends both scan_code and name events)
    if t - _last_key_time < 0.05:
        return
    _last_key_time = t

    k = e.name
    if len(k) == 1:
        add_event("key", key=k, action="type")
        print(f"[{t:.1f}s] TYPE '{k}'")
    else:
        add_event("key", key=k, action="press")
        print(f"[{t:.1f}s] KEY {k}")

# F8 toggle recording
def toggle_recording():
    global recording, events, start_time
    recording = not recording
    if recording:
        events = []
        start_time = time.time()
        print("\n*** RECORDING (F8 to stop) ***\n")
    else:
        print(f"\n*** STOPPED ({len(events)} events) ***")
        save = input("Save? (y/n): ").strip().lower()
        if save == 'y':
            fname = input("Filename [recorded.json]: ").strip() or "recorded.json"
            with open(fname, 'w') as f:
                json.dump(events, f, indent=2)
            print(f"Saved: {fname}")

print("=" * 60)
print("  Action Recorder v2")
print("  F8 = Start/Stop   ESC = Exit")
print("=" * 60)

kb.add_hotkey('f8', toggle_recording)
kb.add_hotkey('esc', lambda: sys.exit(0))
kb.hook(on_key)

m_listener = mouse.Listener(on_click=on_click)
m_listener.start()

print("Ready - press F8 to start recording")
kb.wait()
