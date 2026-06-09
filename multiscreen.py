#!/usr/bin/env python3
"""
Multi-screen manager for Turing Smart Screen.

Cycles through configured screens using keyboard shortcuts.
Screens and keybindings are configured in multiscreen.yaml.

Usage:
  python3 multiscreen.py
"""

import os
import signal
import subprocess
import sys
import time
import threading
from pathlib import Path

import re

import yaml
from pynput import keyboard

MAIN_DIR = Path(__file__).resolve().parent
CONFIG_PATH = MAIN_DIR / "config.yaml"
MULTISCREEN_CONFIG_PATH = MAIN_DIR / "multiscreen.yaml"
PYTHON = sys.executable

current_process = None
current_index = 0
switch_lock = threading.Lock()
screens = []
keybindings = {}


def load_multiscreen_config():
    global screens, keybindings
    with open(MULTISCREEN_CONFIG_PATH) as f:
        data = yaml.safe_load(f)
    screens = data.get("screens", [])
    raw_bindings = data.get("keybindings", {})

    keybindings = {}
    for action, combo_str in raw_bindings.items():
        keys = parse_combo(combo_str)
        if keys:
            keybindings[action] = keys

    if not screens:
        print("[multiscreen] ERROR: No screens defined in multiscreen.yaml")
        sys.exit(1)


def parse_combo(combo_str: str) -> frozenset:
    parts = [p.strip().lower() for p in combo_str.split("+")]
    key_set = set()
    for p in parts:
        mapped = KEY_MAP.get(p)
        if mapped:
            key_set.add(mapped)
        else:
            try:
                key_set.add(keyboard.KeyCode.from_char(p))
            except Exception:
                print(f"[multiscreen] WARNING: Unknown key '{p}' in combo '{combo_str}'")
    return frozenset(key_set)


KEY_MAP = {
    "ctrl": "ctrl",
    "ctrl_l": "ctrl",
    "ctrl_r": "ctrl",
    "shift": "shift",
    "shift_l": "shift",
    "shift_r": "shift",
    "alt": "alt",
    "alt_l": "alt",
    "alt_r": "alt",
    "home": keyboard.Key.home,
    "end": keyboard.Key.end,
    "page_up": keyboard.Key.page_up,
    "page_down": keyboard.Key.page_down,
    "insert": keyboard.Key.insert,
    "delete": keyboard.Key.delete,
    "f1": keyboard.Key.f1,
    "f2": keyboard.Key.f2,
    "f3": keyboard.Key.f3,
    "f4": keyboard.Key.f4,
    "f5": keyboard.Key.f5,
    "f6": keyboard.Key.f6,
    "f7": keyboard.Key.f7,
    "f8": keyboard.Key.f8,
    "f9": keyboard.Key.f9,
    "f10": keyboard.Key.f10,
    "f11": keyboard.Key.f11,
    "f12": keyboard.Key.f12,
    "f13": keyboard.Key.f13,
    "f14": keyboard.Key.f14,
    "f15": keyboard.Key.f15,
    "f16": keyboard.Key.f16,
    "f17": keyboard.Key.f17,
    "f18": keyboard.Key.f18,
    "f19": keyboard.Key.f19,
    "f20": keyboard.Key.f20,
    "up": keyboard.Key.up,
    "down": keyboard.Key.down,
    "left": keyboard.Key.left,
    "right": keyboard.Key.right,
    "space": keyboard.Key.space,
    "tab": keyboard.Key.tab,
    "enter": keyboard.Key.enter,
    "esc": keyboard.Key.esc,
    "escape": keyboard.Key.esc,
}


def normalize_key(key):
    if key in (keyboard.Key.ctrl_l, keyboard.Key.ctrl_r):
        return "ctrl"
    if key in (keyboard.Key.shift_l, keyboard.Key.shift_r):
        return "shift"
    if key in (keyboard.Key.alt_l, keyboard.Key.alt_r, keyboard.Key.alt_gr):
        return "alt"
    return key


def set_theme(theme_name: str):
    with open(CONFIG_PATH) as f:
        content = f.read()
    content = re.sub(r"(THEME:\s*)(\S+)", rf"\g<1>{theme_name}", content, count=1)
    with open(CONFIG_PATH, "w") as f:
        f.write(content)


def start_monitor(index: int):
    global current_process, current_index

    screen = screens[index]
    theme = screen["theme"]
    name = screen.get("name", theme)

    set_theme(theme)
    current_index = index

    env = os.environ.copy()
    current_process = subprocess.Popen(
        [PYTHON, str(MAIN_DIR / "main.py")],
        cwd=str(MAIN_DIR),
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    print(f"[multiscreen] Started: {name} (PID {current_process.pid})")


def stop_monitor():
    global current_process
    if current_process and current_process.poll() is None:
        current_process.send_signal(signal.SIGTERM)
        try:
            current_process.wait(timeout=8)
        except subprocess.TimeoutExpired:
            current_process.kill()
            current_process.wait()
        print(f"[multiscreen] Stopped PID {current_process.pid}")
    current_process = None


def switch_to(index: int):
    with switch_lock:
        if index == current_index and current_process and current_process.poll() is None:
            return
        index = index % len(screens)
        name = screens[index].get("name", screens[index]["theme"])
        print(f"[multiscreen] Switching to: {name}")
        stop_monitor()
        time.sleep(1)
        start_monitor(index)


pressed_keys = set()


def get_pressed_normalized():
    return frozenset(normalize_key(k) for k in pressed_keys)


def on_press(key):
    pressed_keys.add(key)
    current = get_pressed_normalized()

    for action, combo in keybindings.items():
        if combo.issubset(current):
            print(f"[multiscreen] Hotkey matched: {action}")
            if action == "next":
                target = (current_index + 1) % len(screens)
                threading.Thread(target=switch_to, args=(target,), daemon=True).start()
            elif action == "prev":
                target = (current_index - 1) % len(screens)
                threading.Thread(target=switch_to, args=(target,), daemon=True).start()
            elif action.startswith("screen_"):
                try:
                    idx = int(action.split("_", 1)[1])
                    if 0 <= idx < len(screens):
                        threading.Thread(target=switch_to, args=(idx,), daemon=True).start()
                except ValueError:
                    pass
            break


def on_release(key):
    pressed_keys.discard(key)


def main():
    load_multiscreen_config()

    print("[multiscreen] Turing Smart Screen - Multi-screen Manager")
    print(f"[multiscreen] {len(screens)} screen(s) configured:")
    for i, s in enumerate(screens):
        print(f"  [{i}] {s.get('name', s['theme'])} (theme: {s['theme']})")
    print()
    print("[multiscreen] Keybindings:")
    for action, combo_str in keybindings.items():
        raw = None
        with open(MULTISCREEN_CONFIG_PATH) as f:
            raw_data = yaml.safe_load(f)
        raw = raw_data.get("keybindings", {}).get(action, "")
        print(f"  {action}: {raw}")
    print()
    print("[multiscreen] CTRL+C to exit")
    print()

    start_monitor(0)

    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.start()

    try:
        while True:
            if current_process and current_process.poll() is not None:
                print("[multiscreen] Monitor process died, restarting...")
                time.sleep(2)
                start_monitor(current_index)
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[multiscreen] Shutting down...")
        stop_monitor()
        set_theme(screens[0]["theme"])
        listener.stop()
        print("[multiscreen] Bye!")


if __name__ == "__main__":
    main()
