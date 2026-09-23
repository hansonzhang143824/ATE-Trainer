"""
回放录制的操作
用法: python replay_actions.py [filename] [speed]
"""
import json, time, sys
from pynput.mouse import Button, Controller as Mouse
import keyboard as kb

mouse_ctrl = Mouse()

def replay(filename, speed=1.0):
    with open(filename) as f:
        events = json.load(f)

    print(f"Loaded {len(events)} events from {filename}, speed={speed}x")
    print("Starting in 3s...")
    time.sleep(3)

    prev_t = 0
    for i, e in enumerate(events):
        delay = (e["time"] - prev_t) / speed
        if delay > 0:
            time.sleep(delay)
        prev_t = e["time"]

        if e["type"] == "click":
            mouse_ctrl.position = (e["x"], e["y"])
            btn = Button.left if "left" in e.get("button","") else Button.right
            if e["pressed"]:
                mouse_ctrl.press(btn)
            else:
                mouse_ctrl.release(btn)
        elif e["type"] == "key":
            k = e["key"]
            try:
                kb.press_and_release(k)
            except:
                kb.write(k)

        print(f"[{i+1}/{len(events)}] {e['type']} {e.get('key', e.get('button', ''))}")

    print("Done.")

if __name__ == "__main__":
    fname = sys.argv[1] if len(sys.argv) > 1 else "recorded.json"
    speed = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0
    replay(fname, speed)
