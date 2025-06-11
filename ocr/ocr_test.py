from paddleocr import PaddleOCR
from PIL import Image
import numpy as np
from draw_ocr import draw_boxes_on_image
import pprint

# 初始化（可配置参数）
ocr = PaddleOCR(
    use_textline_orientation=True,    # 启用方向分类
    lang="ch",             # 中文识别
)

# 执行 OCR 并获取可视化结果
img_path = "test.png"
result = ocr.predict(img_path)
if result and isinstance(result, list):
    res_dict = result[0]

    # 提取识别结果
    texts = res_dict.get('rec_texts', [])
    scores = res_dict.get('rec_scores', [])
    boxes = res_dict.get('rec_boxes', [])

    # 加载原始图像
    image = Image.open('test.png').convert("RGB")

    # result_image = draw_ocr(image, boxes, texts, scores)
    # pil_image = Image.fromarray(result_image)
    # pil_image.show()
    # pil_image.save("result.png")

    image_with_boxes = draw_boxes_on_image(image=image, boxes=boxes)
    image_with_boxes.show()
    image_with_boxes.save("result_boxes.jpg")

    #pprint.pprint(result)

    # # 遍历所有识别到的文本块
    for idx in range(len(texts)):
        text = texts[idx]
        score = scores[idx]
        box = boxes[idx]
        print(f"文本块 {idx + 1}: {text}")
        print(f"置信度: {score:.4f}")
        print(f"文本框坐标: {box.tolist()}")
        print("-" * 30)


