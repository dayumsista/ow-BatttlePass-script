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

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

execution_count = 0
max_executions = 150
join_game_timesleep = 30
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
    stop_loop()
    time.sleep(5)
    
    if kill_process_by_name('Overwatch.exe'):
        print("Overwatch process killed successfully.")
    else:
        print("No Overwatch process found.")
    
    time.sleep(5)
    
    os.system("start steam://rungameid/2357570")
    time.sleep(join_game_timesleep)

    position_1 = find_image_position("1.png", region=(0, 125, 416, 376), threshold=0.8)
    move_and_click(position_1)
    time.sleep(2)
    
    position_2 = find_image_position("2.png", region=(1129, 254, 335, 555), threshold=0.8)
    move_and_click(position_2)
    time.sleep(2)
    
    position_3 = find_image_position("3.png", region=(220, 690, 160, 33), threshold=0.8)
    move_and_click(position_3)

    global execution_count
    with execution_lock:
        execution_count = 0  
        countdown_label.config(text=f"{execution_count}/{max_executions}")

    start_loop()  

def perform_actions():
    global execution_count, running
    running = True

    while not stop_flag.is_set():
        try:
            if execution_count < max_executions:
                time.sleep(1)
                position_4 = find_image_position("4.png", region=(316, 575, 236, 370), threshold=0.8)
                move_and_click(position_4)
                time.sleep(5)

                position_4_1 = find_image_position("4-1.png", region=(1761, 40, 124, 30), threshold=0.9)
                if position_4_1:
                    logging.info("🟢 进入游戏，执行操作")
                    time.sleep(12)
                    pyautogui.press('esc') 
                    logging.info("🟢 按下 ESC 键")

                    time.sleep(0.5)

                    position_5 = find_image_position("5.png", region=(880, 635, 120, 43), threshold=0.8)
                    move_and_click(position_5)

                    for _ in range(4):  
                        pyautogui.press('space')  
                        time.sleep(0.8)  

                    execution_count += 1
                    countdown_label.config(text=f"{execution_count}/{max_executions}")

                else:
                    logging.warning(f"⚠️ 关键 UI 未找到，执行 task() 重新启动")
                    task()
                    break

            if execution_count >= max_executions:
                task()
                break

            time.sleep(1)  
        except Exception as e:
            logging.error(f"❌ 运行错误: {e}")
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
    root.mainloop()

if __name__ == "__main__":
    main()
