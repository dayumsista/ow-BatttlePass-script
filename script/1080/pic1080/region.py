def calculate_region(x_min, x_max, y_min, y_max):
    """
    计算给定坐标范围的宽度和高度，并返回适合复制的region格式。
    
    :param x_min: x坐标的最小值
    :param x_max: x坐标的最大值
    :param y_min: y坐标的最小值
    :param y_max: y坐标的最大值
    :return: region格式字符串 (region=(x_min, y_min, width, height))
    """
    width = x_max - x_min
    height = y_max - y_min
    return f"region=({x_min}, {y_min}, {width}, {height})"

# 给定的坐标范围
x_min = 880
x_max = 1000
y_min = 635
y_max = 678

# 计算并输出region格式
region_str = calculate_region(x_min, x_max, y_min, y_max)
print(region_str)
