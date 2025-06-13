# DnfGUI.py
import threading
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

        try:
            keyboard.add_hotkey('ctrl+q', self.on_start)
            keyboard.add_hotkey('ctrl+w', self.on_stop)
            print("全局快捷键已注册：Ctrl+Q (启动)，Ctrl+W (停止)")
        except Exception as e:
            print(f"快捷键注册失败: {e}")
            messagebox.showwarning("快捷键冲突", "快捷键已被其他程序占用，请关闭相关程序后重试。")

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

        # 创建Listbox作为日志输出框
        self.log_frame = tk.Frame(root)
        self.log_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        # 创建滚动条
        self.scrollbar = tk.Scrollbar(self.log_frame)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 创建Listbox并关联滚动条
        self.log_listbox = tk.Listbox(
            self.log_frame,
            height=10,
            width=50,
            yscrollcommand=self.scrollbar.set
        )
        self.log_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.config(command=self.log_listbox.yview)

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
            threading.Thread(target=self._run_start_callback, daemon=True).start()

    # ✅ 新增：停止检测逻辑
    def on_stop(self):
        """点击“停止检测”或按下 Ctrl+W 时调用"""
        if self.running:
            self.running = False
            self.stop_button.config(state=tk.DISABLED)
            self.log("检测已停止。")
            threading.Thread(target=self._run_stop_callback, daemon=True).start()

    def _run_start_callback(self):
        """在子线程中执行 start_callback"""
        try:
            self.start_callback()
        except Exception as e:
            self.root.after(0, self.log, f"启动任务出错: {e}")

    def _run_stop_callback(self):
        """在子线程中执行 stop_callback"""
        try:
            self.stop_callback()
        except Exception as e:
            self.root.after(0, self.log, f"停止任务出错: {e}")
        finally:
            # 确保最终更新 UI 在主线程中执行
            self.root.after(0, self._finalize_stop)

    def _finalize_stop(self):
        self.stop_button.config(state=tk.DISABLED)
        self.start_button.config(state=tk.NORMAL)

    def log(self, message):
        import datetime
        log_time = datetime.datetime.now().strftime("%H:%M:%S")
        log_message = f"[{log_time}] {message} \n"
        self.log_listbox.insert(tk.END, log_message)
        self.log_listbox.see(tk.END)

    def update_buttons(self, running):
        self.running = running
        self.start_button.config(state=tk.DISABLED if running else tk.NORMAL)
        self.stop_button.config(state=tk.NORMAL if running else tk.DISABLED)
