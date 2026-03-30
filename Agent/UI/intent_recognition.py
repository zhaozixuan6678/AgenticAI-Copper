"""
LangChain智能代理意图识别模块
负责解析用户自然语言指令，识别意图并选择合适的工具
使用LLM进行意图识别和参数提取
"""

import os
import json
from typing import Dict, Any, Optional, List
from langchain_core.language_models import BaseLanguageModel
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic.v1 import BaseModel, Field
from langchain_community.chat_models import ChatOpenAI
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class IntentRecognitionResult(BaseModel):
    """LLM返回的意图识别结果结构"""
    intent: str = Field(description="识别的意图，必须是以下之一：feature_engineering, performance_prediction, model_training, general_query")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="提取的参数字典")
    confidence: float = Field(default=0.0, description="识别置信度，0.0-1.0")


class IntentRecognizer:
    """基于LLM的意图识别器，用于解析用户自然语言指令"""
    
    def __init__(self):
        # 初始化LLM
        self.llm = ChatOpenAI(
            model_name="qwen/qwen3-max-thinking",
            temperature=0.3,
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            openai_api_base=os.getenv("OPENAI_API_BASE"),
            max_tokens=1024
        )
        
        # 定义意图识别提示词模板
        self.intent_prompt = PromptTemplate(
            template="""
You are a professional intent recognition assistant for copper alloy performance prediction system.
Please analyze the user's natural language instruction (which can be in English or Chinese) and return JSON format results according to the following requirements:

1. Identify the user's intent (intent), which must be one of the following four options:
   - feature_engineering: related to feature engineering, data transformation, feature extraction, etc.
   - performance_prediction: related to performance prediction, alloy performance estimation, hardness/conductivity prediction, etc.
   - model_training: related to model training, parameter optimization, model tuning, etc.
   - general_query: other general queries or system commands

2. Extract relevant parameters (parameters) based on the intent type:
   - For feature_engineering: extract input_path (input file path), output_path (output file path)
   - For performance_prediction: extract alloy_composition (alloy composition dictionary, e.g., {{"Cu": 90.5, "Al": 5.2}}), processing_params (processing parameters dictionary, e.g., {{"Temperature": 500, "Time": 8}}), processing_route (processing route string)
   - For model_training: extract train_path (training data path), param_path (parameter configuration path), etc.

3. Evaluate the recognition confidence (confidence), between 0.0-1.0

User instruction: {user_input}

Please return only JSON format results, do not include any other text.
""",
            input_variables=["user_input"]
        )
        
        # 创建输出解析器
        self.parser = JsonOutputParser(pydantic_object=IntentRecognitionResult)
    
    def recognize_intent(self, user_input: str) -> str:
        """使用LLM识别用户输入的意图"""
        try:
            # 构建链式调用
            chain = self.intent_prompt | self.llm | self.parser
            
            # 执行LLM调用
            result = chain.invoke({"user_input": user_input})
            
            # 返回意图
            return result.get("intent", "general_query")
            
        except Exception as e:
            print(f"LLM意图识别失败：{e}")
            # 备用方案：简单的关键词匹配
            user_input_lower = user_input.lower()
            # 中文关键词
            if "特征" in user_input_lower or "工程" in user_input_lower or "转换" in user_input_lower:
                return "feature_engineering"
            elif "预测" in user_input_lower or "性能" in user_input_lower or "硬度" in user_input_lower or "电导率" in user_input_lower:
                return "performance_prediction"
            elif "训练" in user_input_lower or "模型" in user_input_lower or "优化" in user_input_lower:
                return "model_training"
            # 英文关键词
            elif "feature" in user_input_lower or "engineering" in user_input_lower or "transform" in user_input_lower:
                return "feature_engineering"
            elif "predict" in user_input_lower or "performance" in user_input_lower or "hardness" in user_input_lower or "conductivity" in user_input_lower:
                return "performance_prediction"
            elif "train" in user_input_lower or "model" in user_input_lower or "optimize" in user_input_lower:
                return "model_training"
            else:
                return "general_query"
    
    def extract_parameters(self, user_input: str, intent: str) -> Dict[str, Any]:
        """使用LLM从用户输入中提取参数"""
        try:
            # 构建链式调用
            chain = self.intent_prompt | self.llm | self.parser
            
            # 执行LLM调用
            result = chain.invoke({"user_input": user_input})
            
            # 返回参数
            return result.get("parameters", {})
            
        except Exception as e:
            print(f"LLM参数提取失败：{e}")
            # 返回空参数字典
            return {}
    
    def get_best_tool_for_intent(self, intent: str) -> str:
        """根据意图获取最佳工具名称"""
        tool_mapping = {
            "feature_engineering": "feature_engineering",
            "performance_prediction": "performance_prediction",
            "model_training": "model_training"
        }
        return tool_mapping.get(intent, "general_query")

# 创建全局意图识别器实例
intent_recognizer = IntentRecognizer()
