import random
import time
from time import sleep

import numpy as np
import win32gui
from PIL import ImageGrab

from gui.task.task_base import Task
from ocr.ocr_util import OcrUtil


class DetextChallengeAgain(Task):
    def __init__(self, gui):
        super().__init__("detect_challenge_again", gui)
        self.ocr = OcrUtil()

    def execute(self):
        self.detection_loop()

    def detection_loop(self):
        try:
            while not self.is_stopped():
                start_time = time.time()
                screenshot = ImageGrab.grab()
                image_np = np.array(screenshot)  # 得到 RGB 格式数组
                self.gui.log(f"checkTextExist")
                box = self.ocr.checkTextExist("修理装备", image_np)
                self.gui.log(f"checkEnd")
                elapsed = time.time() - start_time
                if elapsed < 0.1:
                    time.sleep(0.1 - elapsed)

                self.handle_detection(box)

        except Exception as e:
            self.gui.log(f"发生错误: {str(e)}")

    def handle_detection(self, box):
        self.is_dnf_foreground()
        try:
            if box is not None:
                self.gui.log(f"detect target {box}")
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
                self.gui.log("nothing found")

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

