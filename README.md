1.安装anaconda和vscode

2.vscode的扩展(快捷键Ctrl Shift X)安装Python拓展(必须)和Chinese语言(如果你需要)
-直接搜索Python/Chinese即可

3.在Anaconda Prompt中 cd到你的脚本的安装目录(确保没有中文)
pip install -r requirements.txt (安装所需的运行库)

4.Steam中右键守望先锋 属性 通用 启动选项中 粘贴下面的启动项
--lobbyMap=0x0800000000001999
这样会启动Steam大厅背景是黑屏 为了提高视图效率和精确度
Steam的这个设置换号不会跟随 所以如果换号刷需要重新设置

5.Windows显示设置设为1920*1080 100%缩放

6.vscode中运行test.py
依次点击 游戏-英雄精通-莱因哈特 然后按下F8开始 F10中断

7.游戏语言最好是简体中文 因为我在本地pic文件夹图片源文件还有代码中对识图划定的范围都是用的简体中文 其他语言可能会出现位置不对的情况 需要自行更改代码修正

8.在代码开头部分有几个数值
max_executions = 150 这个是最大循环次数 在150次后会自动重启游戏防止游戏卡顿刷战令失效
join_game_timesleep = 30 这个是进入游戏后的等待延迟 在自动重启游戏后从启动游戏到开始自动点击 游戏-英雄精通-莱因哈特 的等待时间
extra_time_sleep = 0 额外等待时间 如果你在英雄精通内停留时间不够5秒 就给这个赋值 比如在游戏内停留时间为三秒就赋值为2


此脚本已经几个月没有更新 坐标版大概率已经全部不对 识图版也需要更新图片和扫描范围
ctypes + user32.dll 出现过追封行为 自追封后本项目便搁置
使用风险自行承担

![image](https://github.com/user-attachments/assets/5d521c8f-5416-4d33-b7ed-5d9087538ac4)
此项目从2024年国庆前维护至今
