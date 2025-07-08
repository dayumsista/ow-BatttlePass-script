function move_device(x, y, delay)
    km.move(x, y)  -- 移动设备，而不是鼠标
    os.execute("sleep " .. (delay / 1000))  -- 适配 `kmbox` 的 Lua 休眠
end

-- 开始执行设备移动
move_device(100, 0, 500)  -- 右移 100
move_device(0, 100, 500)  -- 下移 100
move_device(-100, 0, 500) -- 左移 100
move_device(0, -100, 500) -- 上移 100
