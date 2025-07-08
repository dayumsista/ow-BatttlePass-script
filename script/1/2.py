import pyautogui
import time
from PIL import ImageGrab

# 你的目标绿色，可以从图片提取，也可以直接用这个RGB值
target_color = (101, 192, 76)  # 这是示例值，需要校正成你的绿色

# 设置颜色容差，防止因微小色差导致不识别
color_tolerance = 10

def is_color_match(c1, c2, tolerance=10):
    return all(abs(a - b) <= tolerance for a, b in zip(c1, c2))

def main():
    print("开始监测屏幕中心颜色，按 Ctrl+C 退出...")
    try:
        while True:
            screen = ImageGrab.grab()
            width, height = screen.size
            center_color = screen.getpixel((width // 2, height // 2))

            if is_color_match(center_color, target_color, color_tolerance):
                print("检测到目标绿色，点击鼠标！")
                pyautogui.click()
                time.sleep(0.5)  # 点击后稍微休息一下，避免连点太快
            else:
                time.sleep(0.05)  # 稍微等待，减少CPU占用
    except KeyboardInterrupt:
        print("\n监测停止。")

if __name__ == "__main__":
    main()
