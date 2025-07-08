import serial
import time
import configparser
import os

class KmboxSerial:
    """ 串口通信模块 """

    def __init__(self, config_path="config.ini"):
        """ 读取配置文件，初始化串口 """
        self.config = configparser.ConfigParser()
        self.config.read(config_path)

        self.port = self.config["SerialConfig"]["port"]
        self.baudrate = int(self.config["SerialConfig"]["baudrate"])

        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=1)
            time.sleep(1)  # 等待串口稳定
            print(f"✅ 成功连接到 {self.port}，波特率 {self.baudrate}")
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

    def close(self):
        """ 关闭串口 """
        self.ser.close()
        print("🔌 串口已关闭")
