import threading
import logging
from abc import ABC, abstractmethod

import win32gui

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class Task(ABC):
    """任务基类，所有具体任务需要继承此类"""

    def __init__(self, name ,gui):
        self.name = name
        self.gui = gui
        self.logger = logging.getLogger(f"Task.{name}")
        self._stop_event = threading.Event()

    @abstractmethod
    def execute(self):
        """执行任务的具体逻辑，子类必须实现"""
        pass

    def stop(self):
        """停止任务"""
        self._stop_event.set()
        self.logger.info("收到停止信号")

    def is_stopped(self):
        """检查任务是否被要求停止"""
        return self._stop_event.is_set()

    def run(self):
        """任务执行入口，封装执行逻辑"""
        try:
            self.logger.info("任务开始执行")
            self.execute()
            self.logger.info("任务执行完成")
        except Exception as e:
            self.logger.error(f"任务执行出错: {str(e)}", exc_info=True)
        finally:
            self._stop_event.clear()
    def is_dnf_foreground(self):
        """
        判断 DNF 是否为当前焦点窗口
        """
        hwnd = win32gui.GetForegroundWindow()
        title = win32gui.GetWindowText(hwnd)
        if "地下城与勇士" in title or "DNF" in title:
            return True
        return False
