"""
技能46 · 桌面监控统一入口与监控方式决策

监控方式（按用户方案取舍）:
  ② 变化触发为主: 定时截图 + 像素差分（change_watch）—— 默认，低资源，无需特殊权限
  ③ UI 钩子(可选): SetWinEventHook 事件级精准监控（ui_hook）—— 需管理员权限获得完整覆盖
  ④ WGC 帧捕获: 首版不启用（暂不支持）
  ⑤ MCP 封装: 后续迭代计划

决策规则: 根据当前进程权限自动判断可用的监控方式，
  并可通过 preference 参数由用户显式指定。
"""

import logging
from typing import Optional, Union

logger = logging.getLogger(__name__)

MONITOR_MODES = {
    "change": "②变化触发（定时截图+像素差分，默认，低资源）",
    "ui_hook": "③UI钩子（SetWinEventHook 事件级精准，需管理员权限）",
    "wgc": "④WGC帧捕获（首版不启用）",
    "mcp": "⑤MCP封装（后续迭代）",
}


def detect_permission() -> dict:
    """
    检测当前运行环境的授权情况。
    Returns:
        dict(is_admin=是否管理员, can_ui_hook=UI钩子可用性, note=说明)
    """
    from .ui_hook import is_admin

    admin = is_admin()
    return {
        "is_admin": admin,
        "can_ui_hook": admin,  # UI 钩子完整覆盖需要管理员；非管理员可监听低权限进程事件
        "note": "管理员权限" if admin else "非管理员权限（UI钩子只能捕获普通权限进程事件）",
    }


def choose_watcher(preference: Optional[str] = None) -> dict:
    """
    根据用户授权情况自动判断/由 preference 指定监控方式。

    Args:
        preference: None/auto=按权限自动选择；'change'=强制变化触发；'ui_hook'=强制UI钩子

    Returns:
        dict(mode=方式key, mode_name=方式名, watcher_cls=监控器类, permission=权限信息)
    """
    permission = detect_permission()

    if preference in ("change", "ui_hook"):
        mode = preference
    elif preference is None or preference in ("auto", "自动", ""):
        # 自动决策：默认变化触发；仅当管理员权限且用户要求事件级时才建议 UI 钩子
        mode = "change"
    else:
        raise ValueError(f"未知监控方式: {preference}，可选: change / ui_hook / auto")

    if mode == "change":
        from .change_watch import ScreenChangeWatcher
        cls = ScreenChangeWatcher
        note = "已选择②变化触发（默认，低资源，无需特殊权限）"
    else:
        from .ui_hook import UIHookWatcher
        cls = UIHookWatcher
        if not permission["is_admin"]:
            note = "已选择③UI钩子，但当前为非管理员权限，部分系统事件无法捕获；建议以管理员权限运行"
        else:
            note = "已选择③UI钩子（管理员权限，事件级精准监控）"

    return {
        "mode": mode,
        "mode_name": MONITOR_MODES[mode],
        "watcher_cls": cls,
        "permission": permission,
        "note": note,
    }


class ScreenMonitor:
    """
    统一监控入口：自动或按用户指定选择监控方式并启动。

    用法:
        monitor = ScreenMonitor(preference="auto")   # 按权限自动选择
        monitor.on_event(callback)                    # 注册回调
        monitor.start_async()                          # 后台启动
        monitor.stop()
    """

    def __init__(self, preference: Optional[str] = None, **kwargs):
        choice = choose_watcher(preference)
        self.mode = choice["mode"]
        self.mode_name = choice["mode_name"]
        self.permission = choice["permission"]
        self.note = choice["note"]
        logger.info(self.note)

        self.watcher = choice["watcher_cls"](**kwargs)
        self._callback = None
        self._event_adapter = None

    def on_event(self, callback) -> "ScreenMonitor":
        """注册统一回调：callback(event_desc, payload)。event_desc 为可读事件描述。"""
        self._callback = callback
        if self.mode == "change":
            def change_adapter(ratio, img):
                if self._callback:
                    self._callback(f"屏幕变化 {ratio:.2%}", {"diff_ratio": ratio, "image": img})
            self.watcher.on_change(change_adapter)
        else:
            def hook_adapter(name, hwnd, info):
                if self._callback:
                    self._callback(f"UI事件:{name}", {"hwnd": hwnd, "info": info})
            self.watcher.on_event(hook_adapter)
        return self

    def start(self):
        """阻塞式启动。"""
        self.watcher.start()

    def start_async(self):
        """后台线程启动。"""
        self.watcher.start_async()

    def stop(self):
        """停止监控。"""
        self.watcher.stop()

    def status(self) -> str:
        """返回当前监控状态描述。"""
        return (
            f"监控方式: {self.mode_name}\n"
            f"权限: {self.permission['note']}\n"
            f"状态: {self.note}"
        )
