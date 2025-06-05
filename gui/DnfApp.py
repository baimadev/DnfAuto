# DnfApp.py
import tkinter as tk
from DnfGui import DnfGUI
import threading
import pyautogui
import numpy as np
import time
import os
import sys
from ctypes import windll
from ultralytics import YOLO
import random
from PIL import ImageGrab
import cv2
import win32gui


# 修复 DPI 缩放问题
windll.user32.SetProcessDPIAware()

if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.dirname(__file__)
model_path = os.path.join(base_path, '../runs', 'detect', 'train', 'weights', 'best.pt')
model = YOLO(model_path)

class TkinterOverlay:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()  # 隐藏主窗口

        # 创建透明顶层窗口
        self.overlay = tk.Toplevel()
        self.overlay.overrideredirect(True)
        self.overlay.attributes("-topmost", True)
        self.overlay.attributes("-transparentcolor", "black")
        self.overlay.configure(bg='black')

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.overlay.geometry(f"{screen_width}x{screen_height}+0+0")

        # 创建 Canvas 用于绘图
        self.canvas = tk.Canvas(self.overlay, width=screen_width, height=screen_height,
                                bg='black', highlightthickness=0)
        self.canvas.pack()
        self.overlay.update()
        self.root.destroy()  # 关闭默认主窗口

    def clear_overlay(self):
        self.canvas.delete("all")
        self.overlay.update()

    def update_overlay(self, results):
        self.canvas.delete("all")  # 清空上一帧

        try:
            detections = results[0].boxes.data.cpu().numpy()
            if len(detections) > 0:
                for det in detections:
                    if det.shape[0] == 6:
                        x1, y1, x2, y2, conf, cls_id = det
                    elif det.shape[0] == 7:
                        _, x1, y1, x2, y2, conf, cls_id = det
                    else:
                        continue

                    label = model.names[int(cls_id)]
                    text = f"{label} {conf:.2f}"

                    # 绘制绿色矩形框
                    self.canvas.create_rectangle(x1, y1, x2, y2, outline="#00FF00", width=2)

                    # 标签背景
                    text_width = len(text) * 8
                    text_height = 16
                    self.canvas.create_rectangle(x1, y1 - text_height, x1 + text_width, y1,
                                                fill="#00FF00", outline="")

                    # 居中显示文本
                    self.canvas.create_text(x1 + 4, y1 - text_height + 2, text=text,
                                            fill="white", anchor="nw", font=("Arial", 10))

        except Exception as e:
            print(f"绘制错误: {e}")

        self.overlay.update()


# 主程序逻辑
class DnfApp:
    def __init__(self, root):
        self.root = root
        self.running = False
        self.is_stopped = False  # 新增状态标志

        # 初始化 GUI
        self.gui = DnfGUI(root, self.start_detection, self.stop_detection)

        # 初始化 Tkinter 覆盖层
        self.overlay = TkinterOverlay()

    def start_detection(self):
        self.running = True
        self.is_stopped = False
        self.gui.update_buttons(True)
        threading.Thread(target=self.detection_loop, daemon=True).start()

    def stop_detection(self):
        self.running = False
        self.is_stopped = True  # 设置停止标志
        self.gui.update_buttons(False)
        self.overlay.clear_overlay()  # 立即清空画布

    def detection_loop(self):
        try:
            while self.running:
                start_time = time.time()
                screenshot = ImageGrab.grab()
                screen_np = np.array(screenshot)
                screen_np = cv2.cvtColor(screen_np, cv2.COLOR_RGB2BGR)
                results = model.predict(screen_np, verbose=False)

                if not self.is_stopped:  # 只有在非停止状态下才更新 overlay
                    self.overlay.update_overlay(results)

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
                    self.press_x_after = random.uniform(3, 5)
                    pyautogui.doubleClick('right')
                    pyautogui.keyDown('right')
                    print(f"双击右方向键，并开始长按。将在 {self.press_x_after:.2f} 秒后按住 X 键")
                else:
                    elapsed = time.time() - self.detection_start_time
                    if elapsed < self.press_x_after:
                        print(f"持续按住右方向键（{elapsed:.2f}/{self.press_x_after:.2f}秒）")
                    else:
                        pyautogui.keyDown('x')
                        print("已按住 X 键并继续按住右方向键")
            else:
                if hasattr(self, 'detection_start_time'):
                    delattr(self, 'detection_start_time')
                if getattr(self, 'detected_last_frame', False):
                    pyautogui.keyUp('right')
                    pyautogui.keyUp('x')
                    print("释放右方向键和 X 键")
                self.detected_last_frame = False

                if self.is_stopped:  # 如果已经停止，则不再绘制
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


# 启动 GUI
if __name__ == "__main__":
    root = tk.Tk()
    root.attributes('-topmost', 1)
    root.update()
    root.focus_force()
    app = DnfApp(root)
    root.mainloop()
