import serial
import time

class KmboxController:
    def __init__(self, port="COM3", baudrate=115200, timeout=1):
        """ 初始化串口 """
        try:
            self.ser = serial.Serial(port, baudrate, timeout=timeout)
            time.sleep(1)  # 等待串口稳定
            print(f"✅ 成功连接到 {port}，波特率 {baudrate}")
        except serial.SerialException as e:
            print(f"❌ 串口连接失败: {e}")
            exit()

    def send_command(self, command):
        print(f'📤 发送: {command}')
        self.ser.write(f'{command}\r\n'.encode('utf-8'))
        time.sleep(0.05)
        response = self.ser.read(self.ser.inWaiting()).decode('utf-8', errors='ignore').strip()
        print(f'📥 接收: {response}')
        return response

    def initialize_kmbox(self):
        #初始化 kmbox
        self.send_command("import km")

    def move(self, x, y):
        self.send_command(f"km.move({x},{y})")

    def get_position(self):
        response = self.send_command("km.getpos()")
        print(f"🧐 解析前的数据: {response}") 

        lines = response.splitlines() 
        if len(lines) > 1 and "(" in lines[1] and ")" in lines[1]:
            try:
                pos_data = lines[1].split("(")[1].split(")")[0] 
                x, y = map(int, pos_data.split(","))  
                return (x, y)
            except ValueError:
                print("❌ 解析坐标失败，返回格式可能不正确！")
                return None
        else:
            print("❌ 未找到位置信息！")
            return None

    def stop(self):
        self.send_command("km.move(0,0)")

    def reset(self):
        self.send_command("km.reset()")

    def close(self):
        self.ser.close()
        print("🔌 串口已关闭")

# 运行示例
if __name__ == "__main__":
    kmbox = KmboxController(port="COM3")  # 修改成你的 COM 端口
    kmbox.initialize_kmbox()  # 初始化 kmbox

    kmbox.move(20, 0)  # 移动到 (20,0)
    pos = kmbox.get_position() 
    if pos:
        print(f"📍 当前位置: {pos}")

    kmbox.stop() 
    kmbox.close() 
