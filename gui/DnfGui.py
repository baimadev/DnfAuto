# DnfGUI.py
import tkinter as tk
from tkinter import messagebox
import keyboard  # 全局热键库

class DnfGUI:
    def __init__(self, root, start_callback, stop_callback):
        self.root = root
        self.start_callback = start_callback
        self.stop_callback = stop_callback
        self.running = False

        # 设置窗口
        self.root.title("Title")
        self.root.geometry("400x300")
        self.root.resizable(False, False)
        self.root.attributes('-topmost', 1)

        # ✅ 注册全局快捷键（无需窗口焦点）
        try:
            keyboard.add_hotkey('ctrl+q', self.on_start)
            keyboard.add_hotkey('ctrl+w', self.on_stop)
            print("全局快捷键已注册：Ctrl+Q (启动)，Ctrl+W (停止)")
        except Exception as e:
            print(f"快捷键注册失败: {e}")
            messagebox.showwarning("快捷键冲突", "快捷键已被其他程序占用，请关闭相关程序后重试。")

        # 标题标签
        self.label = tk.Label(root, text="Title", font=("Arial", 16))
        self.label.pack(pady=20)

        # 启动按钮
        self.start_button = tk.Button(
            root, text="启动检测 (Ctrl+Q)", width=25, command=self.on_start
        )
        self.start_button.pack(pady=10)

        # 停止按钮
        self.stop_button = tk.Button(
            root, text="停止检测 (Ctrl+W)", width=25, command=self.on_stop, state=tk.DISABLED
        )
        self.stop_button.pack(pady=10)

        # 日志输出框
        self.log_text = tk.Text(root, height=10, width=50, state='disabled')
        self.log_text.pack(pady=10)

        # 确保窗口获得焦点（用于按钮点击等）
        self.root.update()
        self.root.focus_force()

    # ✅ 新增：启动检测逻辑
    def on_start(self):
        """点击“启动检测”或按下 Ctrl+Q 时调用"""
        if not self.running:
            self.running = True
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.log("实时检测已启动...")
            self.start_callback()

    # ✅ 新增：停止检测逻辑
    def on_stop(self):
        """点击“停止检测”或按下 Ctrl+W 时调用"""
        if self.running:
            self.running = False
            self.stop_button.config(state=tk.DISABLED)
            self.log("检测已停止。")
            self.stop_callback()

    # ✅ 日志输出到文本框
    def log(self, message):
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.config(state='disabled')
        self.log_text.see(tk.END)

    # ✅ 更新按钮状态（外部控制）
    def update_buttons(self, running):
        self.running = running
        self.start_button.config(state=tk.DISABLED if running else tk.NORMAL)
        self.stop_button.config(state=tk.NORMAL if running else tk.DISABLED)
