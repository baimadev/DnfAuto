import os
import sys
import subprocess
import time
import datetime
import pyautogui
import tkinter as tk
from tkinter import messagebox
from threading import Thread, Event
from queue import Queue
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# 尝试导入pynput，如果失败则自动安装
try:
    from pynput import keyboard
except ImportError:
    logging.info("缺少pynput库，正在尝试安装...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pynput"])
        from pynput import keyboard

        logging.info("pynput安装成功")
    except Exception as e:
        logging.error(f"安装失败: {e}")
        print("请手动运行: pip install pynput")
        sys.exit(1)


class ScreenshotTool:
    def __init__(self):
        logging.info("初始化截图工具")

        # 设置截图保存目录为当前目录下的images文件夹
        self.save_dir = os.path.join(os.getcwd(), "images")
        # 确保保存目录存在
        os.makedirs(self.save_dir, exist_ok=True)
        logging.info(f"截图将保存到: {self.save_dir}")

        # 程序运行标志
        self.running = True

        # 创建主窗口，但先不显示
        self.root = tk.Tk()
        self.root.title("截图工具")
        self.root.geometry("300x100")
        self.root.resizable(False, False)
        self.root.withdraw()  # 隐藏窗口

        # 用于线程间通信的队列
        self.queue = Queue()

        # 截图操作锁，防止并发操作
        self.screenshot_lock = Event()
        self.screenshot_lock.set()  # 初始状态为可操作

        # 键盘监听线程
        self.keyboard_thread = Thread(target=self.start_keyboard_listener, daemon=True)
        self.keyboard_thread.start()

        # 定期检查队列中的消息
        self.check_queue()

        # 绑定关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        logging.info("截图工具初始化完成")

    def start_keyboard_listener(self):
        """启动键盘监听线程"""

        def on_press(key):
            try:
                # 检查是否按下了Ctrl+A
                if hasattr(key, 'char') and key.char == '\x01' and self.running:  # Ctrl+A的ASCII码是1
                    logging.info("Ctrl+A被按下，请求截图")
                    # 检查是否可以进行截图操作
                    if self.screenshot_lock.is_set():
                        self.screenshot_lock.clear()  # 锁定截图操作
                        self.queue.put("take_screenshot")
                    else:
                        logging.info("正在进行截图操作，请稍候...")
            except Exception as e:
                logging.error(f"键盘事件处理错误: {e}")

        with keyboard.Listener(on_press=on_press) as listener:
            listener.join()

    def check_queue(self):
        """检查队列中的消息"""
        while not self.queue.empty():
            message = self.queue.get()
            if message == "take_screenshot":
                self.take_screenshot()

        if self.running:
            self.root.after(100, self.check_queue)  # 每100毫秒检查一次

    def take_screenshot(self):
        """执行区域截图并自动保存"""
        try:
            # 隐藏主窗口
            self.root.withdraw()
            time.sleep(0.1)  # 确保窗口完全隐藏

            # 创建截图选择器
            region_selector = RegionSelector(self)
            screenshot = region_selector.select_region()

            if screenshot:
                # 生成文件名
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
                filename = f"screenshot_{timestamp}.png"
                file_path = os.path.join(self.save_dir, filename)

                # 保存截图
                screenshot.save(file_path)
                logging.info(f"截图已自动保存至: {file_path}")

                # 显示保存成功的提示
                self.show_notification(f"截图已保存: {filename}")
        except Exception as e:
            logging.error(f"截图过程中出错: {e}")
            messagebox.showerror("错误", f"截图过程中出错: {e}")
        finally:
            self.screenshot_lock.set()  # 释放截图锁
            self.root.deiconify()

    def show_notification(self, message):
        """显示保存成功的通知"""
        notification = tk.Toplevel(self.root)
        notification.title("截图保存成功")
        notification.geometry("300x80")
        notification.resizable(False, False)

        # 居中显示
        notification.update_idletasks()
        width = notification.winfo_width()
        height = notification.winfo_height()
        x = (notification.winfo_screenwidth() // 2) - (width // 2)
        y = (notification.winfo_screenheight() // 2) - (height // 2)
        notification.geometry(f'{width}x{height}+{x}+{y}')

        tk.Label(notification, text=message).pack(pady=20)
        notification.after(2000, notification.destroy)  # 2秒后自动关闭

    def on_close(self):
        """处理窗口关闭事件"""
        self.running = False
        self.root.after(200, self.root.destroy)

    def run(self):
        """运行截图工具"""
        logging.info("截图工具已启动，按Ctrl+A进行区域截图")
        self.root.mainloop()


class RegionSelector:
    """区域选择器类，用于选择屏幕上的特定区域"""

    def __init__(self, parent):
        self.parent = parent
        self.root = tk.Toplevel()
        self.root.attributes('-fullscreen', True)
        self.root.attributes('-alpha', 0.3)  # 半透明
        self.root.configure(bg='black')

        # 记录鼠标位置
        self.start_x = None
        self.start_y = None
        self.end_x = None
        self.end_y = None

        # 创建画布
        self.canvas = tk.Canvas(self.root, bg='black', highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # 绑定事件
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.root.bind("<Escape>", self.on_cancel)

        # 选择框
        self.selection_rect = None

        # 截图结果
        self.screenshot = None

    def on_press(self, event):
        """鼠标按下事件处理"""
        self.start_x = event.x
        self.start_y = event.y

        # 创建选择框
        if self.selection_rect:
            self.canvas.delete(self.selection_rect)
        self.selection_rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y,
            outline='red', width=2
        )

    def on_drag(self, event):
        """鼠标拖动事件处理"""
        self.end_x = event.x
        self.end_y = event.y

        # 更新选择框
        if self.selection_rect:
            self.canvas.coords(
                self.selection_rect,
                self.start_x, self.start_y,
                self.end_x, self.end_y
            )

    def on_release(self, event):
        """鼠标释放事件处理"""
        self.end_x = event.x
        self.end_y = event.y

        # 确保起点和终点正确
        x1, y1 = min(self.start_x, self.end_x), min(self.start_y, self.end_y)
        x2, y2 = max(self.start_x, self.end_x), max(self.start_y, self.end_y)

        # 关闭选择窗口
        self.root.destroy()

        # 截取选定区域
        if x2 > x1 and y2 > y1:
            try:
                self.screenshot = pyautogui.screenshot(region=(x1, y1, x2 - x1, y2 - y1))
            except Exception as e:
                messagebox.showerror("错误", f"截图失败: {str(e)}")

    def on_cancel(self, event):
        """取消截图"""
        self.root.destroy()

    def select_region(self):
        """开始选择区域并返回截图结果"""
        try:
            self.root.wait_window()  # 等待窗口关闭
            return self.screenshot
        except Exception as e:
            messagebox.showerror("错误", f"区域选择过程中出错: {e}")
            self.root.destroy()
            return None


if __name__ == "__main__":
    try:
        app = ScreenshotTool()
        app.run()
    except KeyboardInterrupt:
        logging.info("程序被用户中断")
    except Exception as e:
        logging.error(f"程序运行出错: {e}")
        messagebox.showerror("错误", f"程序运行出错: {e}")
    finally:
        logging.info("程序已退出")