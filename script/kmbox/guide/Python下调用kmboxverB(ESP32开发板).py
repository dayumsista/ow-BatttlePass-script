import serial # 虽然名字叫pyserial，但导入模块依然是serial
from time import sleep # 从time模块里单独调用sleep函数

ser = serial.Serial('COM9',115200) # 串口号，波特率 默认MicroPython一般只需要这两个
# ser.open()
while 1:
    # 判断串口通讯是否被打开，不打开就打开
    if ser.isOpen() != True:
        ser.open()
    # 通过串口通讯发送数据
    ser.write('print("ni hao")\r\n'.encode('utf-8'))
    # 等待 0.001秒 
    sleep(0.001)
    # 如果有
    if ser.inWaiting():
        data = ser.readline()
        print(data)
    sleep(0.1)
