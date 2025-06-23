# yolo_model_util.py
from enum import Enum
from time import sleep

import cv2
import mss
import numpy as np
from ultralytics import YOLO
import threading

from gui.utils.scene_navigator import resource_path

region = {'left': 0, 'top': 0, 'width': 1700, 'height': 956}


class DetectionTarget(Enum):
    ROLE = "role"
    FORWARD = "forward"
    SFJX = "sfjx"  # 是否继续
    MONSTER = "monster"
    SMSD = "smsd"  # 神秘商店
    CAN_HEN = "can_hen"  # 妖气残痕


class YoloModelUtil:
    _instance_lock = threading.Lock()
    _model = None
    _is_loading = False
    _load_event = threading.Event()

    def __new__(cls):
        if cls._model is None:
            with cls._instance_lock:
                if cls._model is None:
                    cls._model = super(YoloModelUtil, cls).__new__(cls)
                    cls._model._load_model_in_thread()
        cls._model._load_event.wait()
        return cls._model

    def _load_model_in_thread(self):
        self._is_loading = True
        thread = threading.Thread(target=self._load_model_async)
        thread.daemon = True
        thread.start()

    def _load_model_async(self):
        try:
            self.new_model = YOLO(resource_path('../models/role.pt'))
            self.old_model = YOLO(resource_path('../models/best15.pt'))
            print("yolo模型加载完成")
        except Exception as e:
            print(f"模型加载失败: {e}")
        finally:
            self._is_loading = False
            self._load_event.set()

    def capture_screen(self, is_capture_full=False):
        with mss.mss() as sct:
            if is_capture_full:
                screenshot = sct.grab(sct.monitors[1])
            else:
                screenshot = sct.grab(region)
            return np.array(screenshot)[:, :, :3]

    def predict(self, image, is_use_new_model=True):
        if is_use_new_model:
            results = self.new_model.predict(image)
        else:
            results = self.old_model.predict(image)
        return results

    def check_exist(self, detection_target: DetectionTarget, image=None, is_use_new_model=True, conf=0.6):
        if image is None:
            image = self.capture_screen()
        results = self.predict(image, is_use_new_model)
        for result in results:
            for box in result.boxes:
                confidence = box.conf.item()
                if confidence < conf:
                    continue
                cls_name = result.names[int(box.cls)]
                if cls_name == detection_target.value:
                    return True
        return False

    def get_positions(self, detection_target: DetectionTarget, image = None, is_use_new_model=True, conf=0.6):
        if image is None:
            image = self.capture_screen()
        results = self.predict(image, is_use_new_model)
        for result in results:
            for box in result.boxes:
                cls = int(box.cls)
                label = result.names[cls]
                confidence = box.conf.item()
                if confidence < conf:
                    continue
                if label == detection_target.value:
                    x1, y1, x2, y2 = map(float, box.xyxy[0])
                    cx = (x1 + x2) / 2
                    cy = (y1 + y2) / 2
                    print(f"检测到{detection_target.value} 位置: ({cx}, {cy})")
                    return cx, cy
        return None, None


if __name__ == "__main__":
    yolo_util = YoloModelUtil()
    sleep(2)
    frame_rgb = yolo_util.capture_screen(True)
    yolo_util.get_positions(frame_rgb, DetectionTarget.ROLE)
