from gui.keybord.wuya_test import WyhkmCOM

# 方法1：使用PyTorch
import torch
print(torch.version.cuda)  # 输出如"11.8"

if __name__ == "__main__":

    # 使用示例
    try:
        # 初始化时会自动完成所有准备工作
        wyhkm = WyhkmCOM()

        wyhkm.key_press(65)  # 键码：65（字母 'A'）
        wyhkm.key_press("A")  # 键名：'A'
        wyhkm.key_press("X")  # 功能键 F1
        wyhkm.key_press("Enter")  # 回车键

        wyhkm.key_press("Ctrl+V")  # 复制
        # 获取鼠标位置
        pos = wyhkm.get_cursor_pos()
        print(f"当前鼠标位置: {pos}")

    except Exception as e:
        print(f"程序运行出错: {e}")