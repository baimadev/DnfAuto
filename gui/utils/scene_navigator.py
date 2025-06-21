import os
import random
import sys
import time
from time import sleep

import cv2
import pygetwindow as gw

from gui.keybord.keyboard_util import WyhkmCOM
from ocr.ocr_util import OcrUtil


def resource_path(relative_path):
    """获取资源的绝对路径，适用于开发和 PyInstaller"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

# 游戏区域和随机延迟定义
region = {'left': 0, 'top': 0, 'width': 1700, 'height': 956}
random1_time = round(random.uniform(0.1311, 0.1511), 4)
random5_time = round(random.uniform(0.4011, 0.6011), 4)
random6_time = round(random.uniform(2.0111, 2.3011), 4)


class SceneNavigator:
    def __init__(self, game_title="地下城与勇士：创新世纪"):
        self.game_title = game_title
        self.utils = WyhkmCOM()
        self.templates = {
            'sailiya': cv2.imread(resource_path('image/sailiya.png'), 0),
            'shenyuan': cv2.imread(resource_path('image/shenyuan.png'), 0),
            'fenjieji': cv2.imread(resource_path('image/fenjieji.png'), 0),
            'shenyuan_xuanze': cv2.imread(resource_path('image/shenyuan_xuanze.png'), 0),
            'zhongmochongbaizhe': cv2.imread(resource_path('image/zhongmochongbaizhe.png'), 0),
            'youxicaidan': cv2.imread(resource_path('image/youxicaidan.png'), 0),
            'shijieditu': cv2.imread(resource_path('image/shijieditu.png'), 0),
            'yincangshangdian': cv2.imread(resource_path('image/yincangshangdian.png'), 0),
            'xuanzejuese': cv2.imread(resource_path('image/xuanzejuese.png'), 0),
            'xuanzejuese_jiemian': cv2.imread(resource_path('image/xuanzejuese_jiemian.png'), 0)
        }
        for key, template in self.templates.items():
            if template is None:
                print(f"模板加载失败: {key} (路径: {resource_path(f'image/{key}.png')})")
            else:
                print(f"模板加载成功: {key}, 尺寸: {template.shape}")
        if any(t is None for t in self.templates.values()):
            raise ValueError("无法加载模板图像，请检查路径！")
        self.last_right_press_time = 0
        self.right_key_duration = 5
        self.right_key_active = False
        self.last_shenyuan_click_time = 0
        self.shenyuan_click_cooldown = 3
        self.clicked_youxicaidan = False
        self.clicked_shijieditu = False
        # 点击世界地图 选择深渊
        self.choice_map = False
        # 进入地下城 选择深渊
        self.is_underground_choice_map = False
        self.ocr = OcrUtil()

    def move_to_shenyuan_map(self, frame, gray_frame, frame_array = None):
        game_window = gw.getWindowsWithTitle(self.game_title)[0]
        is_in_map = False

        # 检测到在赛利亚房间
        # 检测场景
        # 打开游戏菜单
        sailiya_locations = self.ocr.check_text_exist(target="赛丽亚", image_path=frame_array)
        if sailiya_locations is not None:
            print("检测到sailiya")
            if not self.clicked_youxicaidan:
                self.utils.key_press("ESC")
                print(f"点击菜单")
                self.clicked_youxicaidan = True
                is_in_map = False
                return is_in_map

        # 已打开游戏菜单
        # 点击世界地图
        if self.clicked_youxicaidan and not self.clicked_shijieditu:
            shijieditu_result = self.ocr.check_text_exist(target="世界地图", image_path=frame_array)
            print(f"检测到word map: {shijieditu_result}")
            if shijieditu_result is not None:
                self.utils.activate_window(game_window)
                x_center, y_center = shijieditu_result
                self.utils.click(x_center,y_center, "left")
                print(f"点击word map")
                self.clicked_shijieditu = True
                is_in_map = False
            else:
                self.clicked_shijieditu = False

        # 打开了世界地图
        # 点击深渊
        if self.clicked_shijieditu and not self.choice_map:
            zmcbz = self.ocr.check_text_exist(target="终末崇拜者", image_path=frame_array)
            if zmcbz is not None:
                self.utils.activate_window(game_window)
                x_center, y_center = zmcbz
                self.utils.click(x_center,y_center, "left")
                print(f"点击word-map-shenyuan: {zmcbz}")
                self.choice_map = True
                return False

        # 检测是否在跌宕群岛
        sne = self.ocr.check_text_exist(target="赛尼尔", image_path=frame_array)
        if sne is not None:
            print(f"检测到已在shenyuan门口")
            self.utils.activate_window(game_window)
            # 点击跌宕群岛
            ddqd = self.ocr.check_text_exist(target="群岛", image_path=frame_array)
            if ddqd is not None:
                x_center, y_center = ddqd
                self.utils.click(x_center, y_center, "right")
                print(f"点击diedangqd {ddqd}")
                is_in_map = False
                return is_in_map
            else:
                print(f"未检测到diedangqd")

        # 检测是否在Underground
        shenyuan_xuanze_locations = self.utils.detect_template(gray_frame, self.templates['shenyuan_xuanze'])
        if shenyuan_xuanze_locations:
            print("检测到shenyuan选择")
            self.utils.click(1089,738, "left")
            is_in_map = True

        return is_in_map
