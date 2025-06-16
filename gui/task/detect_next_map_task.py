import random
import time
from time import sleep

import cv2
import numpy as np
import win32gui
from PIL import ImageGrab

from gui.task.task_base import Task
from gui.utils.tkinter_overlay import TkinterOverlay

# detect by yolo
class DetextNextMapTask(Task):
    def __init__(self, gui, model):
        super().__init__("detect_next_map", gui)
        self.model = model
        self.overlay = TkinterOverlay()

    def execute(self):
        self.detection_loop()

    def detection_loop(self):
        try:
            while not self.is_stopped():
                start_time = time.time()
                screenshot = ImageGrab.grab()
                screen_np = np.array(screenshot)
                screen_np = cv2.cvtColor(screen_np, cv2.COLOR_RGB2BGR)
                results = self.model.predict(screen_np, verbose=False)

                if not self.is_stopped():
                    self.overlay.update_overlay(results, self.model)

                elapsed = time.time() - start_time
                if elapsed < 0.1:
                    time.sleep(0.1 - elapsed)

                self.handle_detection(results)

        except Exception as e:
            self.gui.log(f"发生错误: {str(e)}")

    def handle_detection(self, results):
        self.is_dnf_foreground()
        try:
            detections = results[0].boxes.data.cpu().numpy()
            if len(detections) > 0:
                if not hasattr(self, 'detection_start_time'):
                    self.detection_start_time = time.time()
                    self.press_x_after = random.uniform(1, 2)
                    self.gui.log("检测到进入下个地图标志，聚物拾取。")
                    self.gui.log("按下TAB，随机延时，开始按住X键")
                else:
                    elapsed = time.time() - self.detection_start_time
                    if elapsed < self.press_x_after:
                        self.gui.log(f"继续按住X键（{elapsed:.2f}/{self.press_x_after:.2f}秒）")
                    else:
                        self.gui.log("松开X键 随机延时 按下F10 sleep")
                        delattr(self, 'detection_start_time')
                        sleep(random.uniform(3, 5))
            else:
                if self.is_stopped():  # 如果已经停止，则不再绘制
                    self.overlay.clear_overlay()

        except Exception as e:
            print(f"处理检测结果出错: {e}")

    def is_dnf_foreground(self):
        """
        判断 DNF 是否为当前焦点窗口
        """
        hwnd = win32gui.GetForegroundWindow()
        title = win32gui.GetWindowText(hwnd)
        if "地下城与勇士" in title or "DNF" in title:
            return True
        return False

