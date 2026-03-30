"""
LangChain智能代理系统配置文件
"""

# 系统配置
SYSTEM_CONFIG = {
    "name": "铜合金性能预测智能代理系统",
    "version": "1.0.0",
    "description": "基于LangChain框架的铜合金性能预测智能代理",
    "author": "AI Assistant",
    "license": "MIT"
}

# 工具配置
TOOL_CONFIG = {
    "feature_engineering": {
        "enabled": True,
        "description": "将原始合金数据转换为机器学习特征",
        "input_format": "Excel文件",
        "output_format": "Excel文件"
    },
    "performance_prediction": {
        "enabled": True,
        "description": "预测铜合金的硬度、电导率和综合性能指标",
        "input_format": "合金成分和工艺参数",
        "output_format": "数值预测结果"
    },
    "model_training": {
        "enabled": True,
        "description": "训练和优化铜合金性能预测模型",
        "input_format": "训练数据和参数配置",
        "output_format": "训练好的模型和评估报告"
    }
}

# 意图识别配置
INTENT_CONFIG = {
    "confidence_threshold": 0.7,
    "max_retries": 3,
    "default_intent": "general_query"
}

# 性能预测模型配置
PREDICTION_CONFIG = {
    "hardness_model": "SVR",
    "ec_model": "CAT",
    "q3_model": "SVR",
    "feature_selection_strategy": "auto",
    "ensemble_enabled": True
}
