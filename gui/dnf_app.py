# dnf_app.py
import os
import random
import sys
import threading
import time
import tkinter as tk
from ctypes import *

import cv2
import mss
import numpy as np
import pygetwindow as gw
from ultralytics import YOLO

from dnf_gui import DnfGUI
from gui.task.task_manager import TaskManager
from gui.utils.monster_fighter import MonsterFighterA
from gui.utils.scene_navigator import SceneNavigator, region
from gui.utils.tkinter_overlay import TkinterOverlay


# 主程序逻辑
class DnfApp:
    def __init__(self, root):
        windll.user32.SetProcessDPIAware()
        self.model_ready = False
        threading.Thread(target=self._load_model, daemon=True).start()

        self.root = root
        # 初始化 GUI
        self.gui = DnfGUI(root, self.start_detection, self.stop_detection)
        # 初始化 Tkinter 覆盖层
        self.overlay = TkinterOverlay()
        # 初始化任务管理器
        self.manager = TaskManager()
        #self.manager.register_task(DetextNextMapTask(self.gui, self.model))
        #self.manager.register_task(DetextChallengeAgain(self.gui))

        self.navigator = SceneNavigator()
        self.fighter = MonsterFighterA()


    def _load_model(self):
        try:
            if getattr(sys, 'frozen', False):
                base_path = sys._MEIPASS
            else:
                base_path = os.path.dirname(__file__)
            model_path = os.path.join(base_path, '../runs', 'detect', 'train', 'weights', 'best.pt')
            self.model = YOLO(model_path)
            self.model_ready = True
            self.gui.log("YOLO模型加载完成")
        except Exception as e:
            self.gui.log(f"模型加载失败: {str(e)}")

    def start_detection(self):
        # self.manager.start_all()
        self.thread = threading.Thread(target=self.run_shenyuan_map, daemon=True)
        self.thread.start()
        self.gui.update_buttons(True)
        

    def stop_detection(self):
        # self.manager.stop_all()
        self.thread.join(timeout=2)
        cv2.destroyAllWindows()
        self.gui.update_buttons(False)
    
    def run_shenyuan_map(self):
        game_window = gw.getWindowsWithTitle("地下城与勇士：创新世纪")[0]
        game_window.moveTo(0, 0)
        self.navigator.utils.activate_window(game_window)
        time.sleep(1)

        self.total_roles = int(self.role_combo.currentText())
        self.current_role = 0

        with mss.mss() as sct:
            while not self.stop_event.is_set() and self.current_role < self.total_roles:
                try:
                    screenshot = sct.grab(region)
                    frame = np.array(screenshot)
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
                    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                    in_town = self.navigator.move_to_shenyuan_map(frame, gray_frame)
                    zhongmo_locations = self.navigator.utils.detect_template(gray_frame, self.navigator.templates['zhongmochongbaizhe'], threshold=0.8)
                    self.gui.log(f"检测到 zhongmochongbaizhe: {len(zhongmo_locations)} 个位置")
                    in_monster_map = bool(zhongmo_locations)

                    if in_monster_map:
                        self.gui.log("检测到 zhongmochongbaizhe.png，进入刷怪模式")
                        yincangshangdian_locations = self.navigator.utils.detect_template(gray_frame, self.navigator.templates['yincangshangdian'])
                        if yincangshangdian_locations:
                            self.gui.log("检测到 yincangshangdian.png，暂停刷怪操作")
                            if self.fighter.attacker.current_direction is not None:
                                self.navigator.utils.release_key(self.fighter.attacker.current_direction)
                                self.fighter.attacker.current_direction = None
                                self.gui.log("已释放方向键，暂停移动")
                            self.navigator.utils.activate_window(game_window)
                            self.navigator.utils.click(373, 39, "left")
                            self.gui.log("已点击隐藏商店按钮 (373, 39)")
                            time.sleep(1)
                            self.gui.log("隐藏商店操作完成，继续刷怪")

                        frame, should_pickup = self.fighter.fight_monsters(frame, gray_frame)
                        if should_pickup:
                            self.current_role += 1
                            self.gui.log(f"角色 {self.current_role}/{self.total_roles} 已刷完，开始切换角色")
                            self.switch_role(game_window, sct)
                    elif in_town:
                        self.gui.log("在城镇，继续导航")
                    else:
                        self.gui.log("未检测到明确场景，跳过刷怪逻辑")

                    self.frame_queue.put(frame)
                    time.sleep(0.033)
                except Exception as e:
                    self.gui.log(f"运行中发生错误: {str(e)}")
                    import traceback
                    traceback.print_exc()
                    time.sleep(1)

    def switch_role(self, game_window, sct):
        time.sleep(3)
        screenshot = sct.grab(region)
        gray_frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_BGRA2GRAY)
        youxicaidan_locations = self.navigator.utils.detect_template(gray_frame, self.navigator.templates['youxicaidan'])
        self.gui.log(f"检测到游戏菜单: {len(youxicaidan_locations)} 个位置")
        for yx1, yy1, yx2, yy2 in youxicaidan_locations:
            click_x = yx1 + (yx2 - yx1) // 2
            click_y = yy1 + (yy2 - yy1) // 2
            self.gui.log(f"检测到 youxicaidan.png，点击坐标 ({click_x}, {click_y})")
            self.navigator.utils.activate_window(game_window)
            self.navigator.utils.click(click_x, click_y, "left")
            time.sleep(1)
            break
        else:
            self.gui.log("未检测到 youxicaidan.png，切换可能失败")

        screenshot = sct.grab(region)
        gray_frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_BGRA2GRAY)
        xuanzejuese_locations = self.navigator.utils.detect_template(gray_frame, self.navigator.templates['xuanzejuese'])
        self.gui.log(f"检测到选择角色按钮: {len(xuanzejuese_locations)} 个位置")
        for xx1, xy1, xx2, xy2 in xuanzejuese_locations:
            click_x = xx1 + (xx2 - xx1) // 2
            click_y = xy1 + (xy2 - xy1) // 2
            self.gui.log(f"检测到 xuanzejuese.png，点击坐标 ({click_x}, {click_y})")
            self.navigator.utils.activate_window(game_window)
            self.navigator.utils.click(click_x, click_y, "left")
            time.sleep(1)
            break
        else:
            self.gui.log("未检测到 xuanzejuese.png，切换可能失败")

        screenshot = sct.grab(region)
        gray_frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_BGRA2GRAY)
        xuanzejuese_jiemian_locations = self.navigator.utils.detect_template(gray_frame, self.navigator.templates['xuanzejuese_jiemian'])
        self.gui.log(f"检测到选择角色界面: {len(xuanzejuese_jiemian_locations)} 个位置")
        if xuanzejuese_jiemian_locations:
            self.gui.log("检测到 xuanzejuese_jiemian.png，切换角色")
            self.navigator.utils.key_press("Right")
            time.sleep(0.1)
            self.navigator.utils.key_press("Space")
            time.sleep(2)

            screenshot = sct.grab(region)
            gray_frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_BGRA2GRAY)
            sailiya_locations = self.navigator.utils.detect_template(gray_frame, self.navigator.templates['sailiya'])
            self.gui.log(f"检测到塞利亚: {len(sailiya_locations)} 个位置")
            if sailiya_locations:
                self.gui.log("检测到 sailiya.png，角色切换成功，重置状态")
                self.navigator.clicked_youxicaidan = False
                self.navigator.clicked_shijieditu = False
                self.fighter.qianjin_reached = False
                self.fighter.boss_dead = False
                self.fighter.has_applied_buff = False  # 重置 buff 状态
            else:
                self.gui.log("未检测到 sailiya.png，切换可能失败")
        else:
            self.gui.log("未检测到 xuanzejuese_jiemian.png，切换失败")

# 启动 GUI
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # 先隐藏主窗口
    # 显示加载中提示
    splash = tk.Toplevel()
    tk.Label(splash, text="初始化中...").pack()
    root.update()
    # 异步初始化
    def init_app():
        app = DnfApp(root)
        splash.destroy()
        root.deiconify()  # 显示主窗口
    threading.Thread(target=init_app, daemon=True).start()
    root.mainloop()