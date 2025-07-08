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
import cv2
import numpy as np
import pyautogui
import os
import logging

def find_image_position(template_filename, region=None, threshold=0.8, max_attempts=30):
    """
    识别屏幕上的目标图像，如果连续 max_attempts 次都失败，则触发 task()。
    
    参数:
    - template_filename: 模板图片文件名 (str)
    - region: 识别的屏幕区域 (tuple) (左上角x, 左上角y, 宽度, 高度)
    - threshold: 识别置信度 (float)
    - max_attempts: 最大失败次数 (int)

    返回:
    - (x, y) 点击坐标 (如果找到)
    - None (如果未找到)
    """

    script_dir = os.path.dirname(os.path.abspath(__file__))  
    template_path = os.path.join(script_dir, 'pic', template_filename)  

    failure_count = 0  # 失败计数器

    while failure_count < max_attempts:
        screenshot = pyautogui.screenshot(region=region)
        screenshot = np.array(screenshot)
        screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)

        template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
        if template is None:
            logging.error(f"❌ 找不到模板图像 {template_path}")
            return None
        
        gray_screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
        result = cv2.matchTemplate(gray_screenshot, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
        if max_val >= threshold:
            logging.info(f"✅ 识别成功: {template_filename}, 置信度: {max_val}")
            center_x = max_loc[0] + template.shape[1] // 2 + region[0]
            center_y = max_loc[1] + template.shape[0] // 2 + region[1]
            return center_x, center_y  # 识别成功，返回坐标
        
        failure_count += 1
        logging.warning(f"⚠️ 识别失败 {failure_count}/{max_attempts} 次: {template_filename}")
        time.sleep(1)  # 适当延迟，避免 CPU 过载

    logging.error(f"❌ 连续 {max_attempts} 次未找到 {template_filename}，执行 task() 重新启动游戏")
    return None

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
    logging.info("🚀 执行 `task()`：停止当前任务，重启游戏")
    print("🚀 执行 `task()`：停止当前任务，重启游戏")

    stop_loop()  # ✅ 确保 `perform_actions()` 退出
    stop_flag.set()  # ✅ 强制终止所有 `while` 循环
    time.sleep(2)

    # ✅ 确保 Overwatch.exe 彻底关闭
    kill_process_by_name('Overwatch.exe')
    
    time.sleep(3)
    os.system("start steam://rungameid/2357570")
    time.sleep(join_game_time_sleep)

    # ✅ 直接点击固定坐标
    pyautogui.moveTo(move_to_x, move_to_y)
    time.sleep(0.5)
    pyautogui.click()
    time.sleep(0.5)
    pyautogui.moveTo(1280, 720)
    time.sleep(0.5)
    pyautogui.click()
    time.sleep(0.5)
    pyautogui.moveTo(290, 878)
    time.sleep(0.5)
    pyautogui.click()
    time.sleep(2)

    global execution_count
    with execution_lock:
        execution_count = 0  # ✅ 任务完成后重置执行计数
        update_gui()  # ✅ 确保 UI 刷新

    logging.info("✅ `task()` 完成，重新启动 `start_loop()`")
    print("✅ `task()` 完成，重新启动 `start_loop()`")

    stop_flag.clear()  # ✅ 清除 `stop_flag`，确保下次 `start_loop()` 可以运行
    time.sleep(5)
    start_loop()  # ✅ 重新启动 `perform_actions()`

def update_background_color(color):
    outer_frame.config(bg=color)
    tray_icon.icon = create_image(25, color)

def perform_actions():
    global running, execution_count
    running = True
    failure_count_4_1 = 0  # `4-1.png` 识别失败次数

    while not stop_flag.is_set():
        try:
            if execution_count < max_executions:
                time.sleep(1)
                pyautogui.moveTo(470, 620)  # **移动到固定位置**
                time.sleep(0.5)
                pyautogui.click()
                time.sleep(8)

                position_4_1 = find_image_position("4-1.png", region=(1761, 40, 124, 30), threshold=0.9)

                if position_4_1:
                    logging.info("🟢 进入游戏，执行操作")
                    print("🟢 进入游戏，执行操作")
                    time.sleep(12)
                    pyautogui.press('esc') 
                    logging.info("🟢 按下 ESC 键")
                    print("🟢 按下 ESC 键")

                    time.sleep(0.5)

                    # **🔹 直接移动到 (1034, 666) 并点击**
                    pyautogui.moveTo(1034, 666)
                    time.sleep(0.5)
                    pyautogui.click()

                    for _ in range(4):  
                        pyautogui.press('space')  
                        time.sleep(0.8)  

                    with execution_lock:
                        execution_count += 1  # **增加执行计数**
                        update_gui()  # **✅ 确保 UI 刷新**
                    
                    print(f"✅ 任务执行次数: {execution_count}/{max_executions}")

                else:
                    failure_count_4_1 += 1
                    logging.warning(f"⚠️ `4-1.png` 识别失败 {failure_count_4_1}/30 次")
                    print(f"⚠️ `4-1.png` 识别失败 {failure_count_4_1}/30 次")

                    if failure_count_4_1 >= 30:
                        logging.error(f"❌ 连续 30 次未找到 `4-1.png`，执行 `task()` 关闭进程并重启游戏")
                        print(f"❌ 连续 30 次未找到 `4-1.png`，执行 `task()` 关闭进程并重启游戏")

                        stop_loop()  # **确保 `perform_actions()` 停止**
                        time.sleep(2)

                        # ✅ 执行 `task()`，并确保 `perform_actions()` 线程退出
                        task()
                        return  # ✅ 终止 `perform_actions()` 线程

            if execution_count >= max_executions:
                logging.info("🔄 任务执行次数达到上限，执行 `task()`")
                print("🔄 任务执行次数达到上限，执行 `task()`")
                stop_loop()
                task()
                return  # ✅ 确保 `perform_actions()` 退出

            time.sleep(1)  
        except Exception as e:
            logging.error(f"❌ 运行错误: {e}")
            print(f"❌ 运行错误: {e}")
            break  

    running = False

def start_loop():
    if not running:
        stop_flag.clear()
        update_background_color("green")
        threading.Thread(target=perform_actions).start()

def stop_loop():
    stop_flag.set()
    update_background_color("red")

def enable_F8_F10_controls():
    if validate_uuid():
        keyboard.add_hotkey('F8', start_loop)
        keyboard.add_hotkey('F10', stop_loop)
    else:
        # 终止程序或禁用功能
        root.destroy()
        sys.exit("HWID 验证失败")
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
    enable_F8_F10_controls()
    root.mainloop()

if __name__ == "__main__":
    main()