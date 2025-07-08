import time
import threading
from pynput import keyboard, mouse

# 运行状态标志
running = False

def click_space():
    global running
    keyboard_controller = keyboard.Controller()
    while running:
        keyboard_controller.press(keyboard.Key.space)
        keyboard_controller.release(keyboard.Key.space)
        time.sleep(0.005)  # 每5秒点击一次（0.2次/秒）

def on_press(key):
    global running
    try:
        if key == keyboard.Key.f8:
            if not running:
                running = True
                threading.Thread(target=click_space, daemon=True).start()
                print("[+] 自动空格点击已启动")
        elif key == keyboard.Key.f10:
            running = False
            print("[-] 自动空格点击已停止")
    except Exception as e:
        print("[Error]", e)

# 监听键盘事件
with keyboard.Listener(on_press=on_press) as listener:
    listener.join()