# dnf_app.py
import threading
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
        windll.user32.SetProcessDPIAware()
        self.model_ready = False
        threading.Thread(target=self._load_model, daemon=True).start()

        self.root = root
        # 初始化 GUI
        self.gui = DnfGUI(root, self.start_detection, self.stop_detection)
        # 初始化 Tkinter 覆盖层
        self.overlay = TkinterOverlay()
        # 初始化任务管理器
        self.manager = TaskManager()
        #self.manager.register_task(DetextNextMapTask(self.gui, self.model))
        #self.manager.register_task(DetextChallengeAgain(self.gui))

    def _load_model(self):
        try:
            if getattr(sys, 'frozen', False):
                base_path = sys._MEIPASS
            else:
                base_path = os.path.dirname(__file__)
            model_path = os.path.join(base_path, '../runs', 'detect', 'train', 'weights', 'best.pt')
            self.model = YOLO(model_path)
            self.model_ready = True
            self.gui.log("YOLO模型加载完成")
        except Exception as e:
            self.gui.log(f"模型加载失败: {str(e)}")

    def start_detection(self):
        self.manager.start_all()
        self.gui.update_buttons(True)

    def stop_detection(self):
        self.manager.stop_all()
        self.gui.update_buttons(False)

# 启动 GUI
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # 先隐藏主窗口
    # 显示加载中提示
    splash = tk.Toplevel()
    tk.Label(splash, text="初始化中...").pack()
    root.update()
    # 异步初始化
    def init_app():
        app = DnfApp(root)
        splash.destroy()
        root.deiconify()  # 显示主窗口
    threading.Thread(target=init_app, daemon=True).start()
    root.mainloop()