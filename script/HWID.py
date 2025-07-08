import wmi

def get_windows_computer_id():
    try:
        computer = wmi.WMI()
        cs_product = computer.Win32_ComputerSystemProduct()[0]
        return cs_product.UUID
    except Exception as e:
        return f"Error retrieving computer ID: {e}"

computer_id = get_windows_computer_id()
print("Windows计算机ID:", computer_id)

input("\n按 Enter 键关闭窗口...")
