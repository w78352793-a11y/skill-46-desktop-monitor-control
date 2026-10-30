"""
UI 事件钩子监控模块（监控方式③，可选）
基于 Win32 SetWinEventHook 监听窗口创建/激活/移动/大小变化等事件，实现事件级精准监控。

注意：部分系统事件受 UIPI（用户界面特权隔离）限制，需要以管理员权限运行
才能监听到更高级别权限进程（如部分系统窗口）的 UI 事件。

用法:
    from monitor.ui_hook import UIHookWatcher, is_admin
    if not is_admin():
        print("建议以管理员权限运行以获得完整事件覆盖")
    hook = UIHookWatcher()
    hook.on_event(lambda event, hwnd, info: print(event, info))
    hook.start()       # 阻塞
    hook.stop()
"""

import ctypes
import ctypes.wintypes as wt
import logging
import threading
import time
from typing import Callable, Dict, Optional

logger = logging.getLogger(__name__)

# WinEvent 常量（常用子集）
EVENT_MIN = 0x00000001
EVENT_MAX = 0x7FFFFFFF
EVENT_SYSTEM_FOREGROUND = 0x0003       # 前台窗口切换
EVENT_SYSTEM_MOVESIZESTART = 0x000A    # 移动/缩放开始
EVENT_SYSTEM_MOVESIZEEND = 0x000B      # 移动/缩放结束
EVENT_SYSTEM_CAPTURESTART = 0x0008
EVENT_SYSTEM_CAPTUREEND = 0x0009
EVENT_SYSTEM_MINIMIZESTART = 0x0016
EVENT_SYSTEM_MINIMIZEEND = 0x0017
EVENT_OBJECT_CREATE = 0x8000           # 对象创建
EVENT_OBJECT_DESTROY = 0x8001          # 对象销毁
EVENT_OBJECT_SHOW = 0x8002             # 对象显示
EVENT_OBJECT_HIDE = 0x8003             # 对象隐藏
EVENT_OBJECT_NAMECHANGE = 0x800C       # 名称变化

EVENT_NAMES: Dict[int, str] = {
    EVENT_SYSTEM_FOREGROUND: "前台窗口切换",
    EVENT_SYSTEM_MOVESIZESTART: "窗口移动/缩放开始",
    EVENT_SYSTEM_MOVESIZEEND: "窗口移动/缩放结束",
    EVENT_SYSTEM_CAPTURESTART: "捕获开始",
    EVENT_SYSTEM_CAPTUREEND: "捕获结束",
    EVENT_SYSTEM_MINIMIZESTART: "窗口最小化开始",
    EVENT_SYSTEM_MINIMIZEEND: "窗口最小化结束",
    EVENT_OBJECT_CREATE: "对象创建",
    EVENT_OBJECT_DESTROY: "对象销毁",
    EVENT_OBJECT_SHOW: "对象显示",
    EVENT_OBJECT_HIDE: "对象隐藏",
    EVENT_OBJECT_NAMECHANGE: "名称变化",
}

# WinEventProc 回调原型
WinEventProc = ctypes.WINFUNCTYPE(
    None,
    wt.HANDLE,   # hWinEventHook
    wt.DWORD,    # event
    wt.HWND,     # hwnd
    wt.LONG,     # idObject
    wt.LONG,     # idChild
    wt.DWORD,    # dwEventThread
    wt.DWORD,    # dwmsEventTime
)

# 用户32
user32 = ctypes.windll.user32
ole32 = ctypes.windll.ole32


def is_admin() -> bool:
    """检测当前进程是否以管理员权限运行。"""
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def get_window_title(hwnd: int) -> str:
    """获取窗口标题。"""
    try:
        length = user32.GetWindowTextLengthW(hwnd)
        buf = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, buf, length + 1)
        return buf.value
    except Exception:
        return ""


def get_window_class(hwnd: int) -> str:
    """获取窗口类名。"""
    try:
        buf = ctypes.create_unicode_buffer(256)
        user32.GetClassNameW(hwnd, buf, 256)
        return buf.value
    except Exception:
        return ""


