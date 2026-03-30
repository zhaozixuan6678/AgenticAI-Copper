import sys
import os
from pathlib import Path

# 确保导入路径正确
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from agent_core import LangChainAgent

# 实例化 Agent
agent = LangChainAgent()

# 定义训练数据路径
train_data_path = "/Users/zixuanzhao/Desktop/MKG/Agent/Feature.xlsx"

# 调用模型训练工具
print(f"开始训练模型，使用数据: {train_data_path}")
try:
    result = agent._train_models(
        train_path=train_data_path,
        predict_path="dummy_predict.xlsx",  # 占位符
        param_path="dummy_param.xlsx",      # 占位符
        output_path="training_output.xlsx"  # 占位符
    )
    print("模型训练结果:")
    print(result)
except Exception as e:
    print(f"模型训练失败: {e}")
