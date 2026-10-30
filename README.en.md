# Skill 46 · Desktop Monitor & Control

> An importable desktop skill for general-purpose AI agents: pixel-level mouse & keyboard control, screen / window / clipboard operations, and desktop monitoring that auto-decides (or asks the user) based on permission level — ② change-triggered by default, ③ optional UI hooks.

Built on top of **[@matagul/desktop-control](https://clawhub.ai/matagul/desktop-control)** (official OpenClaw/ClawHub ecosystem skill, PyAutoGUI engine) with enhancements. Full attribution & enhancement notes: [CREDITS.md](./CREDITS.md).

---

## Feature Overview

| Capability | Description |
|------------|-------------|
| Mouse control | absolute / relative move, smooth bezier path, single/double/right/middle click, drag & drop, scroll, position tracking |
| Keyboard control | text input (configurable WPM), hotkeys, special keys, combos, key hold/release |
| Screen ops | full-screen / region screenshot, OpenCV template matching, pixel color, multi-monitor |
| Window management | window list, activate window, active window, state control |
| Clipboard | copy / read text |
| Desktop monitoring (NEW) | **② change-triggered** (periodic screenshot + pixel diff), **③ UI hooks** (SetWinEventHook event-level, optional) |
| Safety | failsafe corner abort, approval mode, boundary check, logging |

## Monitoring Decision Protocol (new core feature)

Monitoring mode is **auto-decided by the user's permission level / explicitly asked**:

1. **Auto mode (default)**: `ScreenMonitor(preference="auto")` detects process permission
   - non-admin → auto-select **② change-triggered** (low resource, no special permission)
   - admin → still defaults to **②**, with a hint that **③ UI hooks** can be upgraded to
2. **Explicit mode**: `preference="change"` forces change-triggered; `preference="ui_hook"` forces UI hooks
3. **Ask mode**: when a task needs event-level precision (e.g., watch a window open/close), the agent explains the trade-off and lets the user decide

| Mode | Module | Notes | Permission | Status |
|------|--------|-------|------------|--------|
| ② Change-triggered | `monitor/change_watch.py` | periodic screenshot + OpenCV pixel diff, wake on threshold | none | ✅ default |
| ③ UI hooks | `monitor/ui_hook.py` | SetWinEventHook event-level (foreground / move-resize / name change) | admin for full coverage | ✅ optional |
| ④ WGC frame capture | — | Windows.Graphics.Capture frame-level | high | ❌ not in v1 |
| ⑤ MCP wrapping | — | wrap as MCP server | — | 🔜 future |

## Install (universal agent Skill format)

This repo uses the **standard Skill package layout**: `skills/skill-46-desktop-monitor-control/`, importable by ClawHub / OpenClaw / Marvis and other agents that support local skill import.

### Option 1: import the skill directory

```bash
# Import skills/skill-46-desktop-monitor-control into your agent
# Marvis: skill_install(local_paths=["<abs path>/skills/skill-46-desktop-monitor-control"])
# ClawHub: clawhub install skill-46-desktop-monitor-control (after publishing)
```

### Option 2: pip dependencies

```bash
pip install pyautogui pillow opencv-python pygetwindow numpy
```

## Quick Start

```python
# 1. Desktop control
from desktop_control import DesktopController
dc = DesktopController(failsafe=True)
dc.move_mouse(500, 300, duration=0.3)
dc.click(100, 200)
dc.type_text("Hello", wpm=60)

# 2. Auto-decided desktop monitoring
from monitor import ScreenMonitor, detect_permission
print(detect_permission())
monitor = ScreenMonitor(preference="auto", interval=2.0, threshold=0.02)
monitor.on_event(lambda desc, payload: print(f"[wake] {desc}"))
monitor.start_async()
monitor.stop()

# 3. Block until screen changes (low-level helper)
from monitor.change_watch import watch_until_changed
ratio, img = watch_until_changed(interval=2.0, threshold=0.02, timeout=30)
if img:
    print(f"screen changed {ratio:.2%}")

# 4. UI hook event listening (optional, admin recommended)
from monitor.ui_hook import UIHookWatcher, is_admin, wait_for_event
hook = UIHookWatcher()
hook.on_event(lambda name, hwnd, info: print(f"[UI event] {name}: {info.get('title','')}"))
hook.start_async(); hook.stop()
```

## Directory Layout

```
skill-46-desktop-monitor-control/
├── SKILL.md               # unified skill protocol (frontmatter: name + description)
├── __init__.py            # DesktopController core
├── desktop_control.py     # same (compat for ai_agent import)
├── ai_agent.py            # AI desktop agent (vision + rule-based planning, optional)
├── monitor/
│   ├── __init__.py        # unified monitoring entry: auto decision by permission
│   ├── change_watch.py    # ② change-triggered: periodic screenshot + pixel diff
│   └── ui_hook.py         # ③ UI hooks: SetWinEventHook event-level
├── QUICK_REFERENCE.md     # control API cheatsheet
└── AI_AGENT_GUIDE.md      # AI agent guide
```

## License

[MIT](./LICENSE). Original implementation © [@matagul/desktop-control](https://clawhub.ai/matagul/desktop-control); this repo is an integrated & enhanced derivative.

---

*English README | [中文版 README](./README.md)*
