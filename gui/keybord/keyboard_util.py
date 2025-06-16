import os
import ctypes
import platform
from time import sleep
import time
import pythoncom
import win32com.client
import concurrent.futures

KEY_MAP = {
    'Backspace': 8, 'Tab': 9, 'Enter': 13, 'Shift': 16, 'Ctrl': 17, 'Alt': 18,
    'CapsLock': 20, 'Esc': 27, 'Space': 32, 'PageUp': 33, 'PageDown': 34,
    'End': 35, 'Home': 36, 'Left': 37, 'Up': 38, 'Right': 39, 'Down': 40,
    'PrintScreen': 44, 'Insert': 45, 'Delete': 46,
    '0': 48, '1': 49, '2': 50, '3': 51, '4': 52, '5': 53, '6': 54, '7': 55, '8': 56, '9': 57,
    'A': 65, 'B': 66, 'C': 67, 'D': 68, 'E': 69, 'F': 70, 'G': 71, 'H': 72, 'I': 73,
    'J': 74, 'K': 75, 'L': 76, 'M': 77, 'N': 78, 'O': 79, 'P': 80, 'Q': 81, 'R': 82,
    'S': 83, 'T': 84, 'U': 85, 'V': 86, 'W': 87, 'X': 88, 'Y': 89, 'Z': 90,
    'F1': 112, 'F2': 113, 'F3': 114, 'F4': 115, 'F5': 116, 'F6': 117, 'F7': 118,
    'F8': 119, 'F9': 120, 'F10': 121, 'F11': 122, 'F12': 123,
    'NumLock': 144, 'ScrollLock': 145,
    ';': 186, '=': 187, ',': 188, '-': 189, '.': 190, '/': 191, '`': 192,
    '[': 219, '\\': 220, ']': 221, "'": 222
}

