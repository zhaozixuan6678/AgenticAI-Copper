import os
from pathlib import Path

# 模型保存路径
MODEL_DIR = Path(os.path.dirname(os.path.abspath(__file__))) / "models"
print(MODEL_DIR)
