from time import sleep

import cv2
import mss
import numpy as np
from ultralytics import YOLO

def detect_fix():
    yolo = YOLO('runs/detect/train5/weights/best.pt')
    # yolo = YOLO('gui/models/role.pt')
    source = 'train/images/screenshot_20250622_160431.png' #修改为自己的图片路径及文件名
    forward = yolo.predict(source, save=True)
    for result in forward:
        for box in result.boxes:
            cls_name = result.names[int(box.cls)]
            conf = box.conf.item()
            print(f"yolo test {cls_name} {conf}")


region = {'left': 0, 'top': 0, 'width': 1700, 'height': 956}
def detect_forward():
    yolo = YOLO('runs/detect/train/weights/best.pt')
    #yolo = YOLO('gui/models/role.pt')
    sleep(2)
    with mss.mss() as sct:
        screenshot = sct.grab(region)
        frame_rgb = cv2.cvtColor(np.array(screenshot), cv2.COLOR_BGRA2RGB)
        forward = yolo.predict(frame_rgb,save = True)
        for result in forward:
            for box in result.boxes:
                cls_name = result.names[int(box.cls)]
                conf = box.conf.item()
                print(f"yolo test {cls_name} {conf}")

if __name__ == "__main__":
    detect_forward()
    #detect_fix()