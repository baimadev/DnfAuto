import tkinter as tk
from tkinter import messagebox
import threading
import cv2
import numpy as np
import pyautogui
from PIL import ImageGrab, ImageTk
import win32gui, win32con, win32api
import time
import os
import sys
from ctypes import windll
from ultralytics import YOLO
import random


# 修复 DPI 缩放问题
windll.user32.SetProcessDPIAware()

# 获取当前路径
if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.dirname(__file__)

model_path = os.path.join(base_path, 'runs', 'detect', 'train', 'weights', 'best.pt')
model = YOLO(model_path)

# 透明覆盖层类（保持不变）
class TransparentOverlay:
    def __init__(self):xx
        self.screen_width, self.screen_height = pyautogui.size()
        self.window_name = "YOLOv11 Detection Overlay"
        self.detected_last_frame = False
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        cv2.setWindowProperty(self.window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        cv2.resizeWindow(self.window_name, self.screen_width, self.screen_height)
        hwnd = win32gui.FindWindow(None, self.window_name)
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE,
                               win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT | win32con.WS_EX_TOPMOST | win32con.WS_EX_NOACTIVATE)
        win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(0, 0, 0), 0, win32con.LWA_COLORKEY)
        win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, self.screen_width, self.screen_height, win32con.SWP_SHOWWINDOW)
        self.canvas = np.zeros((self.screen_height, self.screen_width, 3), dtype=np.uint8)
        cv2.imshow(self.window_name, self.canvas)
        cv2.waitKey(1)

    def update_overlay(self, results):
        new_canvas = np.zeros((self.screen_height, self.screen_width, 3), dtype=np.uint8)
        detection_active = False

        try:
            detections = results[0].boxes.data.cpu().numpy()
            if len(detections) > 0:  # 检测到目标
                detection_active = True
                self.detected_last_frame = True
                for det in detections:
                    if det.shape[0] == 6:
                        x1, y1, x2, y2, conf, cls_id = det
                    elif det.shape[0] == 7:
                        _, x1, y1, x2, y2, conf, cls_id = det
                    else:
                        continue

                    cls_name = model.names[int(cls_id)]
                    label = f"{cls_name} {conf:.2f}"
                    cv2.rectangle(new_canvas, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                    cv2.rectangle(new_canvas, (int(x1), int(y1) - 20), (int(x1) + len(label) * 10, int(y1)),
                                  (0, 255, 0), -1)
                    cv2.putText(new_canvas, label, (int(x1) + 5, int(y1) - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                                (255, 255, 255), 2)

                # 第一次进入检测状态时触发双击
                if not hasattr(self, 'detection_start_time'):
                    self.detection_start_time = time.time()
                    self.press_x_after = random.uniform(3, 5)  # 随机设定 3~5 秒之间按 X
                    pyautogui.doubleClick('right')  # 双击右方向键
                    pyautogui.keyDown('right')  # 开始长按右方向键
                    print(f"双击右方向键，并开始长按。将在 {self.press_x_after:.2f} 秒后按住 X 键")

                else:
                    elapsed = time.time() - self.detection_start_time
                    pyautogui.keyDown('right')  # 继续按住右方向键

                    if elapsed < self.press_x_after:
                        print(f"持续按住右方向键（{elapsed:.2f}/{self.press_x_after:.2f}秒）")
                    else:
                        pyautogui.keyDown('x')  # 按住 X 键
                        print("已按住 X 键并继续按住右方向键")

            else:
                # 没有检测到目标时释放按键
                if hasattr(self, 'detection_start_time'):
                    delattr(self, 'detection_start_time')
                if self.detected_last_frame:
                    pyautogui.keyUp('right')
                    pyautogui.keyUp('x')
                    print("释放右方向键和 X 键")
                    self.detected_last_frame = False

        except Exception as e:
            print(f"绘制错误: {e}")

        cv2.imshow(self.window_name, new_canvas)
        cv2.waitKey(1)


# 主程序逻辑
class DnfApp:
    def __init__(self, root):
        self.root = root
        self.running = False
        self.overlay = TransparentOverlay()

        # GUI 设置
        self.root.title("DNF 游戏辅助检测器")
        self.root.geometry("400x300")
        self.root.resizable(False, False)

        self.label = tk.Label(root, text="DNF 游戏目标检测器", font=("Arial", 16))
        self.label.pack(pady=20)

        self.start_button = tk.Button(root, text="启动检测", width=20, command=self.start_detection)
        self.start_button.pack(pady=10)

        self.stop_button = tk.Button(root, text="停止检测", width=20, command=self.stop_detection, state=tk.DISABLED)
        self.stop_button.pack(pady=10)

        self.log_text = tk.Text(root, height=10, width=50, state='disabled')
        self.log_text.pack(pady=10)

    def log(self, message):
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.config(state='disabled')
        self.log_text.see(tk.END)

    def detection_loop(self):
        self.running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.log("实时检测已启动...")

        detection_interval = 0.1
        try:
            while self.running:
                start_time = time.time()
                screenshot = ImageGrab.grab()
                screen_np = np.array(screenshot)
                screen_np = cv2.cvtColor(screen_np, cv2.COLOR_RGB2BGR)
                results = model.predict(screen_np, verbose=False)
                self.overlay.update_overlay(results)

                elapsed = time.time() - start_time
                if elapsed < detection_interval:
                    time.sleep(detection_interval - elapsed)
        except Exception as e:
            self.log(f"发生错误: {str(e)}")
        finally:
            self.log("检测已停止。")
            self.running = False
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)

    def start_detection(self):
        threading.Thread(target=self.detection_loop, daemon=True).start()

    def stop_detection(self):
        self.running = False
        self.stop_button.config(state=tk.DISABLED)


# 启动 GUI
if __name__ == "__main__":
    root = tk.Tk()
    app = DnfApp(root)
    root.mainloop()