class WyhkmCOM:
    _instance = None  # 单例实例
    _initialized = False  # 标记是否已初始化

    def __new__(cls, dll_path=None, auto_connect=True):
        """实现单例模式"""
        if cls._instance is None:
            cls._instance = super(WyhkmCOM, cls).__new__(cls)
            # 初始化标志设为False，将在__init__中完成
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, dll_path=None, auto_connect=True):
        """初始化无涯键鼠盒子COM组件（单例模式）"""
        if self._initialized:
            return

        self._initialized = True

        # 设置DLL路径
        if dll_path:
            self.dll_path = dll_path
        else:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            self.dll_path = os.path.join(current_dir, "wyhkm.dll")

        self.dll = None
        self.com_object = None
        self._current_device = None
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)

        # 检查DLL文件是否存在
        if not os.path.exists(self.dll_path):
            raise FileNotFoundError(f"DLL文件不存在: {self.dll_path}")

        # 检查Python和DLL的位数是否匹配
        self.is_64bit_python = platform.architecture()[0] == '64bit'
        self._check_architecture_compatibility()

        # 自动连接设备
        if auto_connect:
            self._auto_initialize()

    def _check_architecture_compatibility(self):
        """检查Python环境和DLL的位数是否匹配"""
        dll_arch_hint = "64位" if "system32" in self.dll_path.lower() else "32位"
        python_arch = "64位" if self.is_64bit_python else "32位"

        if (self.is_64bit_python and "syswow64" in self.dll_path.lower()) or \
                (
                        not self.is_64bit_python and "system32" in self.dll_path.lower() and "syswow64" not in self.dll_path.lower()):
            print(f"警告: {python_arch} Python环境正在尝试加载{dll_arch_hint} DLL，这可能会导致错误")

    def _auto_initialize(self):
        """自动完成初始化、注册、连接设备的流程"""
        # 加载DLL
        if not self.load_dll():
            raise RuntimeError("DLL加载失败")

        # 进程内注册
        if not self.inprocess_register():
            raise RuntimeError("DLL进程内注册失败")

        # 创建COM对象
        if not self.create_com_object():
            raise RuntimeError("COM对象创建失败")

        # 获取版本信息
        version = self.get_version()
        if version is not None:
            print(f"模块版本: 0x{version:X}")

        # 搜索并打开设备
        device_id = self.search_device()
        if device_id >= 0:
            # 尝试默认DPI模式
            if not self.open_device(device_id, dpi_mode=0):
                # 尝试使用DPI模式3（禁用DPI支持）
                if not self.open_device(device_id, dpi_mode=3):
                    raise RuntimeError("设备打开失败，所有DPI模式尝试均失败")
            else:
                print("初始化键鼠配置")
                self.com_object.SetKeyInterval(100, 150)
                self.com_object.SetMousePosMaxOffset(3)
                self.com_object.SetMouseInterval(100, 150)

        else:
            raise RuntimeError("未找到无涯键鼠盒子设备")

    def _ensure_initialized(self):
        """确保COM对象已初始化"""
        if self.com_object is None:
            self._auto_initialize()

    def _ensure_device_open(self):
        """确保设备已打开"""
        self._ensure_initialized()
        if self._current_device is None:
            # 尝试重新连接设备
            device_id = self.search_device()
            if device_id >= 0:
                if not self.open_device(device_id):
                    raise RuntimeError("设备打开失败")
            else:
                raise RuntimeError("未找到已连接的设备")

    def load_dll(self):
        """加载DLL文件"""
        try:
            self.dll = ctypes.CDLL(self.dll_path)
            print(f"DLL {self.dll_path} 加载成功")
            return True
        except Exception as e:
            print(f"DLL加载失败: {e}")
            return False

    def inprocess_register(self):
        """进程内注册DLL"""
        if not self.dll:
            if not self.load_dll():
                return False

        try:
            # 获取DllInstall函数
            DllInstall = self.dll.DllInstall

            # 设置参数类型
            if self.is_64bit_python:
                # 64位Python环境
                DllInstall.argtypes = [ctypes.c_int32, ctypes.c_int64]
            else:
                # 32位Python环境
                DllInstall.argtypes = [ctypes.c_int32, ctypes.c_int32]

            # 设置返回值类型
            DllInstall.restype = ctypes.c_int32

            # 调用DllInstall函数（参数1=1表示安装，参数2=2表示进程内注册）
            result = DllInstall(1, 2)

            if result >= 0:
                print(f"DLL {self.dll_path} 进程内注册成功")
                return True
            else:
                print(f"DLL进程内注册失败，返回代码: {result}")
                return False

        except Exception as e:
            print(f"进程内注册DLL时出错: {e}")
            return False

    def create_com_object(self):
        """创建COM对象"""
        try:
            # 创建COM对象
            self.com_object = win32com.client.Dispatch("wyp.hkm")
            print("成功创建无涯键鼠盒子COM对象")
            return True
        except Exception as e:
            print(f"创建COM对象失败: {e}")
            return False

    def get_version(self):
        """获取模块版本"""
        self._ensure_initialized()
        try:
            version = self.com_object.GetVersion()
            return version
        except Exception as e:
            print(f"获取版本号失败: {e}")
            return None

    def search_device(self, vid=9746, pid=5889, mode=0):
        """
        查找无涯键鼠盒子设备

        参数:
            vid (int): 设备VID，65536表示忽略此条件
            pid (int): 设备PID，65536表示忽略此条件
            mode (int): 设备模式，0=所有模式，1=键鼠模式，2=键盘模式，3=鼠标模式

        返回:
            int: 设备ID号，-1表示未找到或失败
        """
        self._ensure_initialized()
        try:
            # 调用SearchDevice方法
            device_id = self.com_object.SearchDevice(vid, pid, mode)

            if device_id >= 0:
                print(f"找到设备，ID号: {device_id}")
            else:
                print("未找到设备或搜索失败")

            return device_id
        except Exception as e:
            print(f"搜索设备失败: {e}")
            return -1

    def open_device(self, device_id=None, dpi_mode=0):
        """
        打开无涯键鼠盒子设备

        参数:
            device_id (int): 设备ID号，由search_device返回，若为None则搜索并打开第一个设备
            dpi_mode (int): DPI模式，可选值0-4

        返回:
            bool: 打开成功返回True，失败返回False
        """
        self._ensure_initialized()

        # 如果未指定设备ID，搜索并打开第一个设备
        if device_id is None:
            device_id = self.search_device()
            if device_id < 0:
                print("未找到可打开的设备")
                return False

        try:
            # 调用Open方法
            result = self.com_object.Open(device_id, dpi_mode)

            if result:
                print(f"设备 {device_id} 打开成功，DPI模式: {dpi_mode}")
                self._current_device = device_id  # 记录当前打开的设备
            else:
                print(f"设备 {device_id} 打开失败，DPI模式: {dpi_mode}")

            return result
        except Exception as e:
            print(f"打开设备失败: {e}")
            return False

    def close_device(self, device_id=None):
        """
        关闭无涯键鼠盒子设备

        参数:
            device_id (int): 设备ID号，默认为当前打开的设备
        """
        if self.com_object is None:
            print("COM对象未初始化，无需关闭设备")
            return True

        # 如果未指定设备ID，使用当前记录的设备ID
        if device_id is None:
            device_id = self._current_device

        if device_id is None:
            print("没有需要关闭的设备")
            return True

        try:
            # 调用Close方法
            self.com_object.Close(device_id)
            print(f"设备 {device_id} 已关闭")
            if device_id == self._current_device:
                self._current_device = None  # 清除当前设备记录
            return True
        except Exception as e:
            print(f"关闭设备失败: {e}")
            return False

    def __del__(self):
        """对象销毁时自动关闭设备"""
        self.close_device()
        self.executor.shutdown(wait=True)

    def left_long_click(self):
        self._ensure_device_open()
        try:
            self.com_object.LeftDown()
            self.com_object.DelayRnd(90, 120)
            self.com_object.LeftUp()
            return True
        except Exception as e:
            print(f"鼠标左键长按失败: {e}")
            return False

    def left_click(self):
        self._ensure_device_open()
        try:
            self.com_object.LeftClick()
            return True
        except Exception as e:
            print(f"鼠标左键点击失败: {e}")
            return False

    def right_click(self):
        self._ensure_device_open()
        try:
            self.com_object.RightClick()
            return True
        except Exception as e:
            print(f"鼠标右键点击失败: {e}")
            return False

    def right_double_click(self):
        self._ensure_device_open()
        try:
            self.com_object.RightDoubleClick()
            return True
        except Exception as e:
            print(f"鼠标双击右键失败: {e}")
            return False

    def left_double_click(self):
        self._ensure_device_open()
        try:
            self.com_object.LeftDoubleClick()
            return True
        except Exception as e:
            print(f"鼠标双击左键失败: {e}")
            return False

    def key_press(self, key):
        """
        模拟按键或组合键（按下并释放）

        参数:
            key (int/str):
                - 键码（如 65）
                - 键名（如 "A"、"F1"）
                - 组合键（如 "Ctrl+C"、"Shift+Alt+F1"）

        返回:
            bool: 成功返回 True，失败返回 False
        """
        self._ensure_device_open()
        try:
            return self.com_object.KeyPress(key)
        except Exception as e:
            print(f"按键模拟失败，键 '{key}': {e}")
            return False

    # delay millisecond
    def key_long_press(self, key, delay=100):
        self._ensure_device_open()
        try:
            self.com_object.KeyDown(key)
            self.com_object.DelayRnd(delay - 200, delay + 200)
            self.com_object.KeyUp(key)
        except Exception as e:
            print(f"长按失败，键'{key}': {e}")

    def run(self, key, delay = 1000):
        self._ensure_device_open()
        try:
            self.com_object.KeyDown(key)
            self.com_object.DelayRnd(90, 120)
            self.com_object.KeyUp(key)
            self.com_object.DelayRnd(90, 120)
            self.com_object.KeyDown(key)
            self.com_object.DelayRnd(delay - 200, delay + 200)
            self.com_object.KeyUp(key)
        except Exception as e:
            print(f"run失败，键'{key}': {e}")

    def release_keyboard(self):
        self._ensure_device_open()
        try:
            self.com_object.ReleaseKeyboard()
        except Exception as e:
            print(f"释放键盘失败: {e}")

    def get_cursor_pos(self):
        """
        获取当前鼠标在操作系统桌面中的坐标

        返回:
            tuple: (x, y) 坐标值，如果失败返回 None
        """
        self._ensure_device_open()
        try:
            # 创建用于接收坐标的变量
            x = win32com.client.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_I4, 0)
            y = win32com.client.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_I4, 0)

            # 调用GetCursorPos方法
            result = self.com_object.GetCursorPos(x, y)

            if result:
                # 获取返回的坐标值
                mouse_x = x.value
                mouse_y = y.value
                print(f"成功获取鼠标坐标: ({mouse_x}, {mouse_y})")
                return (mouse_x, mouse_y)
            else:
                print("获取鼠标坐标失败")
                return None

        except Exception as e:
            print(f"获取鼠标坐标时出错: {e}")
            return None

    def move_to(self, x, y):
        """移动鼠标到指定坐标"""
        self._ensure_device_open()
        try:
            if self.com_object.MoveTo(x, y):
                print(f"鼠标已移动到坐标: ({x}, {y})")
                return True
            else:
                print(f"移动鼠标失败，坐标: ({x}, {y})")
                return False
        except Exception as e:
            print(f"移动鼠标失败: {e}")
            return False

    def move_to_target(self, role_x, role_y, target_x, target_y, threshold=5, max_attempts=10):
        attempts = 0
        while attempts < max_attempts:
            if self.is_near_target(role_x, role_y, target_x, target_y, threshold):
                print(f"角色已到达目标附近 (尝试 {attempts} 次)")
                return True
            self.role_move_to(role_x, role_y, target_x, target_y, threshold)

            # 获取角色当前位置 成员变量实时更新
            role_x, role_y = self.simulate_movement(role_x, role_y, target_x, target_y)
            attempts += 1
            time.sleep(0.1)
        print(f"移动失败，超过最大尝试次数 ({max_attempts})")
        return False

    def simulate_movement(self, role_x, role_y, target_x, target_y):
        """模拟移动后的位置（实际应用中应替换为从游戏获取真实位置）"""
        # 简单模拟：每次移动1/4距离
        return role_x + (target_x - role_x) / 4, role_y + (target_y - role_y) / 4
    def is_near_target(self, role_x, role_y, target_x, target_y, threshold=5, distance_type='euclidean'):
        #distance_type: 距离计算方式 ('euclidean' 或 'manhattan')
        # 计算距离
        if distance_type == 'euclidean':
            # 欧几里得距离 (直线距离)
            distance = ((role_x - target_x) ** 2 + (role_y - target_y) ** 2) ** 0.5
        elif distance_type == 'manhattan':
            # 曼哈顿距离 (网格距离)
            distance = abs(role_x - target_x) + abs(role_y - target_y)
        else:
            raise ValueError(f"无效的距离类型: {distance_type}")
        return distance <= threshold

    def role_move_to(self, role_x, role_y, target_x, target_y, threshold=5):
        spacing_x = target_x - role_x
        spacing_y = target_y - role_y
        vehicle = 10
        time_x = abs(spacing_x) / vehicle
        time_y = abs(spacing_y) / vehicle
        print(f"spacing_x:{spacing_x} spacing_y:{spacing_y}")
        print(f"time_x:{time_x} time_y:{time_y}")

        if abs(spacing_x) >= threshold:
            if spacing_x > 0:
                self.run("Right", time_x * 1000)
            elif spacing_x < 0:
                self.run("Left", time_x * 1000)

        if abs(spacing_y) >= threshold:
            if spacing_y > 0:
                self.run("Down", time_y * 1000)
            elif spacing_y < 0:
                self.run("Up", time_y * 1000)


if __name__ == "__main__":
    wyhkm1 = WyhkmCOM()
    # 原有测试代码
    sleep(4)
    def test_run():
        print("run start")
        wyhkm1.run("Right", 4000)

        # delay = 4
        # wyhkm1.com_object.KeyDown(key)
        # sleep(delay)
        # #wyhkm1.com_object.DelayRnd(delay - 200, delay + 200)
        # wyhkm1.com_object.KeyUp(key)
    def hold_x():
        print("sleep 2")
        sleep(2)
        print("hold_x start")
        wyhkm1.key_press("Tab")
        delay = 2000
        wyhkm1.com_object.KeyDown("x")
        wyhkm1.com_object.DelayRnd(delay - 200, delay + 200)
        wyhkm1.com_object.KeyUp("x")

    wyhkm1.executor.submit(test_run)
    wyhkm1.executor.submit(hold_x)
