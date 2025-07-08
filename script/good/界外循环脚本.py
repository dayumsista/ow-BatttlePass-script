TARGET_UUID = "14BEE4D1-55A9-D67D-C8A1-5811224899A9"
import pyautogui
import time
import threading
import tkinter as tk
import sys
import os
import psutil
from PIL import Image, ImageDraw
import keyboard
import wmi
import configparser
import logging

logging.basicConfig(level=logging.INFO)

stop_flag = threading.Event()
running = False
pyautogui.FAILSAFE = False
execution_count = 0
execution_lock = threading.Lock()

def get_base_path():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))

config = configparser.ConfigParser()
config_path = os.path.join(get_base_path(), 'config.ini')
config.read(config_path)

try:
    extra_time_sleep = float(config.get('Settings', 'extra_time_sleep').strip().replace("\x00", ""))
except ValueError as e:
    print(f"Error in config values: {e}")
    sys.exit(1)

def perform_actions():
    global running, execution_count
    running = True
    
    while not stop_flag.is_set():
        time.sleep(1)
        pyautogui.click()
        time.sleep(1)
        pyautogui.press('4')
        time.sleep(0.5)
        pyautogui.click()
        time.sleep(0.2)
        pyautogui.press('space')
        time.sleep(0.8)
        pyautogui.press('space')
        time.sleep(0.2)
        pyautogui.press('space')
        time.sleep(0.2)
        pyautogui.press('space')
        time.sleep(0.2)
        with execution_lock:
            execution_count += 1
            countdown_label.config(text=f"{execution_count}")
    
    running = False

def start_loop():
    stop_flag.clear()
    update_background_color("green")
    threading.Thread(target=perform_actions).start()

def stop_loop():
    stop_flag.set()
    update_background_color("red")

def enable_f8_F10_controls():
    if validate_uuid():
        print("F8 and F10 controls enabled.")
        keyboard.add_hotkey('F8', start_loop)
        keyboard.add_hotkey('F10', stop_loop)
    else:
        print("HWID Error")

def create_gui():
    global root, countdown_label, outer_frame
    root = tk.Tk()
    root.geometry("220x70+1057+0")
    root.overrideredirect(True)
    root.wm_attributes("-topmost", True)

    outer_frame = tk.Frame(root, bg="red", bd=5)
    outer_frame.pack_propagate(False)
    outer_frame.pack(expand=True, fill="both", padx=5, pady=5)

    countdown_label = tk.Label(outer_frame, text=f"0", font=("Helvetica", 20), bg="white")
    countdown_label.pack(expand=True, fill="both", padx=5, pady=5)

    return root

def validate_uuid():
    return True

def update_background_color(color):
    outer_frame.config(bg=color)

def exit_app(root):
    stop_flag.set()
    root.after(0, root.destroy)
    sys.exit()

def main():
    root = create_gui()
    enable_f8_F10_controls()
    root.after(100, lambda: print("GUI ready"))
    root.mainloop()

if __name__ == "__main__":
    main()
