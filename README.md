# Skill 46 · 桌面实时监控与操控（Desktop Monitor & Control）

> 通用智能体（Agent）可导入的桌面技能：像素级鼠标键盘控制、屏幕/窗口/剪贴板操作，以及按用户授权情况自动决策的桌面监控（②变化触发为主、③UI 钩子可选）。

本技能基于 **[@matagul/desktop-control](https://clawhub.ai/matagul/desktop-control)**（OpenClaw/ClawHub 官方生态，PyAutoGUI 引擎）整合增强。完整来源与增强说明见 [CREDITS.md](./CREDITS.md)。

---

## 功能总览

| 能力 | 说明 |
|------|------|
| 鼠标控制 | 绝对/相对移动、平滑贝塞尔路径、单击/双击/右键/中键、拖放、滚动、位置追踪 |
| 键盘控制 | 文本输入（可调 WPM）、快捷键、特殊键、组合键、按住/释放 |
| 屏幕操作 | 全屏/区域截图、OpenCV 图像识别、像素颜色检测、多显示器 |
| 窗口管理 | 窗口列表、激活窗口、活动窗口、状态控制 |
| 剪贴板 | 复制 / 读取文本 |
| 桌面监控（新增） | **②变化触发**（定时截图+像素差分唤醒）、**③UI 钩子**（SetWinEventHook 事件级监听，可选） |
| 安全机制 | failsafe 角落中止、审批模式、边界检查、日志 |

## 监控方式决策协议（新增核心特性）

监控方式由 **用户授权权限自动判断 / 显式征询**：

1. **自动模式（默认）**：`ScreenMonitor(preference="auto")` 检测当前进程权限
   - 非管理员权限 → 自动选择 **②变化触发**（低资源、无需特殊权限）
   - 管理员权限 → 默认仍选 **②变化触发**，同时提示可升级 **③UI 钩子**
2. **显式指定**：`preference="change"` 强制变化触发；`preference="ui_hook"` 强制 UI 钩子
3. **征询场景**：任务需要事件级精准（如监听窗口打开/关闭）时，Agent 应向用户说明差异并让其决定

| 方式 | 模块 | 特点 | 权限要求 | 状态 |
|------|------|------|----------|------|
| ②变化触发 | `monitor/change_watch.py` | 定时截图+OpenCV像素差分，超阈值唤醒 | 无 | ✅ 默认 |
| ③UI钩子 | `monitor/ui_hook.py` | SetWinEventHook 事件级精准（前台切换/移动缩放/名称变化） | 管理员完整覆盖 | ✅ 可选 |
| ④WGC帧捕获 | — | Windows.Graphics.Capture 帧级捕获 | 高 | ❌ 首版未启用 |
| ⑤MCP封装 | — | 包装为 MCP server | — | 🔜 后续迭代 |

## 安装方法（通用智能体 Skill 格式）

本仓库采用**标准 Skill 包格式**：`skills/skill-46-desktop-monitor-control/`，兼容 ClawHub / OpenClaw / Marvis 等支持本地导入的智能体。

### 方式一：直接导入技能目录

```bash
# 将 skills/skill-46-desktop-monitor-control 目录导入你的智能体
# Marvis: skill_install(local_paths=["<绝对路径>/skills/skill-46-desktop-monitor-control"])
# ClawHub: clawhub install skill-46-desktop-monitor-control（发布后）
```

### 方式二：pip 依赖

```bash
pip install pyautogui pillow opencv-python pygetwindow numpy
```

## 快速开始

```python
# 1. 桌面操控
from desktop_control import DesktopController
dc = DesktopController(failsafe=True)
dc.move_mouse(500, 300, duration=0.3)
dc.click(100, 200)
dc.type_text("Hello", wpm=60)

# 2. 自动决策的桌面监控
from monitor import ScreenMonitor, detect_permission
print(detect_permission())                      # 查看授权情况
monitor = ScreenMonitor(preference="auto", interval=2.0, threshold=0.02)
monitor.on_event(lambda desc, payload: print(f"[唤醒] {desc}"))
monitor.start_async()                            # 后台监控
monitor.stop()

# 3. 阻塞等待屏幕变化（低层便捷函数）
from monitor.change_watch import watch_until_changed
ratio, img = watch_until_changed(interval=2.0, threshold=0.02, timeout=30)
if img:
    print(f"屏幕已变化 {ratio:.2%}")

# 4. UI 钩子事件监听（可选，需管理员权限获得完整覆盖）
from monitor.ui_hook import UIHookWatcher, is_admin, wait_for_event
hook = UIHookWatcher()
hook.on_event(lambda name, hwnd, info: print(f"[UI事件] {name}: {info.get('title','')}"))
hook.start_async(); hook.stop()
```

## 目录结构

```
skill-46-desktop-monitor-control/
├── SKILL.md               # 统一技能协议（frontmatter: name + description）
├── __init__.py            # DesktopController 操控核心
├── desktop_control.py     # 同上（兼容 ai_agent 导入）
├── ai_agent.py            # AI 桌面代理（视觉+规则规划+执行，可选）
├── monitor/
│   ├── __init__.py        # 统一监控入口：按权限自动决策监控方式
│   ├── change_watch.py    # ②变化触发：定时截图+像素差分
│   └── ui_hook.py         # ③UI钩子：SetWinEventHook 事件级监听
├── QUICK_REFERENCE.md     # 操控 API 速查
└── AI_AGENT_GUIDE.md      # AI 代理使用指南
```

## License

[MIT](./LICENSE)，原始实现版权归 [@matagul/desktop-control](https://clawhub.ai/matagul/desktop-control) 作者所有，本仓库为整合增强版本。

---

*中文版 README | [English README](./README.en.md)*
