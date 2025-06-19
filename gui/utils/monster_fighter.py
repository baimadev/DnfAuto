import random
import time

import cv2
import mss
import numpy as np
import pygetwindow as gw

from gui.keybord.keyboard_util import WyhkmCOM
from gui.utils.monster_attack import MonsterAttack
from gui.utils.scene_navigator import resource_path, region


class MonsterFighterA:
    def __init__(self):
        self.utils = WyhkmCOM()
        self.monsters = {
            'small_monster': {'action': self.attack_small_or_elite, 'type': 'small'},
            'elite_monster': {'template': cv2.imread(resource_path('image/elite_monster.png'), 0),
                              'action': self.attack_small_or_elite, 'type': 'elite'},
            'boss': {'action': self.attack_boss, 'type': 'boss'},
            'qianjin': {'template': cv2.imread(resource_path('image/qianjin.png'), 0), 'action': self.run_to_qianjin,
                        'type': 'qianjin'},
            'renwu': {'template': cv2.imread(resource_path('image/renwu.png'), 0), 'type': 'player'},
            'shifoujixu': {'template': cv2.imread(resource_path('image/shifoujixu.png'), 0),
                           'action': self.pickup_boss_drops, 'type': 'pickup'},
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
        self.qianjin_reached = False
        self.boss_dead = False
        self.shifoujixu_detected_time = None
        self.attacker = MonsterAttack(self.utils, resource_path('models/best15.pt'), self.monsters, self.skill_keys)
        self.last_display_time = 0
        self.has_applied_buff = False  # 新增：buff 状态变量

    def run_to_qianjin(self, frame, x1, y1, x2, y2):
        game_window = gw.getWindowsWithTitle("地下城与勇士：创新世纪")[0]
        self.utils.activate_window(game_window)
        qianjin_x = x1 + (x2 - x1) // 2
        qianjin_y = y1 + (y2 - y1) // 2
        target_x = 1060
        target_y = 369

        if qianjin_x < target_x:
            direction = 39  # 向右
        else:
            direction = 37  # 向左

        print(
            f"检测到 qianjin，开始奔向固定坐标 (1060, 369)，方向: {'right' if direction == 39 else 'left' if direction == 37 else 'up' if direction == 38 else 'down'}")
        self.attacker.move_to_fixed_point(target_x=1060, target_y=369, direction=direction)
        self.qianjin_reached = True
        print("到达固定坐标或检测到小怪/Boss，停止奔跑")

    def attack_small_or_elite(self, frame, x1, y1, x2, y2):
        should_run_to_qianjin = self.attacker.attack_small_or_elite(frame, x1, y1, x2, y2)
        if should_run_to_qianjin:
            self.run_to_qianjin(frame, x1, y1, x2, y2)

    def attack_boss(self, frame, x1, y1, x2, y2):
        should_run_to_qianjin = self.attacker.attack_boss(frame, x1, y1, x2, y2)
        if should_run_to_qianjin:
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
        print("检测到 shifoujixu.png，Boss 已死，开始拾取")
        if self.attacker.current_direction is not None:
            self.utils.release_key(self.attacker.current_direction)
            self.attacker.current_direction = None
            print("检测到 shifoujixu，强制停止奔跑")
        game_window = gw.getWindowsWithTitle("地下城与勇士：创新世纪")[0]
        self.utils.activate_window(game_window)
        self.utils.key_press('Tab')
        print("按下 tab 键聚集掉落物品")
        start_time = time.time()
        while time.time() - start_time < 3:
            self.utils.key_long_press("x", random.uniform(0.1311, 0.1511))
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
            self.qianjin_reached = False
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
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGRA2RGB)
        yolo_results = self.attacker.yolo_model.predict(frame_rgb)
        for result in yolo_results:
            for box in result.boxes:
                cls_name = result.names[int(box.cls)]
                if cls_name in ['small_monster', 'boss']:
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

    def fight_monsters(self, frame, gray_frame):
        start_time = time.time()
        detected_monsters = self.process_frame(frame, gray_frame)
        should_pickup = False
        in_zhongmochongbaizhe = False
        shifoujixu_confirmed = False

        print(f"检测到的所有怪物: {detected_monsters}")

        in_zhongmochongbaizhe = any(
            monster_name == 'zhongmochongbaizhe' for monster_name, _, _, _, _ in detected_monsters)
        if not in_zhongmochongbaizhe:
            print("未检测到 zhongmochongbaizhe 地图，跳过怪物检测")
            return frame, False
        else:
            print("检测到 zhongmochongbaizhe 地图，继续处理怪物逻辑")

        shifoujixu_detected = any(monster_name == 'shifoujixu' for monster_name, _, _, _, _ in detected_monsters)
        if shifoujixu_detected:
            for monster_name, x1, y1, x2, y2 in detected_monsters:
                if monster_name == 'shifoujixu':
                    print("检测到 shifoujixu，停止所有刷怪操作并休眠 1.5 秒")
                    if self.attacker.current_direction is not None:
                        self.utils.com_object.KeyUp(self.attacker.current_direction)
                        self.attacker.current_direction = None
                        print("已释放方向键，停止移动")

                    sleep_start = time.time()
                    shifoujixu_start_time = None
                    shifoujixu_duration = 0.0
                    with mss.mss() as sct:
                        while time.time() - sleep_start < 1.5:
                            screenshot = sct.grab(region)
                            temp_gray_frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_BGRA2GRAY)
                            shifoujixu_locations = self.utils.detect_template(temp_gray_frame,
                                                                              self.monsters['shifoujixu']['template'],
                                                                              threshold=0.8)
                            if shifoujixu_locations:
                                if shifoujixu_start_time is None:
                                    shifoujixu_start_time = time.time()
                                    print(f"休眠期间首次检测到 shifoujixu，位置: {shifoujixu_locations[0]}")
                                shifoujixu_duration = time.time() - shifoujixu_start_time
                                print(f"shifoujixu 持续检测时间: {shifoujixu_duration:.2f} 秒")
                            else:
                                if shifoujixu_start_time is not None:
                                    print(f"shifoujixu 检测中断，持续时间: {shifoujixu_duration:.2f} 秒")
                                    shifoujixu_start_time = None
                            time.sleep(0.05)

                    if shifoujixu_duration >= 0.5:
                        print("shifoujixu 在 1.5 秒内持续存在超过 0.5 秒，确认 Boss 已死，开始拾取")
                        should_pickup = self.monsters['shifoujixu']['action'](frame, x1, y1, x2, y2)
                        shifoujixu_confirmed = True
                    else:
                        print("shifoujixu 在 1.5 秒内持续存在少于 0.5 秒，判定为误检测，继续刷怪")
                    break

        if shifoujixu_confirmed:
            print("shifoujixu 处理完成，跳过其他怪物操作")
            return frame, should_pickup

        for monster_name, x1, y1, x2, y2 in detected_monsters:
            if monster_name == 'zhongmochongbaizhe':
                continue

            color = (255, 255, 0) if monster_name in ['small_monster', 'elite_monster'] else (
                255, 0, 0) if monster_name == 'boss' else (0, 255, 255) if monster_name == 'qianjin' else (0, 0, 255)
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, f"{monster_name}: ({x1},{y1})", (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            print(f"检测到 {monster_name}")

            if monster_name == 'qianjin':
                self.monsters[monster_name]['action'](frame, x1, y1, x2, y2)
            elif monster_name in ['small_monster', 'elite_monster', 'boss']:
                if self.qianjin_reached and not any(m[0] == 'qianjin' for m in detected_monsters):
                    print("qianjin 消失，进入打怪模式")
                    self.monsters[monster_name]['action'](frame, x1, y1, x2, y2)
                else:
                    self.monsters[monster_name]['action'](frame, x1, y1, x2, y2)

        current_time = time.time()
        if current_time - self.last_display_time >= 0.033:
            self.last_display_time = current_time

        print(f"Fight monsters time: {time.time() - start_time:.3f} seconds")
        return frame, should_pickup
