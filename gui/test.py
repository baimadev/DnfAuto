import cv2
import numpy as np

template = cv2.imread("path_to_sailiya.png", 0)
screen = cv2.imread("path_to_current_screen.png", 0)

result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
threshold = 0.7
locations = np.where(result >= threshold)

print("匹配结果：", locations)
