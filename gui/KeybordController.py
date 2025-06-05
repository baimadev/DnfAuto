import ctypes
import time
import random
import threading
import sys


class KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ("wVk", ctypes.c_ushort),
        ("wScan", ctypes.c_ushort),
        ("dwFlags", ctypes.c_ulong),
        ("time", ctypes.c_ulong),
        ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))
    ]


class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", ctypes.c_long),
        ("dy", ctypes.c_long),
        ("mouseData", ctypes.c_ulong),
        ("dwFlags", ctypes.c_ulong),
        ("time", ctypes.c_ulong),
        ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))
    ]


class HARDWAREINPUT(ctypes.Structure):
    _fields_ = [
        ("uMsg", ctypes.c_ulong),
        ("wParamL", ctypes.c_short),
        ("wParamH", ctypes.c_ushort)
    ]


class INPUT_UNION(ctypes.Union):
    _fields_ = [
        ("mi", MOUSEINPUT),
        ("ki", KEYBDINPUT),
        ("hi", HARDWAREINPUT),
    ]


class INPUT(ctypes.Structure):
    _fields_ = [
        ("type", ctypes.c_ulong),
        ("union", INPUT_UNION),
    ]


# 常量定义
INPUT_KEYBOARD = 1
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_SCANCODE = 0x0008

# 虚拟键码映射表
VK_CODES = {
    'a': 0x41, 'b': 0x42, 'c': 0x43, 'd': 0x44, 'e': 0x45,
    'f': 0x46, 'g': 0x47, 'h': 0x48, 'i': 0x49, 'j': 0x4A,
    'k': 0x4B, 'l': 0x4C, 'm': 0x4D, 'n': 0x4E, 'o': 0x4F,
    'p': 0x50, 'q': 0x51, 'r': 0x52, 's': 0x53, 't': 0x54,
    'u': 0x55, 'v': 0x56, 'w': 0x57, 'x': 0x58, 'y': 0x59,
    'z': 0x5A,

    '1': 0x31, '2': 0x32, '3': 0x33, '4': 0x34, '5': 0x35,
    '6': 0x36, '7': 0x37, '8': 0x38, '9': 0x39, '0': 0x30,

    ' ': 0x20,  # VK_SPACE
    '\n': 0x0D,  # VK_RETURN
    'enter': 0x0D,
    'tab': 0x09,
    'left_arrow': 0x25,  # VK_LEFT
    'right_arrow': 0x27,  # VK_RIGHT
    'up_arrow': 0x26,  # VK_UP
    'down_arrow': 0x28,  # VK_DOWN
    'shift': 0x10,  # VK_SHIFT
    'ctrl': 0x11,  # VK_CONTROL
    'alt': 0x12,  # VK_MENU
}


