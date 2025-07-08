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

def monitor_udp_connections(pid, max_attempts=60, target_udp_count=3):
    attempts = 0
    while attempts < max_attempts:
        udp_count = sum(1 for conn in psutil.net_connections(kind='udp') if conn.pid == pid)
        logging.info(f"🔄 UDP connections for PID {pid}: {udp_count}")
        if udp_count >= target_udp_count:
            logging.info(f"✅ UDP connections reached {target_udp_count} or more, skipping task.")
            return True
        attempts += 1
        time.sleep(1)
    logging.warning(f"⚠️ Max attempts ({max_attempts}) reached without reaching {target_udp_count}. Continuing actions...")
    return False

def get_process_pid(process_name):
    try:
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['name'] == process_name:
                return proc.info['pid']
    except psutil.NoSuchProcess:
        logging.error(f"Process {process_name} not found.")
    except psutil.AccessDenied:
        logging.error(f"Permission denied while accessing process {process_name}.")
    return None

def perform_actions():
    global running, execution_count
    running = True
    
    while not stop_flag.is_set():
        time.sleep(1)
        pyautogui.moveTo(600, 600)
        time.sleep(0.5)
        pyautogui.click()
        time.sleep(1)

        pid = get_process_pid('Overwatch.exe')
        if pid and monitor_udp_connections(pid):
            logging.info("✅ UDP connections confirmed, skipping unnecessary tasks.")
        
        time.sleep(extra_time_sleep)
        if stop_flag.is_set(): break

        time.sleep(6)
        pyautogui.press('shift')
        time.sleep(5)
        pyautogui.press('esc')
        time.sleep(0.5)
        pyautogui.moveTo(1000, 650)
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
