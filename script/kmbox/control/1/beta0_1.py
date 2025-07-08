import serial
import time
import configparser
import os
import configparser

config_path = os.path.join(os.path.dirname(__file__), "config.ini")
config = configparser.ConfigParser()
config.read(config_path)
port = config["SerialConfig"]["port"]
baudrate = int(config["SerialConfig"]["baudrate"])
print("🔍 配置文件路径:", config_path)
print("🔍 读取的配置部分:", config.sections())

class KmboxController:
    """ Kmbox 设备控制类 """

    def __init__(self, port, baudrate, timeout=1):
        """ 初始化串口 """
        try:
            self.ser = serial.Serial(port, baudrate, timeout=timeout)
            time.sleep(1)  # 等待串口稳定
            print(f"✅ 成功连接到 {port}，波特率 {baudrate}")
        except serial.SerialException as e:
            print(f"❌ 串口连接失败: {e}")
            exit()

    def send_command(self, command):
        """ 发送命令并读取返回 """
        print(f'📤 发送: {command}')
        self.ser.write(f'{command}\r\n'.encode('utf-8'))
        time.sleep(0.05)  # 等待设备返回数据
        response = self.ser.read(self.ser.inWaiting()).decode('utf-8', errors='ignore').strip()
        print(f'📥 接收: {response}')
        return response

    def initialize_kmbox(self):
        """ 初始化 kmbox """
        self.send_command("import km")

    def move(self, x, y):
        """ 移动到 (x, y) 位置 """
        self.send_command(f"km.move({x},{y})")

    def get_position(self):
        """ 获取当前位置 """
        response = self.send_command("km.getpos()")
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
        self.send_command("km.move(0,0)")

    def reset(self):
        """ 复位设备（如果 kmbox 有这个 API） """
        self.send_command("km.reset()")

    def close(self):
        """ 关闭串口 """
        self.ser.close()
        print("🔌 串口已关闭")





# **运行示例**
if __name__ == "__main__":
    kmbox = KmboxController(port=port, baudrate=baudrate)
    kmbox.initialize_kmbox()  # 初始化 kmbox

    print("⏳ 等待 3 秒...")
    time.sleep(3)  # 等待 3 秒后移动

    kmbox.move(100, 100)  # 移动到 (100,100)

    pos = kmbox.get_position()  # 获取当前位置
    if pos:
        print(f"📍 当前位置: {pos}")

    kmbox.close()  # 关闭串口
