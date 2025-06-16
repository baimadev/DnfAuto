import time
import threading
import tkinter as tk
from tkinter import messagebox
import pyautogui
import keyboard
from pynput import keyboard as kb

from gui.keybord.keyboard_util import WyhkmCOM


class AutoClickerGUI:
    def __init__(self, root):
        """初始化自动点击器GUI"""
        self.root = root
        self.root.title("自动鼠标点击器")
        self.root.geometry("300x200")
        self.root.resizable(False, False)

        # 点击器状态
        self.running = False
        self.click_thread = None
        self.listener = None
        self.interval = 10.0  # 默认10秒

        # 创建界面
        self.create_widgets()

        # 注册热键
        self.register_hotkeys()

        self.keyboard = WyhkmCOM()


        print("自动点击器已启动，按 Ctrl+Alt+Q 停止")

    def create_widgets(self):
        """创建界面组件"""
        # 间隔设置
        frame_interval = tk.Frame(self.root)
        frame_interval.pack(pady=10)

        tk.Label(frame_interval, text="点击间隔 (秒):").pack(side=tk.LEFT)
        self.entry_interval = tk.Entry(frame_interval, width=5)
        self.entry_interval.pack(side=tk.LEFT, padx=5)
        self.entry_interval.insert(0, str(self.interval))

        # 控制按钮
        frame_buttons = tk.Frame(self.root)
        frame_buttons.pack(pady=10)

        self.btn_start = tk.Button(
            frame_buttons, text="开始点击",
            command=self.start_clicking, width=12, bg="#4CAF50", fg="white"
        )
        self.btn_start.pack(side=tk.LEFT, padx=5)

        self.btn_stop = tk.Button(
            frame_buttons, text="停止点击",
            command=self.stop_clicking, width=12, bg="#f44336", fg="white",
            state=tk.DISABLED
        )
        self.btn_stop.pack(side=tk.RIGHT, padx=5)

        # 状态显示
        self.status_var = tk.StringVar(value="状态: 未启动")
        tk.Label(self.root, textvariable=self.status_var).pack(pady=5)

        # 热键提示
        tk.Label(self.root, text="热键: Ctrl+Alt+Q 停止").pack(pady=5)

    def start_clicking(self):
        """开始自动点击"""
        try:
            # 获取间隔设置
            interval = float(self.entry_interval.get())
            if interval < 1:
                messagebox.showwarning("警告", "间隔时间不能小于1秒")
                return

            self.interval = interval

        except ValueError:
            messagebox.showwarning("警告", "请输入有效的数字")
            return

        if self.running:
            self.status_var.set("状态: 已在运行中")
            return

        self.running = True
        self.btn_start.config(state=tk.DISABLED)
        self.btn_stop.config(state=tk.NORMAL)
        self.status_var.set(f"状态: 运行中 (间隔: {self.interval}秒)")

        self.click_thread = threading.Thread(
            target=self._click_loop, daemon=True
        )
        self.click_thread.start()
        print(f"自动点击已开始，间隔 {self.interval} 秒")

    def stop_clicking(self):
        """停止自动点击"""
        if not self.running:
            self.status_var.set("状态: 未启动")
            return

        self.running = False
        self.btn_start.config(state=tk.NORMAL)
        self.btn_stop.config(state=tk.DISABLED)
        self.status_var.set("状态: 已停止")

        if self.click_thread:
            self.click_thread.join(timeout=1.0)
        print("自动点击已停止")

    def _click_loop(self):
        """点击循环"""
        while self.running:
            try:
                # 点击鼠标左键
                self.keyboard.left_click()
                click_time = time.strftime('%H:%M:%S')
                print(f"点击时间: {click_time}")
                self.root.title(f"自动点击器 - 上次点击: {click_time}")

                # 等待指定间隔
                for _ in range(int(self.interval)):
                    if not self.running:
                        break
                    time.sleep(1)

            except Exception as e:
                messagebox.showerror("错误", f"点击出错: {str(e)}")
                self.stop_clicking()
                time.sleep(1)  # 出错后暂停1秒

    def register_hotkeys(self):
        """注册热键"""

        def on_stop_hotkey():
            if self.running:
                self.stop_clicking()

        # 使用pynput注册全局热键
        self.listener = kb.Listener(
            on_press=lambda key: self._on_key_press(key, on_stop_hotkey)
        )
        self.listener.start()

    def _on_key_press(self, key, callback):
        """热键按下事件处理"""
        try:
            # 检测Ctrl+Alt+Q
            if (key == kb.Key.ctrl_l or key == kb.Key.ctrl_r) and \
                    keyboard.is_pressed('alt') and \
                    keyboard.is_pressed('q'):
                callback()
        except Exception as e:
            print(f"热键检测出错: {e}")

    def on_closing(self):
        """窗口关闭时的处理"""
        if self.running:
            self.stop_clicking()
        if self.listener:
            self.listener.stop()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = AutoClickerGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()