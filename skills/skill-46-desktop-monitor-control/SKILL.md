---
name: skill-46-desktop-monitor-control
description: 技能46·桌面实时监控与操控一体技能：像素级鼠标键盘控制、屏幕/窗口/剪贴板操作，以及按用户授权情况自动决策的桌面监控（②变化触发为主、③UI钩子可选）。用于桌面自动化、屏幕变化感知、窗口事件监听、AI 驱动桌面任务等场景。
---

# 技能46 · 桌面实时监控与操控

将 **desktop-control**（@matagul，PyAutoGUI 引擎）的桌面操控能力，与用户自定义监控方案（②变化触发为主、③UI钩子可选、④WGC暂不选、⑤MCP后续）整合为统一技能。

## 一、技能构成

```
skill-46-desktop-monitor-control/
├── SKILL.md               # 本协议
├── __init__.py            # DesktopController 操控核心（像素级鼠标/键盘/屏幕/窗口/剪贴板）
├── desktop_control.py     # 同上（兼容 ai_agent 导入）
├── ai_agent.py            # AI 桌面代理（视觉+规则规划+执行的自主任务框架，可选）
├── monitor/
│   ├── __init__.py        # 统一监控入口：按权限自动决策监控方式
│   ├── change_watch.py    # ②变化触发：定时截图+像素差分，超阈值唤醒
│   └── ui_hook.py         # ③UI钩子：SetWinEventHook 事件级精准监控（可选）
├── QUICK_REFERENCE.md     # 操控 API 速查
└── AI_AGENT_GUIDE.md      # AI 代理使用指南
```

## 二、依赖

```bash
pip install pyautogui pillow opencv-python pygetwindow numpy
```

- `pyautogui` / `pillow` / `pyperclip`：操控核心（已内置）
- `opencv-python` / `numpy`：变化触发监控（需补充）
- `pygetwindow`：窗口管理（需补充）

## 三、监控方式决策协议（用户授权自动判断/征询）

监控方式按用户方案取舍为 ②③④⑤ 四条路线，**首版落地 ②为主、③可选、④暂不选、⑤后续MCP**。

### 3.1 决策规则

1. **自动模式（默认）**：调用 `monitor.choose_watcher(preference=None)` 或 `ScreenMonitor(preference="auto")`，由当前进程授权权限自动判断：
   - 非管理员权限 → 自动选择 **②变化触发**（定时截图+OpenCV像素diff，低资源、无需特殊权限）；
   - 管理员权限 → 仍默认 **②变化触发**，同时提示可升级为 **③UI钩子** 获取事件级精准监控。
2. **用户显式指定**：`preference="change"` 强制变化触发；`preference="ui_hook"` 强制 UI 钩子（非管理员时给出权限警告）。
3. **权限检测**：`monitor.detect_permission()` 返回 `is_admin` / `can_ui_hook` / `note`，供决策与用户说明。
4. **征询场景**：当用户未明确指定、且任务需要事件级精准（如监听某窗口打开/关闭）时，Agent 应向用户说明两种方式差异并让用户决定；一般屏幕感知任务直接自动选择 ②，无需征询。

### 3.2 方式说明

| 方式 | 模块 | 特点 | 权限要求 | 首版状态 |
|------|------|------|----------|----------|
| ②变化触发 | `monitor.change_watch` | 定时截图+像素差分，超阈值唤醒，低资源 | 无 | ✅ 启用（默认） |
| ③UI钩子 | `monitor.ui_hook` | SetWinEventHook 事件级精准（前台切换/移动缩放/名称变化等） | 管理员获得完整覆盖 | ✅ 可选 |
| ④WGC帧捕获 | — | Windows Graphics Capture 帧级捕获 | 高 | ❌ 暂不选 |
| ⑤MCP封装 | — | 将本技能包装为 MCP server | — | 🔜 后续迭代 |

### 3.3 变化触发监控用法（②）

```python
from monitor import ScreenMonitor, choose_watcher, detect_permission

perm = detect_permission()          # 查看授权情况
choice = choose_watcher()           # 自动决策（通常返回 change）
print(choice["note"])               # 如: 已选择②变化触发（默认，低资源，无需特殊权限）

# 统一入口
monitor = ScreenMonitor(preference="auto", interval=2.0, threshold=0.02)
monitor.on_event(lambda desc, payload: print(f"[唤醒] {desc}"))
monitor.start_async()               # 后台监控
# ... 业务逻辑 ...
monitor.stop()

# 或低层直接使用
from monitor.change_watch import ScreenChangeWatcher, watch_until_changed
ratio, img = watch_until_changed(interval=2.0, threshold=0.02, timeout=30)
if img:
    print(f"屏幕已变化 {ratio:.2%}，可唤醒 AI 处理")
```

