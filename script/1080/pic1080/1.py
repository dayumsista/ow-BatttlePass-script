import pyautogui
import cv2
import numpy as np
import os
import time

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


# 第一步：扫描1.png，扫描区域为 x(0-415) y(125-500)，即区域(0, 125, 416, 376)
position_1 = find_image_position("1.png", region=(0, 125, 416, 376), threshold=0.8)
move_and_click(position_1)

# 等待2秒
time.sleep(2)

# 第二步：扫描2.png，扫描区域为 x(1129-1463) y(254-808)，即区域(1129, 254, 335, 555)
position_2 = find_image_position("2.png", region=(1129, 254, 335, 555), threshold=0.8)
move_and_click(position_2)

# 等待2秒
time.sleep(2)

# 第三步：扫描3.png，扫描区域为 x(220-380) y(690-723)，即区域(220, 690, 160, 33)
position_3 = find_image_position("3.png", region=(220, 690, 160, 33), threshold=0.8)
move_and_click(position_3)
