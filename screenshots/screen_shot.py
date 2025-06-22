import os
import time
import tkinter as tk
from datetime import datetime
from tkinter import messagebox
import mss
import mss.tools
from PIL import Image, ImageTk
import keyboard
import threading
import pyperclip


class ScreenshotTool:
    def __init__(self):
        # 配置
        self.OUTPUT_DIR = os.path.join(os.getcwd(), "screenshots")
        os.makedirs(self.OUTPUT_DIR, exist_ok=True)

        # 截图状态
        self.is_capturing = False
        self.start_pos = None
        self.selection_window = None
        self.root = None
        self.capture_window = None

        # 注册全局快捷键
        keyboard.add_hotkey('ctrl+alt+s', self.start_capture)
        keyboard.add_hotkey('ctrl+alt+e', self.cancel_capture)

        print("截图工具已就绪，按 Ctrl+Alt+S 开始截图，按 Ctrl+Alt+E 取消")

        # 创建主窗口（在主线程）
        self.root = tk.Tk()
        self.root.withdraw()  # 隐藏主窗口

        # 保持主线程运行
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.cleanup()

    def start_capture(self):
        """安全启动截图流程（在主线程调用）"""
        if self.is_capturing:
            return

        self.is_capturing = True
        print("截图模式激活中...")

        # 在主线程创建截图窗口
        self._init_capture_window()

    def _init_capture_window(self):
        """初始化截图窗口（在主线程运行）"""
        # 创建截图窗口
        self.capture_window = tk.Toplevel(self.root)
        self.capture_window.attributes("-alpha", 0.01)
        self.capture_window.attributes("-fullscreen", True)
        self.capture_window.attributes("-topmost", True)
        self.capture_window.overrideredirect(True)

        # 绑定鼠标事件和ESC键
        self.capture_window.bind("<ButtonPress-1>", self.on_mouse_down)
        self.capture_window.bind("<B1-Motion>", self.on_mouse_drag)
        self.capture_window.bind("<ButtonRelease-1>", self.on_mouse_up)
        self.capture_window.bind("<Escape>", lambda e: self.cancel_capture())

        # 显示操作提示
        self.show_tooltip("拖动鼠标选择区域\nCtrl+Alt+E 或 ESC 取消 | 松开鼠标确认", 3000)

    def on_mouse_down(self, event):
        """鼠标按下事件（记录起点）"""
        self.start_pos = (event.x_root, event.y_root)
        self.selection_window = None

        # 创建半透明选区窗口
        self.selection_window = tk.Toplevel(self.root)
        self.selection_window.attributes("-alpha", 0.3)
        self.selection_window.attributes("-fullscreen", True)
        self.selection_window.overrideredirect(True)

        self.canvas = tk.Canvas(
            self.selection_window,
            cursor="cross",
            bg='black', highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

    def on_mouse_drag(self, event):
        """实时更新选区"""
        if not self.start_pos:
            return

        x1, y1 = self.start_pos
        x2, y2 = event.x_root, event.y_root

        self.canvas.delete("all")
        self.canvas.create_rectangle(
            x1, y1, x2, y2,
            outline="red", width=2,
            fill="", dash=(4, 4)  # 虚线边框
        )

    def on_mouse_up(self, event):
        """完成选区"""
        if not self.start_pos:
            self.cancel_capture()
            return

        x1, y1 = self.start_pos
        x2, y2 = event.x_root, event.y_root
        bbox = (
            min(x1, x2), min(y1, y2),
            max(x1, x2), max(y1, y2)
        )

        # 最小尺寸检查
        if (bbox[2] - bbox[0]) < 10 or (bbox[3] - bbox[1]) < 10:
            self.show_tooltip("选区太小（至少10x10像素）", 2000)
            self.cancel_capture()
            return

        # 保存选区信息
        self.current_bbox = bbox

        # 延迟处理，确保UI响应
        self.root.after(100, self._process_screenshot, bbox)

    def _process_screenshot(self, bbox):
        """处理截图（在主线程）"""
        # 清理选区窗口
        self.cancel_capture()

        # 在子线程中执行耗时的截图操作
        process_thread = threading.Thread(
            target=self._capture_and_preview,
            args=(bbox,),
            daemon=True
        )
        process_thread.start()

    def _capture_and_preview(self, bbox):
        """截图并显示预览（在子线程）"""
        try:
            with mss.mss() as sct:
                monitor = {
                    "left": bbox[0],
                    "top": bbox[1],
                    "width": bbox[2] - bbox[0],
                    "height": bbox[3] - bbox[1]
                }
                screenshot = sct.grab(monitor)
                img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)

                # 在主线程显示预览
                self.root.after(0, lambda: self.show_preview(img))

        except Exception as e:
            # 在主线程显示错误
            self.root.after(0, lambda: messagebox.showerror("错误", f"截图失败: {str(e)}"))

    def show_preview(self, image):
        """显示预览窗口（在主线程）"""
        try:
            preview = tk.Toplevel(self.root)
            preview.title("截图预览")

            # 显示图像
            img_tk = ImageTk.PhotoImage(image)
            label = tk.Label(preview, image=img_tk)
            label.image = img_tk  # 保持引用
            label.pack(padx=10, pady=10)

            # 按钮区域
            btn_frame = tk.Frame(preview)
            btn_frame.pack(pady=5)

            tk.Button(
                btn_frame, text="保存 (Enter)",
                command=lambda: self.save_image(image, preview),
                width=12, bg="#4CAF50", fg="white"
            ).pack(side=tk.LEFT, padx=5)

            tk.Button(
                btn_frame, text="取消 (ESC)",
                command=preview.destroy,
                width=12, bg="#f44336", fg="white"
            ).pack(side=tk.RIGHT, padx=5)

            # 绑定快捷键
            preview.bind("<Return>", lambda e: self.save_image(image, preview))
            preview.bind("<Escape>", lambda e: preview.destroy())

            self.center_window(preview)
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("错误", f"预览失败: {str(e)}"))

    def save_image(self, image, window):
        """保存截图（在主线程）"""
        filename = datetime.now().strftime("screenshot_%Y%m%d_%H%M%S.png")
        save_path = os.path.join(self.OUTPUT_DIR, filename)

        try:
            image.save(save_path, "PNG", compress_level=3)
            window.destroy()

            # 显示保存通知
            self.show_tooltip(f"已保存到: {filename}", 2000)

            # 复制文件路径
            pyperclip.copy(save_path)
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("错误", f"保存失败: {str(e)}"))

    def cancel_capture(self):
        """取消截图流程"""
        if self.is_capturing:
            self.cleanup()
            print("截图已取消")

    def cleanup(self):
        """清理所有资源"""
        try:
            self.is_capturing = False
            self.start_pos = None

            # 销毁截图窗口
            if self.capture_window and self.capture_window.winfo_exists():
                self.capture_window.destroy()
                self.capture_window = None

            # 销毁选区窗口
            if self.selection_window and self.selection_window.winfo_exists():
                self.selection_window.destroy()
                self.selection_window = None

            # 销毁所有临时窗口
            for window in self.root.winfo_children():
                if isinstance(window, tk.Toplevel):
                    window.destroy()

        except Exception as e:
            print(f"清理错误: {e}")

    def show_tooltip(self, text, duration):
        """显示临时提示（在主线程）"""
        try:
            tip = tk.Toplevel(self.root)
            tip.attributes("-topmost", True)
            tip.overrideredirect(True)

            label = tk.Label(
                tip, text=text,
                bg="yellow", fg="black", padx=10, pady=5,
                font=("Arial", 10)
            )
            label.pack()

            self.center_window(tip)
            tip.after(duration, tip.destroy)
        except Exception as e:
            print(f"提示错误: {e}")

    @staticmethod
    def center_window(window):
        """窗口居中"""
        try:
            window.update_idletasks()
            width = window.winfo_width()
            height = window.winfo_height()
            x = (window.winfo_screenwidth() // 2) - (width // 2)
            y = (window.winfo_screenheight() // 2) - (height // 2)
            window.geometry(f'+{x}+{y}')
        except Exception as e:
            print(f"居中错误: {e}")


if __name__ == "__main__":
    tool = ScreenshotTool()