class UIHookWatcher:
    """
    基于 SetWinEventHook 的 UI 事件监控器。

    事件回调签名: callback(event_name, hwnd, info)
      event_name: 事件中文名（见 EVENT_NAMES）
      hwnd: 关联窗口句柄
      info: dict(title=窗口标题, class_name=窗口类名)
    """

    def __init__(self, events: Optional[list] = None):
        """
        Args:
            events: 要监听的事件列表，默认监听前台切换与窗口移动/缩放。
                可组合 EVENT_SYSTEM_FOREGROUND / EVENT_SYSTEM_MOVESIZEEND 等。
        """
        self.events = events or [EVENT_SYSTEM_FOREGROUND, EVENT_SYSTEM_MOVESIZEEND, EVENT_OBJECT_NAMECHANGE]
        self._callback: Optional[Callable] = None
        self._hook_handles: list = []
        self._message_thread: Optional[threading.Thread] = None
        self._running = False
        self._event_count = 0

    # ---------- 公共 API ----------

    def on_event(self, callback: Callable[[str, int, Dict], None]) -> "UIHookWatcher":
        """注册事件回调：callback(event_name, hwnd, info)。"""
        self._callback = callback
        return self

    def start(self) -> None:
        """启动监听（阻塞，需消息循环）。"""
        self._running = True
        if not is_admin():
            logger.warning("当前非管理员权限，部分系统 UI 事件可能无法捕获（UIPI 限制）")

        # CoInitialize 供 Oleacc 相关事件使用（部分 EVENT_OBJECT 事件需要）
        ole32.CoInitialize(None)

        self._callback_fn = WinEventProc(self._dispatch_event)

        for ev in self.events:
            handle = user32.SetWinEventHook(
                ev, ev, 0, self._callback_fn, 0, 0, 0x0000  # WINEVENT_OUTOFCONTEXT
            )
            if handle:
                self._hook_handles.append(handle)
                logger.info(f"已注册事件钩子: {EVENT_NAMES.get(ev, hex(ev))}")
            else:
                logger.error(f"注册事件钩子失败: {EVENT_NAMES.get(ev, hex(ev))}")

        if not self._hook_handles:
            raise RuntimeError("未成功注册任何 UI 事件钩子")

        logger.info("UI 钩子监控启动，等待消息循环...")
        # 消息循环（阻塞）
        msg = wt.MSG()
        while self._running:
            result = user32.GetMessageW(ctypes.byref(msg), 0, 0, 0)
            if result == 0:  # WM_QUIT
                break
            if result == -1:
                logger.error("GetMessage 失败")
                break
            user32.TranslateMessage(ctypes.byref(msg))
            user32.DispatchMessageW(ctypes.byref(msg))

    def start_async(self) -> None:
        """后台线程启动监听。"""
        if self._message_thread and self._message_thread.is_alive():
            logger.warning("UI 钩子已在运行")
            return
        self._message_thread = threading.Thread(target=self.start, daemon=True)
        self._message_thread.start()
        logger.info("UI 钩子监控已在线程中启动")

    def stop(self) -> None:
        """停止监听并注销钩子。"""
        self._running = False
        for handle in self._hook_handles:
            user32.UnhookWinEvent(handle)
        self._hook_handles.clear()
        ole32.CoUninitialize()
        logger.info("UI 钩子监控已停止")

    @property
    def event_count(self) -> int:
        """累计捕获事件数。"""
        return self._event_count

    # ---------- 内部实现 ----------

    def _dispatch_event(self, hook, event, hwnd, id_obj, id_child, thread_id, event_time):
        """WinEventProc 回调（在钩子线程内被调用）。"""
        self._event_count += 1
        if not self._callback:
            return
        name = EVENT_NAMES.get(event, hex(event))
        info = {}
        if hwnd:
            info["title"] = get_window_title(hwnd)
            info["class_name"] = get_window_class(hwnd)
        info["id_object"] = id_obj
        info["id_child"] = id_child
        try:
            self._callback(name, hwnd, info)
        except Exception as e:
            logger.error(f"UI 事件回调失败: {e}")


def wait_for_event(
    events: Optional[list] = None,
    timeout: Optional[float] = None,
) -> Optional[Dict]:
    """
    便捷函数：阻塞等待首个目标 UI 事件。

    Returns:
        dict(event=事件名, hwnd=窗口句柄, info=详情)，超时返回 None
    """
    result: Dict = {}
    hook = UIHookWatcher(events=events)
    hook.on_event(lambda name, hwnd, info: result.update(event=name, hwnd=hwnd, info=info))
    t = threading.Thread(target=hook.start, daemon=True)
    t.start()
    start = time.time()
    while not result:
        if timeout is not None and time.time() - start > timeout:
            hook.stop()
            return None
        time.sleep(0.1)
    hook.stop()
    return result
