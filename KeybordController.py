import ctypes
from ctypes import wintypes
import time
import random


class KeyboardController:
    """基于Windows API的键盘控制器，支持多键同时操作"""

    # 键盘虚拟键码常量
    VK_KEYS = {
        'backspace': 0x08, 'tab': 0x09, 'clear': 0x0C, 'enter': 0x0D,
        'shift': 0x10, 'ctrl': 0x11, 'alt': 0x12, 'pause': 0x13,
        'caps_lock': 0x14, 'esc': 0x1B, 'spacebar': 0x20, 'page_up': 0x21,
        'page_down': 0x22, 'end': 0x23, 'home': 0x24, 'left_arrow': 0x25,
        'up_arrow': 0x26, 'right_arrow': 0x27, 'down_arrow': 0x28,
        'select': 0x29, 'print': 0x2A, 'execute': 0x2B, 'print_screen': 0x2C,
        'ins': 0x2D, 'del': 0x2E, 'help': 0x2F,
        '0': 0x30, '1': 0x31, '2': 0x32, '3': 0x33, '4': 0x34,
        '5': 0x35, '6': 0x36, '7': 0x37, '8': 0x38, '9': 0x39,
        'a': 0x41, 'b': 0x42, 'c': 0x43, 'd': 0x44, 'e': 0x45,
        'f': 0x46, 'g': 0x47, 'h': 0x48, 'i': 0x49, 'j': 0x4A,
        'k': 0x4B, 'l': 0x4C, 'm': 0x4D, 'n': 0x4E, 'o': 0x4F,
        'p': 0x50, 'q': 0x51, 'r': 0x52, 's': 0x53, 't': 0x54,
        'u': 0x55, 'v': 0x56, 'w': 0x57, 'x': 0x58, 'y': 0x59, 'z': 0x5A,
        'numpad_0': 0x60, 'numpad_1': 0x61, 'numpad_2': 0x62,
        'numpad_3': 0x63, 'numpad_4': 0x64, 'numpad_5': 0x65,
        'numpad_6': 0x66, 'numpad_7': 0x67, 'numpad_8': 0x68, 'numpad_9': 0x69,
        'multiply_key': 0x6A, 'add_key': 0x6B, 'separator_key': 0x6C,
        'subtract_key': 0x6D, 'decimal_key': 0x6E, 'divide_key': 0x6F,
        'f1': 0x70, 'f2': 0x71, 'f3': 0x72, 'f4': 0x73, 'f5': 0x74,
        'f6': 0x75, 'f7': 0x76, 'f8': 0x77, 'f9': 0x78, 'f10': 0x79,
        'f11': 0x7A, 'f12': 0x7B, 'f13': 0x7C, 'f14': 0x7D,
        'f15': 0x7E, 'f16': 0x7F, 'f17': 0x80, 'f18': 0x81,
        'f19': 0x82, 'f20': 0x83, 'f21': 0x84, 'f22': 0x85,
        'f23': 0x86, 'f24': 0x87,
        'num_lock': 0x90, 'scroll_lock': 0x91,
        'left_shift': 0xA0, 'right_shift': 0xA1,
        'left_ctrl': 0xA2, 'right_ctrl': 0xA3,
        'left_alt': 0xA4, 'right_alt': 0xA5,
        'browser_back': 0xA6, 'browser_forward': 0xA7,
        'browser_refresh': 0xA8, 'browser_stop': 0xA9,
        'browser_search': 0xAA, 'browser_favorites': 0xAB,
        'browser_start_and_home': 0xAC, 'volume_mute': 0xAD,
        'volume_Down': 0xAE, 'volume_up': 0xAF,
        'next_track': 0xB0, 'previous_track': 0xB1,
        'stop_media': 0xB2, 'play/pause_media': 0xB3,
        'start_mail': 0xB4, 'select_media': 0xB5,
        'start_application_1': 0xB6, 'start_application_2': 0xB7
    }

    def __init__(self):
        """初始化键盘控制器"""
        self.user32 = ctypes.windll.user32

        # 定义必要的结构体
        class KEYBDINPUT(ctypes.Structure):
            _fields_ = [
                ("wVk", wintypes.WORD),
                ("wScan", wintypes.WORD),
                ("dwFlags", wintypes.DWORD),
                ("time", wintypes.DWORD),
                ("dwExtraInfo", ctypes.POINTER(wintypes.ULONG))
            ]

        class INPUT(ctypes.Structure):
            class _INPUT(ctypes.Union):
                _fields_ = [("ki", KEYBDINPUT)]

            _anonymous_ = ("_input",)
            _fields_ = [("type", wintypes.DWORD), ("_input", _INPUT)]

        self.KEYBDINPUT = KEYBDINPUT
        self.INPUT = INPUT

        # 输入类型常量
        self.INPUT_KEYBOARD = 1
        self.KEYEVENTF_KEYDOWN = 0x0000
        self.KEYEVENTF_KEYUP = 0x0002

        # 额外信息
        self.extra = ctypes.c_ulong(0)

        # 记录当前按住的键（使用集合支持多键）
        self.held_keys = set()

    def _get_vk_code(self, key):
        """获取键名对应的虚拟键码"""
        if isinstance(key, int):
            return key
        elif isinstance(key, str):
            key = key.lower()
            if key in self.VK_KEYS:
                return self.VK_KEYS[key]
            elif len(key) == 1 and ord('a') <= ord(key) <= ord('z'):
                return ord(key.upper())
            elif len(key) == 1 and ord('0') <= ord(key) <= ord('9'):
                return ord(key)
        raise ValueError(f"未知的键: {key}")

    def press(self, key):
        """按下指定键"""
        key = key.lower()  # 统一小写处理
        if key not in self.held_keys:
            vk = self._get_vk_code(key)
            input_struct = self.INPUT(
                type=self.INPUT_KEYBOARD,
                ki=self.KEYBDINPUT(
                    wVk=vk,
                    wScan=0,
                    dwFlags=self.KEYEVENTF_KEYDOWN,
                    time=0,
                    dwExtraInfo=ctypes.pointer(self.extra)
                )
            )
            self.user32.SendInput(1, ctypes.byref(input_struct), ctypes.sizeof(input_struct))
            self.held_keys.add(key)

    def release(self, key):
        """释放指定键"""
        key = key.lower()  # 统一小写处理
        if key in self.held_keys:
            vk = self._get_vk_code(key)
            input_struct = self.INPUT(
                type=self.INPUT_KEYBOARD,
                ki=self.KEYBDINPUT(
                    wVk=vk,
                    wScan=0,
                    dwFlags=self.KEYEVENTF_KEYUP,
                    time=0,
                    dwExtraInfo=ctypes.pointer(self.extra)
                )
            )
            self.user32.SendInput(1, ctypes.byref(input_struct), ctypes.sizeof(input_struct))
            self.held_keys.remove(key)

    def tap(self, key, delay=0.05):
        """敲击指定键(按下并释放)"""
        self.press(key)
        time.sleep(delay)  # 模拟人类按键间隔
        self.release(key)

    def double_tap(self, key, interval_range=(0.05, 0.15), post_delay_range=(0.05, 0.15)):
        """双击指定键，参数可控制两次敲击之间的间隔和双击后的延迟"""
        interval = random.uniform(*interval_range)
        post_delay = random.uniform(*post_delay_range)

        self.tap(key)
        time.sleep(interval)
        self.tap(key)
        time.sleep(post_delay)

    def direction_double_tap(self, direction, press_time_range=(0.05, 0.1), interval_range=(0.03, 0.08)):
        """模拟方向键的双击，先按下保持一小段时间再快速双击"""
        press_time = random.uniform(*press_time_range)
        interval = random.uniform(*interval_range)

        # 按下方向键
        self.press(direction)
        time.sleep(press_time)

        # 快速双击
        self.release(direction)
        time.sleep(0.01)  # 短暂释放
        self.press(direction)
        time.sleep(interval)
        self.release(direction)
        time.sleep(0.01)
        self.press(direction)
        time.sleep(interval)
        self.release(direction)

    def double_tap_and_hold(self, key, double_interval_range=(0.03, 0.08), hold_delay=0.05):
        """双击指定键后持续按住"""
        # 双击
        interval = random.uniform(*double_interval_range)

        self.press(key)
        time.sleep(0.02)  # 第一次按下
        self.release(key)
        time.sleep(interval)  # 双击间隔

        self.press(key)
        time.sleep(0.02)  # 第二次按下
        self.release(key)
        time.sleep(hold_delay)  # 准备按住前的延迟

        # 再次按下并保持
        self.press(key)

    def release_all(self):
        """释放所有按住的键"""
        for key in list(self.held_keys):
            self.release(key)

    def type_string(self, text, delay_range=(0.05, 0.15)):
        """输入字符串，每个字符之间有随机延迟"""
        for char in text:
            if char.isupper() or (char in '!@#$%^&*()_+' and char != '+'):
                self.press('shift')
                self.tap(char.lower())
                self.release('shift')
            else:
                self.tap(char)
            # 添加随机延迟，模拟人类输入
            time.sleep(random.uniform(*delay_range))

    def combination(self, keys, delay=0.05):
        """执行组合键，如Ctrl+C, Alt+Tab等"""
        # 按下所有键
        for key in keys[:-1]:
            self.press(key)
            time.sleep(delay)

        # 按下并释放最后一个键
        self.tap(keys[-1])

        # 逆序释放其他键
        for key in reversed(keys[:-1]):
            self.release(key)
            time.sleep(delay)

    def humanized_keystroke(self, key, press_time_range=(0.05, 0.15), between_delay_range=(0.02, 0.08)):
        """模拟人类不规则的按键方式"""
        press_time = random.uniform(*press_time_range)
        start_time = time.time()

        # 模拟不规则的按键压力
        while time.time() - start_time < press_time:
            self.press(key)
            time.sleep(random.uniform(0.005, 0.02))
            self.release(key)
            time.sleep(random.uniform(0.003, 0.01))
            self.press(key)

        # 释放按键后添加随机延迟
        time.sleep(random.uniform(*between_delay_range))


# 使用示例：多键同时操作
if __name__ == "__main__":
    keyboard = KeyboardController()

    try:
        # 双击右方向键开始向右移动
        # keyboard.double_tap_and_hold('right_arrow')
        # print("开始向右移动")
        # time.sleep(1)

        # 按住X键开始攻击（与方向键同时按住）
        keyboard.press('x')
        print("开始攻击，同时继续移动")
        time.sleep(10)

        # 释放X键停止攻击，但继续移动
        # keyboard.release('x')
        # print("停止攻击，继续移动")
        # time.sleep(1)

        # 释放方向键停止移动
        # keyboard.release('right_arrow')
        # print("停止移动")

    finally:
        # 确保释放所有按键，避免残留
        keyboard.release_all()
        print("已释放所有按键")