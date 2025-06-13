# dnf_app.py

import tkinter as tk
from dnf_gui import DnfGUI
import os
import sys
from ctypes import windll
from ultralytics import YOLO

from gui.task.task_manager import TaskManager
from gui.task.detect_next_map_task import DetextNextMapTask
from gui.task.detect_challenge_again import DetextChallengeAgain
from gui.utils.tkinter_overlay import TkinterOverlay



# 主程序逻辑
class DnfApp:
    def __init__(self, root):
        # 修复 DPI 缩放问题
        windll.user32.SetProcessDPIAware()

        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(__file__)
        model_path = os.path.join(base_path, '../runs', 'detect', 'train', 'weights', 'best.pt')
        self.model = YOLO(model_path)

        self.root = root
        # 初始化 GUI
        self.gui = DnfGUI(root, self.start_detection, self.stop_detection)
        # 初始化 Tkinter 覆盖层
        self.overlay = TkinterOverlay()
        # 初始化任务管理器
        self.manager = TaskManager()
        #self.manager.register_task(DetextNextMapTask(self.gui, self.model))
        self.manager.register_task(DetextChallengeAgain(self.gui))

    def start_detection(self):
        self.manager.start_all()
        self.gui.update_buttons(True)

    def stop_detection(self):
        self.manager.stop_all()
        self.gui.update_buttons(False)

# 启动 GUI
if __name__ == "__main__":
    root = tk.Tk()
    root.attributes('-topmost', 1)
    root.update()
    root.focus_force()
    app = DnfApp(root)
    root.mainloop()