### 3.4 UI 钩子监控用法（③，可选）

```python
from monitor.ui_hook import UIHookWatcher, is_admin, wait_for_event

if not is_admin():
    print("非管理员权限：部分系统 UI 事件无法捕获，建议以管理员运行")

hook = UIHookWatcher()              # 默认监听: 前台切换/移动缩放结束/名称变化
hook.on_event(lambda name, hwnd, info: print(f"[UI事件] {name}: {info.get('title','')}"))
hook.start_async()
hook.stop()

ev = wait_for_event(timeout=30)     # 阻塞等待首个 UI 事件
```

## 四、操控能力（desktop-control 核心 API）

### 鼠标

```python
from desktop_control import DesktopController
dc = DesktopController(failsafe=True, require_approval=False)

dc.move_mouse(500, 300, duration=0.3)        # 平滑移动
dc.click(100, 200)                           # 指定位置左键单击
dc.click(button='right')                     # 右键
dc.double_click(300, 300)                    # 双击
dc.drag(100, 100, 500, 500, duration=1.0)    # 拖放
dc.scroll(-5)                                # 向下滚动
x, y = dc.get_mouse_position()               # 当前坐标
```

### 键盘

```python
dc.type_text("Hello", wpm=60)                # 拟人化输入
dc.hotkey('ctrl', 'c')                       # 复制
dc.press('enter')                            # 回车
dc.key_down('ctrl'); dc.click(...); dc.key_up('ctrl')  # 多选
```

### 屏幕

```python
img = dc.screenshot(region=(100, 100, 500, 300))   # 区域截图
dc.screenshot(filename="shot.png")                 # 截图保存
r, g, b = dc.get_pixel_color(500, 300)             # 像素颜色
loc = dc.find_on_screen("button.png", confidence=0.8)  # 图像识别（需OpenCV）
w, h = dc.get_screen_size()
```

### 窗口

```python
dc.get_all_windows()          # 窗口标题列表
dc.activate_window("Chrome")  # 激活窗口
dc.get_active_window()        # 当前焦点窗口
```

### 剪贴板

```python
dc.copy_to_clipboard("text")
text = dc.get_from_clipboard()
```

### 安全机制

- `failsafe=True`（默认）：鼠标移到屏幕角落立即中止自动化；
- `require_approval=True`：每次操作前请求用户确认；
- `dc.is_safe()`：执行前安全检查；
- `dc.pause(sec)`：暂停。

## 五、AI 桌面代理（可选）

```python
from ai_agent import AIDesktopAgent, create_agent
agent = create_agent(failsafe=True)
result = agent.execute_task("打开记事本输入文字并截图")
```

规则式规划引擎（画图/输入/游戏/打开应用四类模板），LLM 规划为 TODO 扩展点；任务执行每步截图留痕。

## 六、触发词与路由

- 桌面操控：鼠标/键盘/点击/输入/拖拽/截图/图像识别/窗口激活/剪贴板
- 桌面监控：监控屏幕/屏幕变化/等待变化/变化唤醒/监听窗口/UI事件/前台切换
- 综合任务：帮我操作电脑/自动操作/桌面自动化/AI桌面代理

Agent 收到上述意图时优先加载本技能；涉及 App 界面交互（点击/滑动/输入）仍按 Marvis 路由派发 app-agent，本技能作为底层操控执行层。

## 七、故障排查

| 问题 | 处理 |
|------|------|
| 鼠标位置偏移 | 检查 Windows DPI 缩放，用 `get_screen_size()` 确认分辨率 |
| 键盘输入失效 | 确保目标窗口有焦点；部分应用需管理员权限 |
| 变化监控未触发 | 调低 `threshold`（默认0.02）；确认 `opencv-python` 已安装 |
| UI钩子覆盖不全 | 以管理员权限运行；监听事件子集需自行扩展 EVENT 常量 |
| failsafe 误触发 | 将鼠标移离角落；或 `failsafe=False`（谨慎） |
