# 桌面控制 - 快速参考卡

## 🚀 即时开始

```python
from skills.desktop_control import DesktopController

dc = DesktopController()
```

## 🖱️ 鼠标控制（前 10 名）

```python
# 1. 移动鼠标
dc.move_mouse(500, 300, duration=0.5)

# 2. 点击
dc.click(500, 300)  # 在位置左键点击
dc.click()           # 在当前位置点击

# 3. 右键点击
dc.right_click(500, 300)

# 4. 双击
dc.double_click(500, 300)

# 5. 拖放
dc.drag(100, 100, 500, 500, duration=1.0)

# 6. 滚动
dc.scroll(-5)  # 向下滚动 5 次

# 7. 获取位置
x, y = dc.get_mouse_position()

# 8. 相对移动
dc.move_relative(100, 50)  # 向右移动 100px，向下 50px

# 9. 平滑移动
dc.move_mouse(1000, 500, duration=1.0, smooth=True)

# 10. 中键点击
dc.middle_click()
```

## ⌨️ 键盘控制（前 10 名）

```python
# 1. 输入文本（瞬间）
dc.type_text("Hello World")

# 2. 输入文本（拟人化，60 WPM）
dc.type_text("Hello World", wpm=60)

# 3. 按键
dc.press('enter')
dc.press('tab')
dc.press('escape')

# 4. 快捷键
dc.hotkey('ctrl', 'c')      # 复制
dc.hotkey('ctrl', 'v')      # 粘贴  
dc.hotkey('ctrl', 's')      # 保存
dc.hotkey('win', 'r')       # 运行对话框
dc.hotkey('alt', 'tab')     # 切换窗口

# 5. 按住与释放
dc.key_down('shift')
dc.type_text("hello")  # 输入 "HELLO"
dc.key_up('shift')

# 6. 方向键
dc.press('up')
dc.press('down')
dc.press('left')
dc.press('right')

# 7. 功能键
dc.press('f5')  # 刷新

# 8. 多次按下
dc.press('backspace', presses=5)

# 9. 特殊键
dc.press('home')
dc.press('end')
dc.press('pagedown')
dc.press('delete')

# 10. 快速组合
dc.hotkey('ctrl', 'alt', 'delete')
```

## 📸 屏幕操作（前 5 名）

```python
# 1. 截图（全屏）
img = dc.screenshot()
dc.screenshot(filename="screen.png")

# 2. 截图（区域）
img = dc.screenshot(region=(100, 100, 800, 600))

# 3. 获取像素颜色
r, g, b = dc.get_pixel_color(500, 300)

# 4. 在屏幕上查找图像
location = dc.find_on_screen("button.png")

# 5. 获取屏幕大小
width, height = dc.get_screen_size()
```

## 🪟 窗口管理（前 5 名）

```python
# 1. 获取所有窗口
windows = dc.get_all_windows()

# 2. 激活窗口
dc.activate_window("Chrome")

# 3. 获取活动窗口
active = dc.get_active_window()

# 4. 列出窗口
for title in dc.get_all_windows():
    print(title)

# 5. 切换到应用
dc.activate_window("Visual Studio Code")
```

## 📋 剪贴板（前 2 名）

```python
# 1. 复制到剪贴板
dc.copy_to_clipboard("Hello!")

# 2. 从剪贴板获取
text = dc.get_from_clipboard()
```

## 🔥 现实世界示例

### 示例 1：自动填充表单
```python
dc.click(300, 200)  # 姓名字段
dc.type_text("John Doe", wpm=80)
dc.press('tab')
dc.type_text("john@email.com", wpm=80)
dc.press('tab')
dc.type_text("Password123", wpm=60)
dc.press('enter')
```

### 示例 2：复制粘贴自动化
```python
# 全选
dc.hotkey('ctrl', 'a')
# 复制
dc.hotkey('ctrl', 'c')
# 等待
dc.pause(0.5)
# 切换窗口
dc.hotkey('alt', 'tab')
# 粘贴
dc.hotkey('ctrl', 'v')
```

### 示例 3：文件操作
```python
# 选择多个文件
dc.key_down('ctrl')
dc.click(100, 200)
dc.click(100, 250)
dc.click(100, 300)
dc.key_up('ctrl')
# 复制
dc.hotkey('ctrl', 'c')
```

### 示例 4：截图工作流
```python
# 截图
dc.screenshot(filename=f"capture_{time.time()}.png")
# 在 Paint 中打开
dc.hotkey('win', 'r')
dc.pause(0.5)
dc.type_text('mspaint')
dc.press('enter')
```

### 示例 5：查找与替换
```python
# 打开查找与替换
dc.hotkey('ctrl', 'h')
dc.pause(0.3)
# 输入查找文本
dc.type_text("old_text")
dc.press('tab')
# 输入替换文本
dc.type_text("new_text")
# 全部替换
dc.hotkey('alt', 'a')
```

## ⚙️ 配置

```python
# 带故障保护（移到角落中止）
dc = DesktopController(failsafe=True)

# 带批准模式（每个操作前询问）
dc = DesktopController(require_approval=True)

# 最大速度（无安全检查）
dc = DesktopController(failsafe=False)
```

## 🛡️ 安全

```python
# 检查是否安全继续
if dc.is_safe():
    dc.click(500, 500)

# 暂停执行
dc.pause(2.0)  # 等待 2 秒

# 紧急中止：将鼠标移到任意屏幕角落
```

## 🎯 专业提示

1. **瞬间输入**：`interval=0` 或 `wpm=None`
2. **拟人输入**：`wpm=60`（60 字/分钟）
3. **平滑鼠标**：`duration=0.5, smooth=True`
4. **瞬间鼠标**：`duration=0`
5. **等待 UI**：动作之间使用 `dc.pause(0.5)`
6. **故障保护**：始终启用以确保安全
7. **先测试**：使用 `demo.py` 测试功能
8. **坐标**：使用 `get_mouse_position()` 查找它们
9. **截图**：捕获前后截图以进行验证
10. **快捷键 > 菜单**：更快更可靠

## 📦 依赖

```bash
pip install pyautogui pillow opencv-python pygetwindow pyperclip
```

## 🚨 常见问题

**鼠标移动不正确？**
- 检查 Windows 设置中的 DPI 缩放
- 使用 `get_mouse_position()` 验证坐标

**键盘不工作？**
- 确保目标应用有焦点
- 某些应用阻止自动化（游戏、安全应用）

**故障保护触发？**
- 让鼠标远离屏幕角落
- 如需要可禁用：`failsafe=False`

---

**为 OpenClaw 构建** 🦞 - 桌面自动化变得简单！
