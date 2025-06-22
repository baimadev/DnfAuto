import random
import threading
import time
from time import sleep

import cv2
import mss
import numpy as np
import pygetwindow as gw
from ultralytics import YOLO

from gui.keybord.keyboard_util import WyhkmCOM
from gui.utils.scene_navigator import region


class MonsterAttack:
    def __init__(self, utils, yolo_model_path, role_model_path, monsters_data, skill_keys, gui):
        self.utils = WyhkmCOM()
        self.yolo_model = YOLO(yolo_model_path)
        self.yolo_role = YOLO(role_model_path)
        self.monsters = monsters_data
        self.skill_keys = skill_keys
        self.gui = gui
        self.skill_key_map = {
            'a': 65, 's': 83, 'd': 68, 'f': 70, 'g': 71, 'h': 72,
            'q': 81, 'w': 87, 'e': 69, 'r': 82, 't': 84, 'x': 88
        }
        self.current_direction = None

    def get_positions(self, frame_rgb):
        results = self.yolo_role.predict(frame_rgb)
        for result in results:
            for box in result.boxes:
                cls = int(box.cls)
                label = result.names[cls]
                conf = float(box.conf)
                bbox = box.xyxy[0].tolist()
                if label == 'role':
                    x1, y1, x2, y2 = map(float, box.xyxy[0])
                    cx = (x1 + x2) / 2
                    cy = (y1 + y2) / 2
                    print(f"检测到role 位置: ({cx}, {cy})")
                    return cx, cy
        return None, None

    def move_towards_stop_on_monster(self, direction ="Right"):
        frame_counter = 0
        update_interval = 3

        with mss.mss() as sct:
            self.current_direction = None
            self.utils.run_and_hold(direction)

            while True:
                if frame_counter % update_interval == 0:
                    screenshot = sct.grab(region)
                    frame_rgb = cv2.cvtColor(np.array(screenshot), cv2.COLOR_BGRA2RGB)

                    sfjx = self.check_exist(frame_rgb,"sfjx")
                    if sfjx is not None:
                        self.utils.release_keyboard()
                        print(f"检测到 {sfjx} 停止移动")
                        return True

                    yolo_results = self.yolo_model.predict(frame_rgb)
                    for result in yolo_results:
                        for box in result.boxes:
                            confidence = box.conf.item()
                            cls_name = result.names[int(box.cls)]
                            if cls_name in ['small_monster', 'boss']:
                                if confidence <= 0.6:
                                    continue
                                self.utils.release_keyboard()
                                print(f"检测到 {cls_name} 置信度：{confidence:.2f}，停止奔跑")
                                return True
                frame_counter += 1
                time.sleep(0.01)

    def move_to_target(self, target_x, target_y, stop_offset=50):
        # 创建线程间通信对象
        stop_event = threading.Event()
        direction_lock = threading.Lock()
        current_direction = [None]  # 使用列表实现引用传递
        keyboard_released = [False]  # 跟踪键盘释放状态

        # 位置获取和条件检测线程
        def position_and_checker():
            with mss.mss() as sct:
                while not stop_event.is_set():
                    cycle_start = time.time()

                    # 获取当前位置
                    screenshot = sct.grab(region)
                    frame_rgb = cv2.cvtColor(np.array(screenshot), cv2.COLOR_BGRA2RGB)
                    renwu_x, renwu_y = self.get_positions(frame_rgb)

                    # 位置检测失败处理
                    if renwu_x is None or renwu_y is None:
                        print("未检测到人物，停止运行")
                        self.utils.release_keyboard()
                        stop_event.set()
                        break

                    # 实时计算距离
                    dx = abs(renwu_x - target_x)

                    # 检查停止条件
                    if dx <= stop_offset:
                        print(f"[检测] 达到停止条件 (dx={dx} <= {stop_offset})")
                        self.utils.release_keyboard()
                        keyboard_released[0] = True
                        stop_event.set()
                        break

                    # 计算新方向（供移动线程使用）
                    new_dir = 'Right' if target_x > renwu_x else 'Left'

                    # 更新方向（如果有变化）
                    with direction_lock:
                        if current_direction[0] != new_dir:
                            # 方向变化时释放旧按键
                            if current_direction[0] is not None:
                                self.utils.release_keyboard()
                                keyboard_released[0] = True
                            current_direction[0] = new_dir

                    # 控制循环频率（约50FPS）
                    cycle_time = (time.time() - cycle_start) * 1000  # 毫秒
                    if cycle_time < 20:  # 如果执行时间不足20ms
                        time.sleep((20 - cycle_time) / 1000)  # 休眠剩余时间

                    # 可选：调试信息
                    # print(f"[检测] 循环耗时: {cycle_time:.2f}ms, dx: {dx}, 方向: {new_dir}")

        # 移动控制线程（使用短按避免长时间阻塞）
        def movement_controller():
            last_direction = None
            while not stop_event.is_set():
                # 获取当前方向
                with direction_lock:
                    direction = current_direction[0]

                # 如果没有方向信息，短暂等待
                if direction is None:
                    time.sleep(0.01)
                    continue

                # 方向切换处理
                if direction != last_direction:
                    if last_direction is not None:
                        # 方向切换时已在检测线程释放按键
                        pass
                    last_direction = direction
                    print(f"[移动] 方向: {direction}")

                # 使用短按避免长时间阻塞（150ms）
                if not keyboard_released[0]:
                    self.utils.run(direction, 800, 10)

                # 短暂休眠
                time.sleep(0.01)

        # 启动线程
        checker_thread = threading.Thread(target=position_and_checker, daemon=True)
        mover_thread = threading.Thread(target=movement_controller, daemon=True)

        checker_thread.start()
        time.sleep(0.1)  # 确保检测线程先启动
        mover_thread.start()

        # 等待线程结束
        checker_thread.join()
        mover_thread.join(timeout=0.5)

        # 确保键盘最终被释放
        if not keyboard_released[0]:
            self.utils.release_keyboard()

        # 返回结果
        if stop_event.is_set():
            print("成功到达目标")
            return True
        print("未能到达目标")
        return False

    def face_monster(self, renwu_x, monster_x):
        direction = 'Right' if monster_x > renwu_x else 'Left'
        print(f"face_monster {direction} ")
        self.utils.key_press(direction)
        self.utils.release_keyboard()
        print(f"调整方向朝 {direction}")

    def attack_small_or_elite(self, frame, x1, y1, x2, y2):
        monster_x = x1 + (x2 - x1) // 2
        monster_y = y1 + (y2 - y1) // 2
        print(f"检测到普通怪物位置: ({monster_x}, {monster_y})")
        return self._attack_monster(frame, monster_x, monster_y, is_boss=False)

    def attack_boss(self, frame, x1, y1, x2, y2):
        monster_x = x1 + (x2 - x1) // 2
        monster_y = y1 + (y2 - y1) // 2
        print(f"检测到 Boss 位置: ({monster_x}, {monster_y})")
        return self._attack_monster(frame, monster_x, monster_y, is_boss=True)

    def getPositions(self, frame_rgb, cls):
        results = self.yolo_role.predict(frame_rgb)
        for result in results:
            for box in result.boxes:
                cls_name = result.names[int(box.cls)]
                if cls_name == cls:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    cx = (x1 + x2) / 2  # 计算中心点 x 坐标
                    cy = (y1 + y2) / 2  # 计算中心点 y 坐标
                    return cx, cy
        return None,None

    def check_exist(self, frame_rgb, cls):
        results = self.yolo_role.predict(frame_rgb)
        for result in results:
            for box in result.boxes:
                confidence = box.conf.item()
                if confidence < 0.6:
                     continue
                cls_name = result.names[int(box.cls)]
                if cls_name == cls:
                    return cls_name
        return None

    def random_move(self):
        direction = random.choice(["Left", "Right"])
        self.utils.run(direction, 1000, 100)
        time.sleep(random.uniform(0.4011, 0.6011))


    def _attack_monster(self, frame, monster_x, monster_y, is_boss=False):
        self.utils.activate_window(gw.getWindowsWithTitle("地下城与勇士：创新世纪")[0])

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGRA2RGB)
        renwu_x, renwu_y = self.get_positions(frame_rgb)
        if renwu_x is not None and renwu_y is not None:
            print(f"renwu 初始位置: ({renwu_x}, {renwu_y})")
            self.move_to_target(monster_x, monster_y)
        else:
            print("初始未检测到 renwu，但因检测到怪物，继续尝试移动并攻击")

        with mss.mss() as sct:
            while True:
                screenshot = sct.grab(region)
                gray_frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_BGRA2GRAY)
                frame_rgb = cv2.cvtColor(np.array(screenshot), cv2.COLOR_BGRA2RGB)
                renwu_x, renwu_y = self.get_positions(frame_rgb)

                if renwu_x is not None and renwu_y is not None:
                    self.face_monster(renwu_x, monster_x)
                    print(f"renwu 当前位置: ({renwu_x}, {renwu_y})，开始攻击")
                else:
                    print("未检测到 renwu，默认朝怪物方向攻击")

                skill_count = random.randint(2, 3)
                print(f"计划释放 {skill_count} 个技能")
                for i in range(skill_count):
                    cx,cy = self.getPositions(frame_rgb,"forward")
                    if cx is not None:
                        self.utils.release_keyboard()
                        print("检测到前进，表示小怪已死，立即停止攻击")
                        return True
                    skill_key = random.choice(self.skill_keys)
                    print(f"释放技能 {skill_key} (第 {i+1}/{skill_count})")
                    self.utils.key_press(skill_key)
                    time.sleep(random.uniform(0.1011, 0.1511))
                    screenshot = sct.grab(region)
                    gray_frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_BGRA2GRAY)

                cx,cy = self.getPositions(frame_rgb,"forward")
                if cx is not None:
                    print("检测到前进，表示小怪已死，立即停止攻击")
                    return True
                print("技能释放完毕，执行一次普通攻击 X")
                self.utils.key_press("x")  # X 键普通攻击
                time.sleep(random.uniform(0.01011, 0.03011))
                screenshot = sct.grab(region)
                gray_frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_BGRA2GRAY)
                current_frame_rgb = cv2.cvtColor(np.array(screenshot), cv2.COLOR_BGRA2RGB)
                monster_still_exists = False
                monster_type = 'boss' if is_boss else 'elite_monster' if 'template' in self.monsters.get('elite_monster', {}) else 'small_monster'
                if monster_type == 'elite_monster':
                    locations = self.utils.detect_template(gray_frame, self.monsters['elite_monster']['template'])
                    monster_still_exists = any(abs(monster_x - (loc[0] + (loc[2] - loc[0]) // 2)) < 50 for loc in locations)
                else:
                    yolo_results = self.yolo_model.predict(current_frame_rgb)
                    for result in yolo_results:
                        for box in result.boxes:
                            if result.names[int(box.cls)] == monster_type:
                                mx1, my1, mx2, my2 = map(int, box.xyxy[0])
                                if abs(monster_x - (mx1 + (mx2 - mx1) // 2)) < 50:
                                    monster_still_exists = True
                                    break

                if not monster_still_exists:
                    print("怪物已消失，停止攻击")
                    return False

                renwu_x, renwu_y = self.get_positions(frame_rgb)
                if renwu_x is None or renwu_y is None:
                    print(f"一轮攻击后未检测到人物，尝试随机移动脱离遮挡")
                    self.random_move()
