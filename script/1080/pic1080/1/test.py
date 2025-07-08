import pyautogui
import cv2
import numpy as np
import os
import time
import threading
import tkinter as tk
from PIL import Image, ImageDraw
from pystray import Icon, MenuItem, Menu
import keyboard
import sys
import psutil
import logging
import configparser
import os

execution_count = 0 

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

import configparser
import os

# 读取配置文件
config = configparser.ConfigParser()
config_path = os.path.join(os.path.dirname(__file__), "config.ini")

# 确保配置文件存在
if not os.path.exists(config_path):
    raise FileNotFoundError(f"❌ 配置文件 {config_path} 不存在，请创建 config.ini")

config.read(config_path, encoding="utf-8")

# 从配置文件读取参数
try:
    max_executions = int(config.get("Settings", "max_executions"))
    extra_time_sleep = int(config.get("Settings", "extra_time_sleep"))
except Exception as e:
    raise ValueError(f"❌ 配置文件解析错误: {e}")

print(f"✅ 配置加载成功: max_executions={max_executions},  extra_time_sleep={extra_time_sleep}")


running = False
stop_flag = threading.Event()  
execution_lock = threading.Lock()  

def update_background_color(color):
    outer_frame.config(bg=color)

def kill_process_by_name(process_name):
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] == process_name:
            print(f"Terminating process: {proc.info['name']}, PID: {proc.info['pid']}")
            proc.terminate()  
            return True
    return False

def move_and_click(position):
    """
    移动鼠标到指定位置并点击
    """
    if position:
        pyautogui.moveTo(position[0], position[1], duration=0.2)  # 让鼠标移动更自然
        pyautogui.click()
        logging.info(f"✅ 点击位置: {position}")
    else:
        logging.warning("⚠️ 未找到点击位置，跳过操作")

def task():
    global running
    logging.warning("⚠️ 触发 `task()`，停止当前任务")
    stop_loop()  
    time.sleep(5)

    running = False  
    stop_flag.clear()

    if kill_process_by_name('Overwatch.exe'):
        logging.info("✅ Overwatch 进程已终止")
    else:
        logging.warning("⚠️ 未找到 Overwatch 进程")

    time.sleep(5)
    
    os.system("start steam://rungameid/2357570")
    time.sleep(10)  
    
    max_attempts = 120
    attempts = 0

    while attempts < max_attempts:
        position_1 = find_image_position("1.png", region=(0, 125, 416, 376), threshold=0.8)

        if position_1:
            move_and_click(position_1)
            logging.info(f"✅ 识别 `1.png` 成功，点击 {position_1}")
            break  # 成功识别后退出循环
        
        attempts += 1
        logging.warning(f"⚠️ 第 {attempts}/{max_attempts} 次未识别到 `1.png`，继续尝试")
        time.sleep(1)  # **每次尝试间隔 1 秒**

    if attempts >= max_attempts:
        logging.error(f"❌ `1.png` 识别失败 {max_attempts} 次，重新执行 task()")
        task()  # **识别失败 120 次后重新启动游戏**
        return

    time.sleep(2)
    
    pyautogui.moveTo(1470, 600, duration=0.2)
    pyautogui.click()
    time.sleep(2)
    
    pyautogui.moveTo(300, 650, duration=0.2)
    pyautogui.click()
    time.sleep(5)

    global execution_count
    with execution_lock:
        execution_count = 0  
        countdown_label.config(text=f"{execution_count}/{max_executions}")

    logging.info("✅ `task()` 完成，重新启动 `start_loop()`")
    root.after(0, start_loop)  # **确保 UI 颜色变化在主线程执行**

def perform_actions():
    global execution_count, running
    running = True
    logging.info("🚀 `perform_actions()` 线程启动")  # 确保函数被执行

    failure_count_4_1 = 0  # 记录 `4-1.png` 识别失败的次数

    while not stop_flag.is_set():
        try:
            if execution_count < max_executions:
                time.sleep(1)

                pyautogui.moveTo(450, 550, duration=0.2)
                pyautogui.click()
                time.sleep(5)

                position_4_1 = find_image_position("4-1.png", region=(1761, 40, 124, 30), threshold=0.9)

                if position_4_1:
                    logging.info("🟢 进入游戏，执行操作")
                    failure_count_4_1 = 0  # 成功识别，重置失败次数
                    time.sleep(16)
                    pyautogui.press('esc') 
                    logging.info("🟢 按下 ESC 键")

                    time.sleep(0.5)
                    pyautogui.moveTo(950, 670, duration=0.2)
                    pyautogui.click()

                    for _ in range(4):  
                        pyautogui.press('space')  
                        time.sleep(0.8)  

                    with execution_lock:
                        execution_count += 1
                        countdown_label.config(text=f"{execution_count}/{max_executions}")

                else:
                    failure_count_4_1 += 1
                    logging.warning(f"⚠️ `4-1.png` 识别失败 {failure_count_4_1}/30 次")

                    if failure_count_4_1 >= 30:
                        logging.error("❌ `4-1.png` 连续 30 次识别失败，执行 task() 重新启动")
                        stop_loop()
                        task()
                        return  # 确保 `perform_actions()` 停止

            if execution_count >= max_executions:
                stop_loop()
                task()
                return  # 确保 `perform_actions()` 停止

            time.sleep(1)  
        except Exception as e:
            logging.error(f"❌ 运行错误: {e}")
            break  

    running = False
 
def start_loop():
    global running
    stop_flag.clear()
    root.after(0, update_background_color, "green")  # **确保 UI 在主线程更新**

    if not running:  # **防止多次启动**
        running = False  # **强制重置 running 变量**
        threading.Thread(target=perform_actions, daemon=True).start()
        logging.info("✅ `start_loop()` 启动新的 `perform_actions()` 线程")


def stop_loop():
    stop_flag.set()
    root.after(0, update_background_color, "red")  

def enable_f8_F10_controls():
    print("F8 and F10 controls enabled.")
    keyboard.add_hotkey('F8', start_loop)
    keyboard.add_hotkey('F10', stop_loop)

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
    root.geometry("220x50+1468+0")
    root.overrideredirect(True)
    root.wm_attributes("-topmost", True)

    outer_frame = tk.Frame(root, bg="red", bd=4)
    outer_frame.pack_propagate(False)

    outer_frame.pack(expand=True, fill="both", padx=4, pady=4)

    countdown_label = tk.Label(outer_frame, text=f"0/{max_executions}", font=("Helvetica", 20), bg="white")
    countdown_label.pack(expand=True, fill="both", padx=4, pady=4)

    return root

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
    task()  # 触发 task() 重新启动游戏
    return None

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

    try:
        root.mainloop()  # GUI 主线程
    except KeyboardInterrupt:
        logging.warning("⚠️  检测到 `Ctrl + C`，正在退出程序...")
        stop_loop()  # 停止线程
        keyboard.unhook_all()  # 释放所有 `keyboard` 监听
        sys.exit(0)  # 退出程序


if __name__ == "__main__":
    main()
