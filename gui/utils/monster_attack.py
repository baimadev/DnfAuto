import random
import time

import cv2
import mss
import numpy as np
import pygetwindow as gw
from ultralytics import YOLO

from gui.keybord.keyboard_util import WyhkmCOM
from gui.utils.scene_navigator import region


class MonsterAttack:
    def __init__(self, utils, yolo_model_path, monsters_data, skill_keys):
        self.utils = WyhkmCOM()
        self.yolo_model = YOLO(yolo_model_path)
        self.monsters = monsters_data
        self.skill_keys = skill_keys
        self.skill_key_map = {
            'a': 65, 's': 83, 'd': 68, 'f': 70, 'g': 71, 'h': 72,
            'q': 81, 'w': 87, 'e': 69, 'r': 82, 't': 84, 'x': 88
        }
        self.current_direction = None

    def get_positions(self, gray_frame):
        renwu_locations = self.utils.detect_template(gray_frame, self.monsters['renwu']['template'])
        if renwu_locations:
            rx1, ry1, rx2, ry2 = renwu_locations[0]
            renwu_x = rx1 + (rx2 - rx1) // 2
            renwu_y = ry1 + 80
            return renwu_x, renwu_y
        return None, None

    def move_to_fixed_point(self, target_x=1060, target_y=369, direction = "Right"):
        frame_counter = 0
        update_interval = 3

        with mss.mss() as sct:
            self.current_direction = None
            self.utils.run_and_hold(direction)

            while True:
                if frame_counter % update_interval == 0:
                    screenshot = sct.grab(region)
                    frame_rgb = cv2.cvtColor(np.array(screenshot), cv2.COLOR_BGRA2RGB)
                    yolo_results = self.yolo_model.predict(frame_rgb)
                    for result in yolo_results:
                        for box in result.boxes:
                            cls_name = result.names[int(box.cls)]
                            if cls_name in ['small_monster', 'boss']:
                                if self.current_direction is not None:
                                    self.utils.com_object.KeyUp(direction)
                                    self.current_direction = None
                                print(f"检测到 {cls_name}，停止奔跑")
                                return True

                frame_counter += 1
                time.sleep(0.01)

    def move_to_target(self, target_x, target_y, stop_offset=50):
        direction = None
        with mss.mss() as sct:
            while True:
                screenshot = sct.grab(region)
                gray_frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_BGRA2GRAY)
                renwu_x, renwu_y = self.get_positions(gray_frame)
                if renwu_x is None or renwu_y is None:
                    print("未检测到 renwu，停止奔跑")
                    if direction:
                        self.utils.com_object.KeyUp(direction)
                    break

                print(f"renwu: ({renwu_x}, {renwu_y}), 目标: ({target_x}, {target_y})")
                dx = abs(renwu_x - target_x)
                dy = abs(renwu_y - target_y)

                new_direction = 'Right' if target_x > renwu_x else 'Left'
                if direction != new_direction:
                    if direction:
                        self.utils.com_object.KeyUp(direction)
                    self.utils.run(new_direction, random.uniform(0.1311, 0.1511))
                    time.sleep(random.uniform(0.01011, 0.03011))
                    direction = new_direction

                if dx <= 100 and dy <= 50:
                    self.utils.com_object.KeyUp(direction)
                    print("到达目标位置，松开方向键")
                    return True
                time.sleep(0.05)
        return False

    def face_monster(self, renwu_x, monster_x):
        direction = 'Right' if monster_x > renwu_x else 'Left'
        self.utils.run(direction, random.uniform(0.1311, 0.1511))
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

    def _attack_monster(self, frame, monster_x, monster_y, is_boss=False):
        try:
            self.utils.activate_window(gw.getWindowsWithTitle("地下城与勇士：创新世纪")[0])
            print("游戏窗口已激活")
        except Exception as e:
            print(f"激活窗口失败: {e}")

        renwu_x, renwu_y = self.get_positions(cv2.cvtColor(frame, cv2.COLOR_BGRA2GRAY))
        if renwu_x is not None and renwu_y is not None:
            print(f"renwu 初始位置: ({renwu_x}, {renwu_y})")
            self.move_to_target(monster_x, monster_y)
        else:
            print("初始未检测到 renwu，但因检测到怪物，继续尝试移动并攻击")

        with mss.mss() as sct:
            while True:
                screenshot = sct.grab(region)
                gray_frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_BGRA2GRAY)
                renwu_x, renwu_y = self.get_positions(gray_frame)
                if renwu_x is not None and renwu_y is not None:
                    self.face_monster(renwu_x, monster_x)
                    print(f"renwu 当前位置: ({renwu_x}, {renwu_y})，开始攻击")
                else:
                    print("未检测到 renwu，默认朝怪物方向攻击")

                skill_count = random.randint(2, 3)
                print(f"计划释放 {skill_count} 个技能")
                for i in range(skill_count):
                    qianjin_locations = self.utils.detect_template(gray_frame, self.monsters['qianjin']['template'])
                    if qianjin_locations:
                        print("检测到 qianjin，表示小怪已死，立即停止攻击")
                        return True
                    skill_key = random.choice(self.skill_keys)
                    print(f"释放技能 {skill_key} (第 {i+1}/{skill_count})")
                    self.utils.key_press(skill_key)
                    time.sleep(random.uniform(0.1011, 0.1511))
                    screenshot = sct.grab(region)
                    gray_frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_BGRA2GRAY)

                qianjin_locations = self.utils.detect_template(gray_frame, self.monsters['qianjin']['template'])
                if qianjin_locations:
                    print("检测到 qianjin，表示小怪已死，立即停止攻击")
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

                renwu_x, renwu_y = self.get_positions(gray_frame)
                if renwu_x is None or renwu_y is None:
                    print("一轮攻击后未检测到 renwu，随机移动以尝试脱离遮挡")
                    direction = random.choice([37, 39])
                    self.utils.key_long_press(direction, random.uniform(0.4011, 0.6011))
                    time.sleep(random.uniform(0.4011, 0.6011))
