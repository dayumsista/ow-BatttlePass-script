TARGET_UUID = "3493DF0D-0A8E-A717-A65E-D843AE4B6FB5"
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

import ctypes
import time
import logging

user32 = ctypes.windll.user32

def move_mouse(x, y):
    """使用 Windows API 移动鼠标"""
    user32.SetCursorPos(x, y)
    time.sleep(0.5)  # ✅ 停顿 0.5 秒，保证移动稳定

def click_mouse():
    """使用 Windows API 执行鼠标点击"""
    user32.mouse_event(2, 0, 0, 0, 0)  # 按下左键
    time.sleep(0.05)  # ✅ 轻微停顿
    user32.mouse_event(4, 0, 0, 0, 0)  # 释放左键
    time.sleep(0.5)  # ✅ 停顿 0.5 秒，保证点击稳定
    logging.info("🖱️ Windows API Clicked.")



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
    except Exception:
        return None

def task():
    """执行任务"""
    logging.info("🔄 Stopping loop...")
    stop_loop()  # ✅ 彻底停止旧的 perform_actions() 线程
    time.sleep(5)

    kill_process_by_name('Overwatch.exe')
    time.sleep(5)

    logging.info("🚀 Starting Overwatch via Steam...")
    os.system("start steam://rungameid/2357570")

    logging.info(f"⌛ Waiting {join_game_time_sleep} seconds for game to launch...")
    time.sleep(join_game_time_sleep)

    logging.info("✅ Clicking UI elements...")

    move_mouse(move_to_x, move_to_y)  # ✅ 先移动
    click_mouse()  # ✅ 再点击
    
    move_mouse(1700, 600)  # ✅ 先移动
    click_mouse()  # ✅ 再点击

    move_mouse(400, 900)  # ✅ 先移动
    click_mouse()  # ✅ 再点击

    global execution_count
    with execution_lock:
        execution_count = 0
        logging.info(f"🔄 Resetting execution count: {execution_count}/{max_executions}")
        countdown_label.config(text=f"{execution_count}/{max_executions}")

    logging.info("🔄 Restarting loop...")
    
    if not running:  # ✅ 确保不会重复开启新线程
        start_loop()


def update_background_color(color):
    outer_frame.config(bg=color)
    tray_icon.icon = create_image(25, color)

def monitor_screen_image(max_attempts=15, confidence=0.9, target_udp_count=3):
    """
    监控 `0.png`，每秒检查一次，最多尝试 `max_attempts` 次：
    - **找到图片** → 返回 `True`
    - **30 次仍找不到** → 检查 UDP 连接
        - **UDP 连接数 ≥ `target_udp_count`** → 通过，不执行 `task()`
        - **UDP 连接数 < `target_udp_count`** → 执行 `task()`
    """
    image_path = os.path.join(get_base_path(), '0.png')

    if not os.path.exists(image_path):
        logging.error(f"❌ Image file not found: {image_path}")
        return False  # 文件不存在，直接跳过

    logging.info(f"🔍 Monitoring screen for {image_path} (max attempts: {max_attempts})")

    for attempt in range(max_attempts):
        try:
            location = pyautogui.locateOnScreen(image_path, region=(2349, 57, 163, 40), confidence=confidence)
            if location:
                logging.info(f"✅ Image found on screen! (Attempt {attempt + 1})")
                print("hello world！")
                return True  # 找到图片，返回 True
        except pyautogui.ImageNotFoundException:
            logging.warning(f"❌ Image not found (Attempt {attempt + 1}/{max_attempts})")
        except Exception as e:
            logging.error(f"⚠️ Error in monitor_screen_image(): {e}")
            break

        time.sleep(1)

    # 🚀 **30 次仍然找不到 0.png，检查 UDP 连接数**
    logging.warning("⚠️ Max attempts reached. Checking UDP connections...")

    pid = get_process_pid('Overwatch.exe')  # 获取进程 PID
    if pid is not None:
        udp_count = sum(1 for conn in psutil.net_connections(kind='udp') if conn.pid == pid)
        logging.info(f"🔍 UDP connections for PID {pid}: {udp_count}")

        if udp_count >= target_udp_count:
            logging.info(f"✅ UDP connections ≥ {target_udp_count}, skipping task.")
            return True  # **UDP 连接数足够，跳过 `task()`**
        else:
            logging.warning(f"⚠️ UDP connections < {target_udp_count}, executing task()...")

    task()  # **UDP 连接不足，执行 `task()`**
    return False


def perform_actions():
    """执行循环动作"""
    global running, execution_count
    running = True

    while not stop_flag.is_set():
        time.sleep(2)
        move_mouse(600, 600)  # ✅ 先移动
        click_mouse()  # ✅ 再点击
        time.sleep(1)
        time.sleep(extra_time_sleep)

        if stop_flag.is_set():
            break

        if not monitor_screen_image():
            logging.warning("⚠️ Image detection and UDP check failed, executing task()...")
            continue

        logging.info("🎮 Continuing game automation sequence...")
        time.sleep(11)
        keyboard.press_and_release('esc')  # ✅ 替换 pyautogui.press()
        time.sleep(0.5)
        
        move_mouse(1260, 881)  # ✅ 先移动
        click_mouse()  # ✅ 再点击
        
        keyboard.press_and_release('space')  # ✅ 替换 pyautogui.press()
        time.sleep(3)

        with execution_lock:
            execution_count += 1
            logging.info(f"🔄 Execution count updated: {execution_count}/{max_executions}")
            countdown_label.config(text=f"{execution_count}/{max_executions}")

        if execution_count >= max_executions:
            task()
            break

    running = False

def start_loop():
    """开始任务循环"""
    global running
    if running:
        logging.warning("⚠️ Loop is already running, skipping start.")
        return

    stop_flag.clear()
    running = True  # ✅ 确保不会重复开启新线程
    update_background_color("green")
    logging.info("✅ Loop started.")
    threading.Thread(target=perform_actions, daemon=True).start()


def stop_loop():
    """停止任务循环并更新颜色"""
    global running
    stop_flag.set()
    running = False  
    logging.info("🛑 Loop stopped.")

    update_background_color("red")  # ✅ 强制更新窗口颜色
    time.sleep(2)  # ✅ 等待确保线程停止



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
    return get_windows_computer_id() == TARGET_UUID

def main():
    global tray_icon
    root = create_gui()
    tray_icon = Icon("example", icon=create_image(25, "red"),
                     menu=Menu(MenuItem("Exit", lambda: exit_app(tray_icon, root))))
    tray_icon.run_detached()
    enable_f8_F10_controls()
    root.mainloop()

if __name__ == "__main__":
    main()
