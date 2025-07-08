import serial
import time
print('打开串口\n')
ser=serial.Serial('COM28',115200)
print('向kmbox发送 import km')
ser.write('import km\r\n'.encode('utf-8'))
time.sleep(0.01)                                    #需要等待kmbox回码
print('kmbox回码如下：',ser.read(ser.inWaiting()))    #读kmbox的回码
print('向kmbox发送 km.move(10,0)')
ser.write('km.move(10,0)\r\n'.encode('utf-8'))
time.sleep(0.01)                                    #需要等待kmbox回码
print('kmbox回码如下：',ser.read(ser.inWaiting()))    #读kmbox的回码
print('向kmbox发送 km.getpos()')
ser.write('km.getpos()\r\n'.encode('utf-8'))
time.sleep(0.01)                                    #需要等待kmbox回码
print('kmbox回码如下：',ser.read(ser.inWaiting()))    #读kmbox的回码

