import random
import time
from time import sleep

import cv2
import mss
import numpy as np
import pygetwindow as gw
from ultralytics import YOLO

from gui.keybord.keyboard_util import WyhkmCOM
from gui.utils.monster_attack import MonsterAttack
from gui.utils.scene_navigator import resource_path, region
from gui.utils.yolo_model_util import YoloModelUtil, DetectionTarget


class MonsterFighterA:
    def __init__(self,gui):
        self.utils = WyhkmCOM()
        self.monsters = {
            'small_monster': {'action': self.attack_small_or_elite, 'type': 'small'},
            'elite_monster': {'template': cv2.imread(resource_path('image/elite_monster.png'), 0),
                              'action': self.attack_small_or_elite, 'type': 'elite'},
            'boss': {'action': self.attack_boss, 'type': 'boss'},
            'zhongmochongbaizhe': {'template': cv2.imread(resource_path('image/zhongmochongbaizhe.png'), 0),
                                   'type': 'map'}
        }

        self.retry_button_template = cv2.imread(resource_path('image/retry_button.png'), 0)
        if self.retry_button_template is None:
            print("加载失败: retry_button (路径: image/retry_button.png)")
        for name, data in self.monsters.items():
            if 'template' in data:
                if data['template'] is None:
                    print(f"加载失败: {name} (路径: image/{name}.png)")
                else:
                    height, width, _ = data['template'].shape
                    print(f"模板加载成功: {name}, 尺寸: {width}x{height}")
        if any('template' in m and m['template'] is None for m in self.monsters.values()):
            raise ValueError("无法加载模板图像，请检查路径！")
        self.skill_keys = ['a', 's', 'd', 'f', 'g', 'h', 'q', 'w', 'e', 'r', 't']
        self.boss_skill = 'y'
        self.boss_dead = False
        self.shifoujixu_detected_time = None
        self.gui = gui
        self.attacker = MonsterAttack(self.monsters, self.skill_keys, gui)
        self.last_display_time = 0
        self.has_applied_buff = False  # 新增：buff 状态变量
        self.repeat_count = 0
        self.last_execute_time = 0
        self.yolo_util = YoloModelUtil()

    def run_to_qianjin(self, frame, x1, y1, x2, y2):
        game_window = gw.getWindowsWithTitle("地下城与勇士：创新世纪")[0]
        self.utils.activate_window(game_window)
        print(f"检测到前进，开始向右")
        self.attacker.move_towards_stop_on_monster("right")

    def attack_small_or_elite(self, frame, x1, y1, x2, y2):
        print("attack_small_or_elite")
        should_run_to_qianjin = self.attacker.attack_small_or_elite(frame, x1, y1, x2, y2)
        if should_run_to_qianjin:
            print(" attack_small_or_elite should_run_to_qianjin")
            self.run_to_qianjin(frame, x1, y1, x2, y2)

    def attack_boss(self, frame, x1, y1, x2, y2):
        print("attack_boss")
        should_run_to_qianjin = self.attacker.attack_boss(frame, x1, y1, x2, y2)
        if should_run_to_qianjin:
            print(" attack_boss should_run_to_qianjin")
            self.run_to_qianjin(frame, x1, y1, x2, y2)

    def is_gray(self, roi):
        mean_color = np.mean(roi, axis=(0, 1))
        b, g, r = mean_color
        color_diff = max(abs(r - g), abs(g - b), abs(b - r))
        roi_hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        mean_hsv = np.mean(roi_hsv, axis=(0, 1))
        saturation = mean_hsv[1]
        print(f"按钮颜色 - RGB: [{b:.1f}, {g:.1f}, {r:.1f}], 差异: {color_diff:.1f}, 饱和度: {saturation:.1f}")
        return color_diff < 10 and saturation < 100

    def pickup_boss_drops(self, frame, x1, y1, x2, y2):
        print("检测到 是否继续，Boss 已死，开始拾取")
        self.utils.release_keyboard()
        self.attacker.current_direction = None
        game_window = gw.getWindowsWithTitle("地下城与勇士：创新世纪")[0]
        self.utils.activate_window(game_window)
        self.utils.key_press('Tab')
        print("按下 tab 键聚集掉落物品")
        self.utils.key_long_press("x", 3000)
        print("拾取完成")

        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2GRAY)
        retry_locations = self.utils.detect_template(gray_frame, self.retry_button_template)
        retry_button_gray = False
        for rx1, ry1, rx2, ry2 in retry_locations:
            padding = 5
            roi = frame[ry1 + padding:ry2 - padding, rx1 + padding:rx2 - padding]
            if roi.size == 0:
                roi = frame[ry1:ry2, rx1:rx2]
            retry_button_gray = self.is_gray(roi)
            print(f"再次挑战按钮状态: {'灰色（不可用）' if retry_button_gray else '彩色（可用）'}")
            break

        if not retry_button_gray:
            print("再次挑战按钮可用，点击重试")
            self.utils.key_press('F10')  # F10
            self.boss_dead = False
            print("已离开 Boss 房间")
        else:
            print("再次挑战按钮为灰色，当前角色刷图完成，退出并切换角色")
            self.utils.key_press("F12")  # F12
            return True
        time.sleep(random.uniform(0.4011, 0.6011))
        return False

    def process_frame(self, frame, gray_frame):
        start_time = time.time()
        detected_monsters = []
        image_array = self.yolo_util.capture_screen()
        yolo_results = self.yolo_util.predict(image_array, False)
        for result in yolo_results:
            for box in result.boxes:
                confidence = box.conf.item()
                if confidence < 0.6:
                    continue
                cls_name = result.names[int(box.cls)]
                if cls_name in ['boss']:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    detected_monsters.append((cls_name, x1, y1, x2, y2))

        yolo_results2 = self.yolo_util.predict(image_array)
        for result in yolo_results2:
            for box in result.boxes:
                confidence = box.conf.item()
                if confidence < 0.6:
                    continue
                cls_name = result.names[int(box.cls)]
                print(f"yolo role {cls_name}")
                if cls_name in ['forward', 'role', 'sfjx', 'monster', 'smsd', 'can_hen']:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    detected_monsters.append((cls_name, x1, y1, x2, y2))

        for monster_name, monster_data in self.monsters.items():
            if 'template' in monster_data and monster_data['template'] is not None:
                locations = self.utils.detect_template(gray_frame, monster_data['template'], threshold=0.8)
                print(f"检测 {monster_name}，找到 {len(locations)} 个匹配，位置: {locations}")
                for x1, y1, x2, y2 in locations:
                    detected_monsters.append((monster_name, x1, y1, x2, y2))

        print(f"Process frame time: {time.time() - start_time:.3f} seconds")
        return detected_monsters

    def detect_smsd(self, frame, x1, y1, x2, y2):
        start_time = time.time()
        last_check_time = 0
        while not self.gui.stop_event.is_set():
            current_time = time.time()
            if current_time - last_check_time < 0.1:
                time.sleep(0.01)  # 短暂休眠避免CPU过载
                continue
            last_check_time = current_time

            if self.yolo_util.check_exist(DetectionTarget.SMSD):
                cx, cy = self.yolo_util.get_positions(DetectionTarget.SMSD, frame)
                # 购买残痕
                self.utils.release_keyboard()
                time.sleep(random.uniform(0.1011, 0.1511))
                self.utils.move_to(cx, cy)
                time.sleep(random.uniform(0.1011, 0.1511))
                self.utils.left_double_click()
                continue
            else:
                # 退出商店
                self.utils.release_keyboard()
                self.utils.key_press("ESC")
                time.sleep(random.uniform(0.1011, 0.1511))
                break


    def fight_monsters(self, frame, gray_frame):
        start_time = time.time()
        detected_monsters = self.process_frame(frame, gray_frame)
        should_pickup = False


        print(f"检测到的所有怪物: {detected_monsters}")

        # 处理是否继续
        shifoujixu_detected = any(monster_name == 'sfjx' for monster_name, _, _, _, _ in detected_monsters)
        if shifoujixu_detected:
            self.last_execute_time = time.time()
            for monster_name, x1, y1, x2, y2 in detected_monsters:
                if monster_name == 'sfjx':
                    print("检测到是否继续")
                    self.utils.release_keyboard()
                    self.attacker.current_direction = None
                    self.pickup_boss_drops(frame, x1, y1, x2, y2)
                    return frame, should_pickup

        for monster_name, x1, y1, x2, y2 in detected_monsters:
            if monster_name == 'zhongmochongbaizhe':
                continue

            print(f"检测到 {monster_name}")

            if monster_name == 'forward':
                #检测到前进
                print("检测到前进")
                self.run_to_qianjin(frame, x1, y1, x2, y2)
                self.last_execute_time = time.time()
            elif monster_name == 'boss':
                #检测到boss
                self.attack_boss(frame, x1, y1, x2, y2)
                self.last_execute_time = time.time()
            elif monster_name == 'monster':
                #检测到小怪
                self.attack_small_or_elite(frame, x1, y1, x2, y2)
                self.last_execute_time = time.time()
            elif monster_name == 'smsd':
                #检测到神秘商店
                self.detect_smsd(frame, x1, y1, x2, y2)
                self.last_execute_time = time.time()

        readable = time.strftime("%H:%M:%S", time.localtime(self.last_execute_time))
        print(f"last execute {readable}")
        current_time = time.time()
        current_str= time.strftime("%H:%M:%S", time.localtime(current_time))
        print(f"last execute {current_str}")

        time_diff = current_time - self.last_execute_time
        if time_diff > 4:
            print(f"上次操作已过了 {time_diff:.2f} 秒，触发随机移动")
            self.attacker.random_move()

        current_time = time.time()
        if current_time - self.last_display_time >= 0.033:
            self.last_display_time = current_time

        print(f"Fight monsters time: {time.time() - start_time:.3f} seconds")
        return frame, should_pickup


