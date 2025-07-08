import psutil
import time

def monitor_overwatch_udp_connections():
    while True:
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['name'] == 'Overwatch.exe':
                pid = proc.info['pid']
                print(f"Found Overwatch.exe with PID: {pid}")
                
                # 获取该进程的 UDP 连接
                connections = psutil.net_connections(kind='udp')
                udp_count = 0
                
                for conn in connections:
                    if conn.pid == pid:  # 检查是否属于 Overwatch.exe
                        udp_count += 1
                        local_ip, local_port = conn.laddr if conn.laddr else ("None", "None")
                        print(f"UDP Connection: Local: {local_ip}:{local_port}")
                
                print(f"Total UDP connections: {udp_count}")
                
                # 如果 UDP 连接数量超过 3，打印 "Hello World"
                if udp_count > 2:
                    print("Hello World")
        time.sleep(1)  # 每隔 1 秒检查一次

monitor_overwatch_udp_connections()
