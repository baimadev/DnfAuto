# draw_ocr.py
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import math

def draw_boxes_on_image(image, boxes, color=(0, 255, 0), width=2):
    """
    在图像上绘制检测框（基于 [x1, y1, x2, y2] 格式的矩形框）

    参数:
        image: PIL.Image 对象（RGB格式）
        boxes: 文本框列表，每个 box 格式为 [x1, y1, x2, y2]
        color: 框的颜色 (R, G, B)
        width: 线宽

    返回:
        绘制完框的 PIL.Image 对象
    """
    draw = ImageDraw.Draw(image)

    for idx, box in enumerate(boxes):
        if len(box) != 4:
            print(f"[警告] 第 {idx + 1} 个 box 数据不合法（应为4个元素）: {box}")
            continue

        x1, y1, x2, y2 = box

        # 绘制矩形框
        draw.rectangle([x1, y1, x2, y2], outline=color, width=width)

    return image