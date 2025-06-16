import time

import numpy as np
from PIL import ImageGrab

from gui.keybord.keyboard_util import WyhkmCOM
from gui.task.task_base import Task
from ocr.ocr_util import OcrUtil

# detect by OCR
class DetextChallengeAgain(Task):

    # detect interval seconds
    INTERVAL = 4
    # detect target
    TARGET = "修理装备"

    last_detect_time = time.time()
    def __init__(self, gui):
        super().__init__("detect_challenge_again", gui)
        self.keyboard = WyhkmCOM()
        self.ocr = OcrUtil()
        self.is_detected_target = False

    def execute(self):
        self.detection_loop()

    def detection_loop(self):
        try:
            while not self.is_stopped():
                elapsed = time.time() - self.last_detect_time
                if elapsed < self.INTERVAL:
                    time.sleep(self.INTERVAL - elapsed)
                self.last_detect_time = time.time()
                print("start detect challenge again.")
                screenshot = ImageGrab.grab()
                image_np = np.array(screenshot)
                box = self.ocr.checkTextExist(self.TARGET, image_np)
                self.handle_detection(box)

        except Exception as e:
            self.gui.log(f"发生错误: {str(e)}")

    def handle_detection(self, box):
        self.is_dnf_foreground()
        try:
            if box is not None:
                self.is_detected_target = True
                self.gui.log(f"detect target {box}")
                self.gui.log("检测到进入下个地图标志，聚物拾取。")
                self.keyboard.run("Right",3500)
                self.keyboard.key_press("Tab")
                self.keyboard.key_long_press("X", 3000)

            else:
                self.gui.log("nothing found")
                if self.is_detected_target:
                    self.is_detected_target = False
                    self.keyboard.release_keyboard()

        except Exception as e:
            print(f"处理检测结果出错: {e}")