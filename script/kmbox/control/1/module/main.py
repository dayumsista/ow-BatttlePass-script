import os
import time
from kmbox_controller import KmboxController
from kmbox_lua import KmboxLua

def list_lua_files(lua_folder="lua"):
    """ 获取 `lua` 文件夹中的所有 Lua 文件 """
    files = [f for f in os.listdir(lua_folder) if f.endswith(".lua")]
    return files

def choose_lua_script(lua_folder="lua"):
    """ 让用户选择要运行的 Lua 文件 """
    lua_files = list_lua_files(lua_folder)
    if not lua_files:
        print("❌ 没有找到 Lua 文件，请检查 `lua` 文件夹！")
        return None

    print("\n📜 可用的 Lua 脚本:")
    for idx, file in enumerate(lua_files):
        print(f"  [{idx + 1}] {file}")

    while True:
        try:
            choice = int(input("\n🔢 请输入要运行的 Lua 文件编号: ")) - 1
            if 0 <= choice < len(lua_files):
                return os.path.join(lua_folder, lua_files[choice])
            else:
                print("❌ 输入无效，请输入正确的编号！")
        except ValueError:
            print("❌ 请输入数字编号！")

if __name__ == "__main__":
    # **确保 Python 运行路径正确**
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    config_path = os.path.join(script_dir, "config.ini")
    print("🔍 使用的配置文件路径:", config_path)

    # **连接 kmbox**
    try:
        kmbox = KmboxController(config_path=config_path)
    except Exception as e:
        print(f"❌ 连接 kmbox 失败: {e}")
        exit()

    # **等待 3 秒**
    print("⏳ 等待 3 秒...")
    time.sleep(3)

    # **获取当前位置**
    try:
        pos = kmbox.get_position()
        if pos:
            print(f"📍 当前位置: {pos}")
        else:
            print("⚠ 无法获取当前位置，检查 `km.getpos()` 是否正常工作")
    except Exception as e:
        print(f"❌ 获取位置失败: {e}")

    # **选择 Lua 文件**
    lua_script = choose_lua_script()

    # **运行 Lua 文件（复用 kmbox 串口）**
    if lua_script:
        try:
            print(f"\n🚀 正在执行 Lua 脚本: {lua_script}")
            lua_executor = KmboxLua(kmbox.serial)  # 复用 kmbox 串口
            with open(lua_script, "r", encoding="utf-8") as f:
                lua_code = f.read()
            lua_response = lua_executor.execute_lua(lua_code)
            print(f"📝 Lua 文件执行结果: {lua_response}")
        except Exception as e:
            print(f"❌ 执行 Lua 文件失败: {e}")

    # **关闭连接**
    try:
        kmbox.close()
    except Exception as e:
        print(f"❌ 关闭连接失败: {e}")

    print("✅ 任务完成，程序退出")