class KeyBoard:
    def __init__(self):
        self.user32 = ctypes.WinDLL('user32', use_last_error=True)
        self._setup_sendinput()
        # 人类操作时间参数 (单位: 秒)
        self.press_duration = (0.02, 0.15)  # 按键按下持续时间范围
        self.release_duration = (0.01, 0.1)  # 按键释放间隔时间范围
        self.double_click_interval = (0.05, 0.2)  # 双击间隔时间范围
        self.hold_delay = (0.3, 0.6)  # 持续按住的延迟时间范围
        self.auto_repeat_delay = (0.1, 0.2)  # 自动重复输入的延迟
        self.key_states = {}  # 跟踪按键状态
        self.lock = threading.Lock()

    def _setup_sendinput(self):
        self.SendInput = self.user32.SendInput
        self.SendInput.argtypes = (
            ctypes.c_uint,  # nInputs
            ctypes.POINTER(INPUT),  # pInputs
            ctypes.c_int  # cbSize
        )
        self.SendInput.restype = ctypes.c_uint
        # 获取GetLastError函数
        self.GetLastError = ctypes.windll.kernel32.GetLastError
        self.GetLastError.restype = ctypes.c_uint

    def _get_vk_code(self, key):
        """获取按键的虚拟键码"""
        if key in VK_CODES:
            return VK_CODES[key]
        raise ValueError(f"Unsupported key: '{key}'")

    def _send_key_event(self, key, keydown=True):
        """发送单个键盘事件"""
        vk_code = self._get_vk_code(key)
        flags = 0
        if not keydown:
            flags |= KEYEVENTF_KEYUP

        # 构建输入结构
        ki = KEYBDINPUT(
            wVk=ctypes.c_ushort(vk_code),
            wScan=0,
            dwFlags=flags,
            time=0,
            dwExtraInfo=ctypes.pointer(ctypes.c_ulong(0))
        )

        # 创建输入联合
        input_union = INPUT_UNION(ki=ki)

        # 创建输入结构
        inp = INPUT(
            type=INPUT_KEYBOARD,
            union=input_union
        )

        # 发送输入
        n_inputs = 1
        cb_size = ctypes.sizeof(INPUT)
        result = self.SendInput(n_inputs, ctypes.byref(inp), cb_size)

        # 如果 SendInput 失败，抛出 WinError
        if result != 1:
            error_code = self.GetLastError()
            raise ctypes.WinError(error_code)

    def _random_sleep(self, duration_range):
        """在给定范围内随机休眠"""
        min_dur, max_dur = duration_range
        sleep_time = random.uniform(min_dur, max_dur)
        time.sleep(sleep_time)
        return sleep_time

    def press(self, key):
        """按下按键（不释放）"""
        with self.lock:
            if self.key_states.get(key, False):
                return  # 按键已处于按下状态
            self._send_key_event(key, keydown=True)
            self.key_states[key] = True

    def release(self, key):
        """释放按键"""
        with self.lock:
            if not self.key_states.get(key, False):
                return  # 按键已处于释放状态
            self._send_key_event(key, keydown=False)
            self.key_states[key] = False

    def click(self, key):
        """模拟单击（按下并释放）"""
        self.press(key)
        self._random_sleep(self.press_duration)
        self.release(key)
        self._random_sleep(self.release_duration)

    def double_click(self, key):
        """模拟双击"""
        self.click(key)
        interval = self._random_sleep(self.double_click_interval)
        self.click(key)

    def hold(self, key, duration=None):
        """
        持续按住按键
        :param key: 按键名称
        :param duration: 按住持续时间（秒），如果为None则使用随机时间
        """
        self.press(key)
        if duration is None:
            self._random_sleep(self.hold_delay)
        else:
            time.sleep(duration)

    def double_click_and_hold(self, key, hold_duration=None):
        """双击后持续按住（第二次按下后保持）"""
        # 第一次单击
        self.click(key)

        # 双击间隔
        interval = self._random_sleep(self.double_click_interval)

        # 第二次按下后保持
        self.press(key)
        if hold_duration is None:
            self._random_sleep(self.hold_delay)
        else:
            time.sleep(hold_duration)

    def auto_repeat(self, key, times=3, delay_range=None):
        """
        模拟按键自动重复输入
        :param key: 按键名称
        :param times: 重复次数
        :param delay_range: 重复间隔时间范围
        """
        if delay_range is None:
            delay_range = self.auto_repeat_delay

        # 初始按下
        self.press(key)

        # 等待足够长的时间以触发自动重复
        initial_delay = random.uniform(0.3, 0.5)
        time.sleep(initial_delay)

        # 模拟重复输入
        for _ in range(times):
            self.release(key)
            self._random_sleep(delay_range)
            self.press(key)
            self._random_sleep(delay_range)

        # 最后释放按键
        self.release(key)

    def release_any(self, key=None):
        """释放任意指定按键，如未指定则释放所有按键"""
        with self.lock:
            if key:
                if key in self.key_states and self.key_states[key]:
                    self.release(key)
            else:
                # 释放所有按下的按键
                for k, pressed in list(self.key_states.items()):
                    if pressed:
                        self.release(k)

    def type_string(self, text, speed_range=(0.05, 0.2)):
        """
        模拟输入字符串
        :param text: 要输入的字符串
        :param speed_range: 字符间的输入速度范围（秒）
        """
        for char in text:
            # 只处理支持的字符
            if char.lower() in VK_CODES:
                self.click(char.lower())
                self._random_sleep(speed_range)
            else:
                # 对于不支持的字符，跳过或记录警告
                print(f"Warning: Character '{char}' not supported")


# 使用示例
if __name__ == "__main__":
    import time as sleep_time

    kb = KeyBoard()

    # 给用户5秒时间切换到目标应用
    print("切换到目标应用...")
    sleep_time.sleep(5)

    # 测试基本输入
    print("输入'hello'")
    kb.type_string("hello")

    # 测试回车
    print("按回车")
    kb.click('enter')

    # 测试按住功能（现在会触发系统自动重复）
    print("按住'x'键2秒")
    kb.hold('x', duration=2)  # 按住2秒
    kb.release('x')  # 释放

    # 测试双击并按住
    print("双击并按住'a'键")
    kb.double_click_and_hold('a', hold_duration=1.5)
    kb.release('a')  # 释放

    # 测试方向键操作
    print("双击上箭头")
    kb.double_click('up_arrow')

    print("按住右箭头1秒")
    kb.hold('right_arrow', duration=1)
    kb.release('right_arrow')

    # 测试自动重复功能
    print("模拟重复输入'x'5次")
    kb.auto_repeat('x', times=5)

    # 确保所有按键都已释放
    kb.release_any()
    print("所有测试完成")