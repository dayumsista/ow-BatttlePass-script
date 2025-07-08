class KmboxLua:
    """ 运行 Lua 代码 """

    def __init__(self, serial):
        """ 直接使用传入的 `serial` 连接 """
        self.serial = serial  # 复用 kmbox 串口

    def execute_lua(self, lua_code):
        """ 发送 Lua 代码并执行 """
        lua_code = lua_code.strip()
        lua_code = lua_code.replace("\n", " ")  # 确保 Lua 代码在一行内发送
        response = self.serial.send_command(lua_code)
        return response

    def execute_lua_file(self, lua_file_path):
        """ 读取 Lua 文件并执行 """
        try:
            with open(lua_file_path, "r", encoding="utf-8") as f:
                lua_code = f.read()
            return self.execute_lua(lua_code)
        except Exception as e:
            print(f"❌ 读取 Lua 文件失败: {e}")
            return None
