"""
变化触发监控模块（监控方式②）
定时截图 + OpenCV 像素差分：屏幕变化超过阈值时唤醒 AI。

特点：低资源、无需特殊权限、适用于大多数桌面监控场景。
"""

import time
import logging
from typing import Callable, Optional, Tuple

logger = logging.getLogger(__name__)

try:
    import numpy as np
except ImportError:
    np = None


class ScreenChangeWatcher:
    """
    基于定时截图 + 像素差分的屏幕变化监控器。

    用法:
        from monitor.change_watch import ScreenChangeWatcher
        watcher = ScreenChangeWatcher(interval=2.0, threshold=0.02)
        watcher.on_change(lambda diff, img: print(f"屏幕变化: {diff:.2%}"))
        watcher.start()          # 阻塞运行；或
        watcher.start_async()    # 后台线程运行
        watcher.stop()
    """

    def __init__(
        self,
        interval: float = 2.0,
        threshold: float = 0.02,
        region: Optional[Tuple[int, int, int, int]] = None,
        scale: float = 0.5,
        cooldown: float = 1.0,
        use_gray: bool = True,
    ):
        """
        Args:
            interval: 截图间隔（秒），默认 2 秒
            threshold: 变化阈值 0~1，像素差异比例超过该值触发回调，默认 0.02（2%）
            region: 监控区域 (left, top, width, height)，None 表示全屏
            scale: 缩放比例 0~1，先缩小再比较以降低 CPU，默认 0.5
            cooldown: 触发回调后的冷却时间（秒），避免高频重复唤醒
            use_gray: 是否转灰度比较（省资源），默认 True
        """
        self.interval = interval
        self.threshold = threshold
        self.region = region
        self.scale = scale
        self.cooldown = cooldown
        self.use_gray = use_gray

        self._running = False
        self._thread = None
        self._callback: Optional[Callable] = None
        self._last_frame = None
        self._last_trigger_time = 0.0
        self._changed_count = 0

        # 延迟导入，允许在缺少 OpenCV 时仍可实例化并提示
        self._cv2 = None

    # ---------- 公共 API ----------

    def on_change(self, callback: Callable[[float, object], None]) -> "ScreenChangeWatcher":
        """注册变化回调：callback(diff_ratio, pil_image)，diff_ratio 为 0~1 的差异比例。"""
        self._callback = callback
        return self

    def start(self) -> None:
        """阻塞式启动监控（Ctrl+C 或调用 stop 停止）。"""
        self._running = True
        self._ensure_cv2()
        logger.info(f"变化监控启动: interval={self.interval}s threshold={self.threshold}")
        try:
            while self._running:
                self._tick()
                time.sleep(self.interval)
        except KeyboardInterrupt:
            self.stop()
        except Exception as e:
            logger.error(f"变化监控异常: {e}")
            self.stop()

    def start_async(self) -> None:
        """后台线程启动监控。"""
        import threading
        if self._thread and self._thread.is_alive():
            logger.warning("监控已在运行")
            return
        self._running = True
        self._thread = threading.Thread(target=self.start, daemon=True)
        self._thread.start()
        logger.info("变化监控已在线程中启动")

    def stop(self) -> None:
        """停止监控。"""
        self._running = False
        logger.info("变化监控已停止")

    @property
    def changed_count(self) -> int:
        """累计触发次数。"""
        return self._changed_count

    # ---------- 内部实现 ----------

    def _ensure_cv2(self) -> None:
        if self._cv2 is not None:
            return
        try:
            import cv2
            self._cv2 = cv2
        except ImportError:
            raise ImportError(
                "变化监控需要 opencv-python 与 numpy，请先安装: pip install opencv-python numpy"
            )

    def _tick(self) -> None:
        import pyautogui
        import io

        self._ensure_cv2()
        cv2 = self._cv2

        img = pyautogui.screenshot(region=self.region)

        # 转 numpy 数组
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        # 直接通过 PIL 转数组（避免额外编码开销）
        import numpy as _np
        frame = _np.array(img.convert("L") if self.use_gray else img)

        # 缩放以降低比较成本
        if self.scale < 1.0:
            h, w = frame.shape[:2]
            frame = cv2.resize(frame, (max(1, int(w * self.scale)), max(1, int(h * self.scale))))

        if self._last_frame is None:
            self._last_frame = frame
            return

        # 计算像素差异比例
        diff = cv2.absdiff(self._last_frame, frame)
        if self.use_gray:
            ratio = float(cv2.countNonZero(diff)) / float(diff.size)
        else:
            ratio = float(cv2.countNonZero(cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY))) / float(diff.size)

        self._last_frame = frame

        if ratio >= self.threshold:
            now = time.time()
            if now - self._last_trigger_time >= self.cooldown:
                self._last_trigger_time = now
                self._changed_count += 1
                logger.info(f"检测到屏幕变化: {ratio:.2%} (累计 {self._changed_count} 次)")
                if self._callback:
                    try:
                        self._callback(ratio, img)
                    except Exception as e:
                        logger.error(f"变化回调执行失败: {e}")


def watch_until_changed(
    interval: float = 2.0,
    threshold: float = 0.02,
    timeout: Optional[float] = None,
    region: Optional[Tuple[int, int, int, int]] = None,
) -> Tuple[float, object]:
    """
    便捷函数：阻塞等待屏幕发生明显变化。

    Returns:
        (diff_ratio, pil_image)；timeout 到期未变化返回 (0.0, None)
    """
    result = {"ratio": 0.0, "img": None}
    watcher = ScreenChangeWatcher(interval=interval, threshold=threshold, region=region, cooldown=0)
    watcher.on_change(lambda r, im: result.update(ratio=r, img=im))
    start = time.time()
    while result["img"] is None:
        watcher._tick()
        if timeout is not None and time.time() - start > timeout:
            return (0.0, None)
        time.sleep(interval)
    return (result["ratio"], result["img"])
