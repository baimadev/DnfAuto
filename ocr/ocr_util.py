from paddleocr import PaddleOCR
from PIL import Image
import numpy as np
from draw_ocr import draw_boxes_on_image
import pprint
import time

class SingletonMeta(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(SingletonMeta, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class OcrUtil(metaclass=SingletonMeta):
    def __init__(self):
        self.ocr = PaddleOCR(lang="ch"
                             # , ocr_version="PP-OCRv5"
                             , ocr_version="PP-OCRv4"
                             , use_doc_orientation_classify=False
                             , use_doc_unwarping=False
                             , use_textline_orientation=False
                             # , text_detection_model_dir="C:/Users/Administrator/.paddlex/official_models/PP-OCRv5_server_det"
                             # , text_recognition_model_dir="C:/Users/Administrator/.paddlex/official_models/PP-OCRv5_server_rec"
                             )

    def checkTextExist(self, target, image_path):
        result = self.ocr.predict(image_path)
        for res in result:
            texts = res.get('rec_texts', [])
            boxes = res.get('rec_boxes', [])
            for text, box in zip(texts, boxes):
                if target in text:
                    return box
        return None

    def check_multi_text_exist(self, target_list, image_path):
        result = self.ocr.predict(image_path)
        check_result = {}
        for res in result:
            texts = res.get('rec_texts', [])
            boxes = res.get('rec_boxes', [])
            for text, box in zip(texts, boxes):
                for target in target_list:
                    if target in text:
                        check_result[target] = box
        return check_result

    def ocr_test(self,result):
        if result and isinstance(result, list):
            res_dict = result[0]

            texts = res_dict.get('rec_texts', [])
            scores = res_dict.get('rec_scores', [])
            boxes = res_dict.get('rec_boxes', [])

            image = Image.open('test.png').convert("RGB")
            image_with_boxes = draw_boxes_on_image(image=image, boxes=boxes)
            image_with_boxes.show()
            image_with_boxes.save("result_boxes.jpg")

            # 遍历所有识别到的文本块
            for idx in range(len(texts)):
                text = texts[idx]
                score = scores[idx]
                box = boxes[idx]
                print(f"文本块 {idx + 1}: {text}")
                print(f"置信度: {score:.4f}")
                print(f"文本框坐标: {box.tolist()}")
                print("-" * 30)


if __name__ == "__main__":
    ocr_util = OcrUtil()
    start_time = time.time()
    result = ocr_util.check_multi_text_exist(["修理装备","德利拉"], "test.png")
    end_time = time.time()
    print(f"OCR 检测耗时: {end_time - start_time:.2f} 秒")
    if not result:
        print("未找到目标文本")
    else:
        np.set_printoptions(threshold=1_000_000_000, suppress=True)
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(result)

