TARGET_UUID = "A530284C-7311-EE11-8C92-BC0FF3D30E17"
import pyautogui
import time
import threading
import tkinter as tk
import sys
import os
import psutil
from pystray import Icon, Menu, MenuItem
from PIL import Image, ImageDraw
import keyboard
import wmi
import configparser
import logging

logging.basicConfig(level=logging.INFO)

stop_flag = threading.Event()
running = False
countdown_thread = None
pyautogui.FAILSAFE = False
tray_icon = None
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
    max_executions = int(config.get('Settings', 'max_executions'))
    extra_time_sleep = float(config.get('Settings', 'extra_time_sleep'))
    move_to_x = int(config.get('Settings', 'move_to_x'))
    move_to_y = int(config.get('Settings', 'move_to_y'))
    join_game_time_sleep = int(config.get('Settings', 'join_game_time_sleep'))
except ValueError as e:
    print(f"Error in config values: {e}")
    sys.exit(1)

previous_udp_count = {}  # 记录每个进程的 UDP 连接数
def monitor_udp_connections(pid, max_attempts=60, target_udp_count=3):
    """监控指定进程的 UDP 连接数
       - 如果 UDP 连接数达到或超过 target_udp_count → 执行 task()
       - 否则，继续监测直到达到 max_attempts"""
    
    global previous_udp_count
    initial_udp_count = sum(1 for conn in psutil.net_connections(kind='udp') if conn.pid == pid)
    previous_udp_count[pid] = initial_udp_count
    attempts = 0

    logging.info(f"🔍 Initial UDP scan for PID {pid}: {initial_udp_count} connections recorded.")

    while attempts < max_attempts:
        udp_count = sum(1 for conn in psutil.net_connections(kind='udp') if conn.pid == pid)
        logging.info(f"🔄 UDP connections for PID {pid}: {udp_count} (Initial: {initial_udp_count})")

        if udp_count >= target_udp_count:
            logging.info(f"✅ UDP connections reached {target_udp_count} or more, skipping task.")
            return True  # 达到目标连接数，跳过任务

        attempts += 1  # 计数器 +1
        time.sleep(1)  # 每次检查间隔 1 秒

    logging.warning(f"⚠️ Max attempts ({max_attempts}) reached without reaching {target_udp_count}. Executing task...")
    return False  # 达到 max_attempts，执行 task

# 错误处理示例
def get_process_pid(process_name):
    """获取指定进程的PID，如果进程不存在则返回None"""
    try:
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['name'] == process_name:
                return proc.info['pid']
    except psutil.NoSuchProcess as e:
        logging.error(f"Process {process_name} not found: {e}")
    except psutil.AccessDenied as e:
        logging.error(f"Permission denied while accessing process {process_name}: {e}")
    return None

def kill_process_by_name(process_name):
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] == process_name:
            proc.kill()

def get_windows_computer_id():
    try:
        computer = wmi.WMI()
        cs_product = computer.Win32_ComputerSystemProduct()[0]
        return cs_product.UUID
    except Exception as e:
        return None

def task():
    stop_loop()
    time.sleep(5)
    kill_process_by_name('Overwatch.exe')
    time.sleep(5)
    os.system("start steam://rungameid/2357570")
    time.sleep(join_game_time_sleep)
    pyautogui.moveTo(move_to_x, move_to_y)
    time.sleep(0.5)
    pyautogui.click()
    time.sleep(0.5)
    pyautogui.moveTo(1700, 600)
    time.sleep(0.5)
    pyautogui.click()
    time.sleep(0.5)
    pyautogui.moveTo(400, 900)
    time.sleep(0.5)
    pyautogui.click()
    time.sleep(2)

    global execution_count
    with execution_lock:
        execution_count = 0
        countdown_label.config(text=f"{execution_count}/{max_executions}")

    start_loop()

def update_background_color(color):
    outer_frame.config(bg=color)
    tray_icon.icon = create_image(25, color)

def perform_actions():
    global running, execution_count
    running = True
    
    while not stop_flag.is_set():
        time.sleep(1)
        pyautogui.moveTo(600, 600)
        time.sleep(0.5)
        pyautogui.click()
        time.sleep(1)

        # 获取 Overwatch.exe 的 PID
        pid = get_process_pid('Overwatch.exe')

        if pid is not None:
            should_skip_task = monitor_udp_connections(pid)  # **返回 True 表示不执行 task**
            
            if not should_skip_task:  
                logging.warning("⚠️ No UDP increase detected. Executing task...")
                task()  # **执行 task**
                break  # 退出循环
            else:
                logging.info("✅ UDP connections reached target. Skipping task.")

        time.sleep(extra_time_sleep)
        if stop_flag.is_set(): break

        # 模拟游戏输入
        time.sleep(5)
        pyautogui.press('shift')
        time.sleep(5)
        pyautogui.press('esc')
        time.sleep(0.5)
        pyautogui.moveTo(1260, 881)
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
            countdown_label.config(text=f"{execution_count}/{max_executions}")

        if execution_count >= max_executions:
            task()
            break

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

def exit_app(icon, root):
    stop_flag.set()
    icon.stop()
    root.after(0, root.destroy)
    sys.exit()

def create_image(size, color):
    image = Image.new('RGB', (size, size), color)
    draw = ImageDraw.Draw(image)
    draw.rectangle([0, 0, size, size], fill=color)
    return image

def create_gui():
    global root, countdown_label, outer_frame
    root = tk.Tk()
    root.geometry("220x70+1957+0")
    root.overrideredirect(True)
    root.wm_attributes("-topmost", True)

    outer_frame = tk.Frame(root, bg="red", bd=5)
    outer_frame.pack_propagate(False)

    outer_frame.pack(expand=True, fill="both", padx=5, pady=5)

    countdown_label = tk.Label(outer_frame, text=f"0/{max_executions}", font=("Helvetica", 20), bg="white")
    countdown_label.pack(expand=True, fill="both", padx=5, pady=5)

    return root

def validate_uuid():
    current_uuid = get_windows_computer_id()
    return current_uuid == TARGET_UUID

def main():
    global countdown_thread, tray_icon
    root = create_gui()
    tray_icon = Icon("example", icon=create_image(25, "red"),
                     menu=Menu(
                         MenuItem("Exit", lambda: exit_app(tray_icon, root)),
                         MenuItem(" ", None, enabled=False)
                 ))

    tray_icon.run_detached()
    enable_f8_F10_controls()
    root.after(100,lambda:print("GUI ready"))
    root.mainloop()

if __name__ == "__main__":
    main()
