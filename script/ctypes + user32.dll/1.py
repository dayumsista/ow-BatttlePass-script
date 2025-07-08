import ctypes
import time

user32 = ctypes.windll.user32

def move_and_click(x, y):
    """使用 Windows API 移动鼠标并点击"""
    user32.SetCursorPos(x, y)
    time.sleep(0.1)
    user32.mouse_event(2, 0, 0, 0, 0)  # 按下左键
    time.sleep(0.05)
    user32.mouse_event(4, 0, 0, 0, 0)  # 释放左键
    print(f"🖱️ Clicked at ({x}, {y})")

# 测试鼠标操作
time.sleep(3)  # 给你 3 秒时间准备
move_and_click(1000, 500)  # 让鼠标点击 (1000, 500)
