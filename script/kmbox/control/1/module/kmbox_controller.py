from kmbox_serial import KmboxSerial

class KmboxController:
    """ kmbox 设备控制 """

    def __init__(self, config_path="config.ini"):
        self.serial = KmboxSerial(config_path)
        self.serial.send_command("import km")  # 设备初始化

    def move(self, x, y):
        """ 移动到 (x, y) 位置 """
        self.serial.send_command(f"km.move({x},{y})")

    def get_position(self):
        """ 获取当前位置 """
        response = self.serial.send_command("km.getpos()")
        print(f"🧐 解析前的数据: {response}")  # 调试信息

        lines = response.splitlines()  # 按行分割
        if len(lines) > 1 and "(" in lines[1] and ")" in lines[1]:
            try:
                pos_data = lines[1].split("(")[1].split(")")[0]  # 提取括号内的内容
                x, y = map(int, pos_data.split(","))  # 解析 x, y 坐标
                return (x, y)
            except ValueError:
                print("❌ 解析坐标失败，返回格式可能不正确！")
                return None
        else:
            print("❌ 未找到位置信息！")
            return None

    def stop(self):
        """ 停止运动 (使用 km.move(0, 0) 代替 stop) """
        self.serial.send_command("km.move(0,0)")

    def reset(self):
        """ 复位设备（如果 kmbox 有这个 API） """
        self.serial.send_command("km.reset()")

    def close(self):
        """ 关闭串口 """
        self.serial.close()
