"""
LangChain智能代理系统主入口
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from UI.ui_interface import ui_interface

if __name__ == "__main__":
    print("正在启动铜合金性能预测智能代理系统...")
    try:
        ui_interface.run_interactive_mode()
    except Exception as e:
        print(f"启动失败：{e}")
        sys.exit(1)
