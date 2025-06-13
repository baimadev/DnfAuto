import tkinter as tk

class TkinterOverlay:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()  # 隐藏主窗口

        # 创建透明顶层窗口
        self.overlay = tk.Toplevel()
        self.overlay.overrideredirect(True)
        self.overlay.attributes("-topmost", True)
        self.overlay.attributes("-transparentcolor", "black")
        self.overlay.configure(bg='black')

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.overlay.geometry(f"{screen_width}x{screen_height}+0+0")

        # 创建 Canvas 用于绘图
        self.canvas = tk.Canvas(self.overlay, width=screen_width, height=screen_height,
                                bg='black', highlightthickness=0)
        self.canvas.pack()
        self.overlay.update()
        self.root.destroy()  # 关闭默认主窗口

    def clear_overlay(self):
        self.canvas.delete("all")
        self.overlay.update()

    def update_overlay(self, results , model):
        self.canvas.delete("all")  # 清空上一帧

        try:
            detections = results[0].boxes.data.cpu().numpy()
            if len(detections) > 0:
                for det in detections:
                    if det.shape[0] == 6:
                        x1, y1, x2, y2, conf, cls_id = det
                    elif det.shape[0] == 7:
                        _, x1, y1, x2, y2, conf, cls_id = det
                    else:
                        continue

                    label = model.names[int(cls_id)]
                    text = f"{label} {conf:.2f}"

                    # 绘制绿色矩形框
                    self.canvas.create_rectangle(x1, y1, x2, y2, outline="#00FF00", width=2)

                    # 标签背景
                    text_width = len(text) * 8
                    text_height = 16
                    self.canvas.create_rectangle(x1, y1 - text_height, x1 + text_width, y1,
                                                fill="#00FF00", outline="")

                    # 居中显示文本
                    self.canvas.create_text(x1 + 4, y1 - text_height + 2, text=text,
                                            fill="white", anchor="nw", font=("Arial", 10))

        except Exception as e:
            print(f"绘制错误: {e}")

        self.overlay.update()
