import pyautogui
import cv2
import numpy as np
import os
import time
import keyboard  # 导入 keyboard 库，用于监听键盘事件

def find_image_position(template_filename, region=None, threshold=0.8):
    # 获取模板图像的完整路径
    script_dir = os.path.dirname(os.path.abspath(__file__))  # 获取当前脚本的路径
    template_path = os.path.join(script_dir, 'pic', template_filename)  # 组合路径
    
    # 截取屏幕区域
    screenshot = pyautogui.screenshot(region=region)
    
    # 将屏幕截图转换为OpenCV格式的图片
    screenshot = np.array(screenshot)
    screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)
    
    # 加载模板图像
    template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
    if template is None:
        print(f"错误: 找不到模板图像 {template_path}")
        return None
    
    gray_screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
    
    # 使用模板匹配
    result = cv2.matchTemplate(gray_screenshot, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    
    # 如果最大匹配值大于阈值，则认为匹配成功
    if max_val >= threshold:
        print(f"图像匹配成功，置信度: {max_val}")
        
        # 计算匹配图像的中心位置
        center_x = max_loc[0] + template.shape[1] // 2 + region[0]
        center_y = max_loc[1] + template.shape[0] // 2 + region[1]
        
        # 返回中心位置
        return center_x, center_y
    else:
        print(f"未找到匹配图像，置信度低于阈值。")
        return None


def move_and_click(position):
    """
    移动到图像的中心位置并点击，间隔0.5秒。
    
    :param position: 图像的中心位置 (x, y)
    """
    if position:
        pyautogui.moveTo(position[0], position[1])  # 移动到目标位置
        time.sleep(0.5)  # 等待 0.5 秒
        pyautogui.click(position[0], position[1])  # 点击
        print(f"点击位置: {position}")
    else:
        print("未找到点击位置，无法执行点击操作。")


def scan_and_click_loop():
    """
    执行整个扫描和点击循环的逻辑。
    """
    while True:
        # 查找 "4.png"，区域为 (316, 575, 236, 370)
        position_4 = find_image_position("4.png", region=(316, 575, 236, 370), threshold=0.8)
        move_and_click(position_4)
        time.sleep(5)

        while True:
            # 查找 "4-1.png"，区域为 (1761, 40, 124, 30)
            position_4_1 = find_image_position("4-1.png", region=(1761, 40, 124, 30), threshold=0.9)
            if position_4_1:
                print("hello world")
                time.sleep(15)
                pyautogui.press('esc')  # 按下 ESC 键
                print("按下 ESC 键")
                
                # 等待 0.5 秒
                time.sleep(0.5)

                # 查找 "5.png"，区域为 (880, 635, 120, 43)
                position_5 = find_image_position("5.png", region=(880, 635, 120, 43), threshold=0.8)
                if position_5:
                    pyautogui.moveTo(position_5[0], position_5[1])  # 移动到图像中心位置
                    time.sleep(0.5)  # 等待0.5秒
                    pyautogui.click()  # 点击图像
                else:
                    print("未找到点击位置，无法执行点击操作。")

                # 按空格4次
                for _ in range(4):  
                    pyautogui.press('space')  
                    time.sleep(0.8)  

                # 再次扫描并点击 position_4
                position_4 = find_image_position("4.png", region=(316, 575, 236, 370), threshold=0.8)
                move_and_click(position_4)
                time.sleep(5)  # 等待 5 秒后再进行下一次扫描

            else:
                print(f"未找到匹配图像，置信度低于阈值。")
            time.sleep(1)  # 每秒钟扫描一次


if __name__ == "__main__":
    scan_and_click_loop()  # 执行扫描并点击循环
