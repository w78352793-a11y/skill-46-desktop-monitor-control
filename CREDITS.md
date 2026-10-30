# 致谢与来源声明 / Credits & Attribution

## 中文版

### 借用来源

本技能基于以下开源技能整合增强：

| 来源 | 作者 | 说明 |
|------|------|------|
| [desktop-control](https://clawhub.ai/matagul/desktop-control) | **[@matagul](https://clawhub.ai/matagul)** | OpenClaw/ClawHub 官方生态技能（ClawHub 370★，v1.0.0，381 次安装）。基于 PyAutoGUI，提供像素级鼠标/键盘/屏幕/窗口/剪贴板操作，内置 failsafe 紧急中止、审批模式、边界检查。依赖 pyautogui + pillow + opencv-python + pygetwindow。支持 Windows。 |

整合时参考了该技能的中文本地化版本（OpenClaw-hot-skills-zh 社区镜像），主要保留原作者的操控核心实现（`DesktopController`）与 AI 代理框架（`AIDesktopAgent`），并对代码进行了审查与兼容性适配。

### 本仓库新增 / 增强内容

1. **桌面监控决策协议（核心新增）**：新增 `monitor/` 模块，实现"按用户授权权限自动判断 / 显式征询"的监控方式决策：
   - `monitor/change_watch.py` —— ②变化触发：定时截图 + OpenCV 像素差分，超阈值唤醒 AI（低资源、无需特殊权限）
   - `monitor/ui_hook.py` —— ③UI钩子：基于 ctypes `SetWinEventHook` 的事件级监听（前台切换/移动缩放/名称变化等，可选，管理员权限完整覆盖）
   - `monitor/__init__.py` —— 统一入口 `ScreenMonitor` / `choose_watcher` / `detect_permission`，按权限自动决策
2. **统一技能协议**：重写 `SKILL.md`，将操控能力与监控决策编排为单一协议（frontmatter: name + description），并附触发词与路由说明、故障排查表。
3. **兼容性适配**：`desktop_control.py` 副本保证 `ai_agent.py` 的 `from desktop_control import DesktopController` 导入路径可用。
4. **规范化发布**：标准 Skill 包目录布局（`skills/skill-46-desktop-monitor-control/`），兼容 ClawHub / OpenClaw / Marvis 等支持本地导入的智能体。

### 未纳入首版（规划中）

- ④ WGC 帧捕获（Windows.Graphics.Capture）：GPU 占用高，未纳入 v1
- ⑤ MCP 封装：将本技能包装为 MCP server，后续迭代

---

## English

### Attribution

This skill integrates and enhances the following open-source skill:

| Source | Author | Notes |
|--------|--------|-------|
| [desktop-control](https://clawhub.ai/matagul/desktop-control) | **[@matagul](https://clawhub.ai/matagul)** | Official OpenClaw/ClawHub ecosystem skill (370★, v1.0.0, 381 installs). PyAutoGUI-based pixel-level mouse/keyboard/screen/window/clipboard control with failsafe abort, approval mode, boundary checks. Deps: pyautogui + pillow + opencv-python + pygetwindow. Windows support. |

The Chinese localized mirror (OpenClaw-hot-skills-zh community repo) was used as the integration reference. The original author's control core (`DesktopController`) and AI agent framework (`AIDesktopAgent`) are retained, reviewed, and adapted for compatibility.

### What this repo adds / enhances

1. **Desktop monitoring decision protocol (core addition)**: new `monitor/` package implementing permission-based auto decision / explicit ask:
   - `monitor/change_watch.py` — ② change-triggered: periodic screenshot + OpenCV pixel diff, wakes AI when threshold exceeded (low resource, no special permission)
   - `monitor/ui_hook.py` — ③ UI hooks: ctypes `SetWinEventHook` event-level listening (foreground / move-resize / name-change, optional, admin for full coverage)
   - `monitor/__init__.py` — unified entry `ScreenMonitor` / `choose_watcher` / `detect_permission`
2. **Unified skill protocol**: rewritten `SKILL.md` composing control + monitoring decision into one protocol (frontmatter: name + description), with trigger words, routing, and troubleshooting table.
3. **Compatibility fix**: `desktop_control.py` copy so `ai_agent.py`'s `from desktop_control import DesktopController` import works.
4. **Standardized packaging**: standard Skill package layout (`skills/skill-46-desktop-monitor-control/`), importable by ClawHub / OpenClaw / Marvis and other local-import agents.

### Not in v1 (planned)

- ④ WGC frame capture (Windows.Graphics.Capture): high GPU usage, not in v1
- ⑤ MCP wrapping: package as MCP server, future iteration
