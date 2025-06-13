import pyautogui
import keyboard
import pyperclip
import threading
import time
import sys


def mouse_position_monitor():
    print("鼠标坐标追踪已启动 (按Ctrl+Alt+C复制坐标，Esc退出)")
    print("=" * 50)

    try:
        while not exit_flag.is_set():
            # 获取鼠标坐标
            x, y = pyautogui.position()

            # 覆盖式打印坐标
            sys.stdout.write(f"\r当前坐标: X={x:<4} Y={y:<4} (按Ctrl+Alt+C复制)")
            sys.stdout.flush()

            # 检查复制快捷键
            if keyboard.is_pressed('ctrl+alt+c'):
                pyperclip.copy(f"{x},{y}")
                print("\n\n坐标已复制到剪贴板!")
                time.sleep(0.5)  # 防止连续触发

            # 检查退出键
            if keyboard.is_pressed('esc'):
                print("\n\n程序已退出")
                exit_flag.set()

            time.sleep(0.05)
    finally:
        keyboard.unhook_all()


if __name__ == "__main__":
    exit_flag = threading.Event()

    # 启动鼠标监控线程
    monitor_thread = threading.Thread(target=mouse_position_monitor)
    monitor_thread.daemon = True
    monitor_thread.start()

    try:
        # 主线程保持运行
        while not exit_flag.is_set():
            time.sleep(0.1)
    except KeyboardInterrupt:
        exit_flag.set()