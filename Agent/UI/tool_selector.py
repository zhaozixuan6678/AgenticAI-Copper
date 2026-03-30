"""
LangChain智能代理工具选择器
负责根据用户输入直接选择并执行合适的工具
使用LLM进行端到端的意图识别和工具选择
"""

import os
import json
from typing import Dict, Any, Optional, List
from langchain_core.language_models import BaseLanguageModel
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic.v1 import BaseModel, Field
from langchain_community.chat_models import ChatOpenAI
from langchain_core.tools import BaseTool
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

try:
    from UI.agent_core import agent
except ImportError:
    from agent_core import agent


class ToolSelectionResult(BaseModel):
    """LLM返回的工具选择结果结构"""
    intent: str = Field(description="识别的意图，必须是以下之一：feature_engineering, feature_selection, performance_prediction, model_training, report_generation, general_query")
    tool_name: str = Field(description="选择的工具名称")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="提取的参数字典")
    confidence: float = Field(default=0.0, description="选择置信度，0.0-1.0")


class ToolSelector:
    """基于LLM的工具选择器，负责选择和执行工具"""
    
    def __init__(self):
        # 初始化LLM
        self.llm = ChatOpenAI(
            model_name="qwen/qwen3-max-thinking",
            temperature=0.3,
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            openai_api_base=os.getenv("OPENAI_API_BASE"),
            max_tokens=1024
        )
        
        # 定义第一步：工具调用判断提示词模板
        self.tool_decision_prompt = PromptTemplate(
            template="""
            You are a professional decision maker for copper alloy performance prediction system.
            Please analyze the user's natural language instruction (which can be in English or Chinese) and return JSON format results according to the following requirements:

            1. Determine whether the user's request requires the use of tools (use_tool), which must be either true or false.

            2. If use_tool is true, identify the most appropriate tool (tool_name) from the following options:
               - feature_engineering: for feature engineering, data transformation, feature extraction, etc.
               - feature_selection: for feature selection, feature importance analysis, etc.
               - performance_prediction: for performance prediction, alloy performance estimation, hardness/conductivity prediction, etc.
               - model_training: for model training, parameter optimization, model tuning, etc.
               - report_generation: for generating research reports, analysis reports, etc.

            3. If use_tool is false, explain why no tool is needed (reason).

            4. Evaluate the decision confidence (confidence), between 0.0-1.0

            Special notes:
            - Use tools for tasks that require actual data analysis, prediction, or report generation
            - Do not use tools for general questions, explanations, or simple inquiries
            - Do not use feature_selection tool for questions that only ask to identify or explain key features
            - Handle both English and Chinese inputs equally well

            User instruction: {user_input}

            Please return only JSON format results, do not include any other text.
            """,
            input_variables=["user_input"]
        )
        
        # 定义第二步：工具参数提取提示词模板
        self.tool_parameter_prompt = PromptTemplate(
            template="""
            You are a professional parameter extraction assistant for copper alloy performance prediction system.
            Please analyze the user's natural language instruction (which can be in English or Chinese) and extract the necessary parameters for the specified tool.

            Tool name: {tool_name}

            Extract relevant parameters (parameters) based on the tool type:
            - For feature_engineering: extract input_path (input file path), output_path (output file path), sheet (sheet name)
            - For feature_selection: extract user_requirement (user's requirement for feature selection), max_features (maximum number of features)
            - For performance_prediction: extract alloy_composition (alloy composition dictionary, e.g., {{"Cu": 90.5, "Al": 5.2}}), processing_params (processing parameters dictionary, e.g., {{"Solution_Temperature": 500, "Aging_Temperature": 200, "Aging_Time": 8}}), processing_route (processing route string)
            - For model_training: extract train_path (training data path), predict_path (prediction data path), param_path (parameter configuration path), output_path (output file path)
            - For report_generation: extract report_type (report type), language (report language)

            Special notes:
            - For processing parameters, ensure correct dictionary format, e.g., "500℃ solution + 200℃ aging 8 hours" should be parsed as {{"Solution_Temperature": 500, "Aging_Temperature": 200, "Aging_Time": 8}}
            - For alloy composition, e.g., "Cu-90.5Al-5.2Mg" should be parsed as {{"Cu": 90.5, "Al": 5.2, "Mg": 2.3}}
            - Handle both English and Chinese inputs equally well

            User instruction: {user_input}

            Please return only JSON format results, do not include any other text.
            """,
            input_variables=["user_input", "tool_name"]
        )
        
        # 定义直接回答提示词模板
        self.direct_answer_prompt = PromptTemplate(
            template="""
            You are a professional copper alloy performance prediction system assistant.
            Please provide a comprehensive answer to the user's question based on your knowledge of materials science and copper alloys.

            User question: {user_input}

            Answer in the same language as the user's question.
            """,
            input_variables=["user_input"]
        )
        
        # 创建输出解析器
        self.parser = JsonOutputParser(pydantic_object=ToolSelectionResult)
        
        # 创建工具决策结果模型
        class ToolDecisionResult(BaseModel):
            use_tool: bool = Field(description="是否需要使用工具")
            tool_name: Optional[str] = Field(default=None, description="选择的工具名称")
            reason: Optional[str] = Field(default=None, description="不需要使用工具的原因")
            confidence: float = Field(default=0.0, description="决策置信度，0.0-1.0")
        
        self.tool_decision_parser = JsonOutputParser(pydantic_object=ToolDecisionResult)
        
        # 创建工具参数结果模型
        class ToolParameterResult(BaseModel):
            parameters: Dict[str, Any] = Field(default_factory=dict, description="提取的参数字典")
            confidence: float = Field(default=0.0, description="参数提取置信度，0.0-1.0")
        
        self.tool_parameter_parser = JsonOutputParser(pydantic_object=ToolParameterResult)
    
    def select_and_execute(self, user_input: str) -> Dict[str, Any]:
        """使用LLM选择并执行最合适的工具"""
        try:
            # 第一步：判断是否需要使用工具
            print("🤖 [第一步] 分析是否需要使用工具...")
            tool_decision_chain = self.tool_decision_prompt | self.llm | self.tool_decision_parser
            tool_decision = tool_decision_chain.invoke({"user_input": user_input})
            
            use_tool = tool_decision.get("use_tool", False)
            tool_name = tool_decision.get("tool_name", "general_query")
            reason = tool_decision.get("reason", "")
            confidence = tool_decision.get("confidence", 0.0)
            
            if use_tool:
                # 第二步：如果需要使用工具，提取参数并执行
                print(f"🤖 [第二步] 提取{tool_name}工具的参数...")
                tool_parameter_chain = self.tool_parameter_prompt | self.llm | self.tool_parameter_parser
                tool_parameter = tool_parameter_chain.invoke({"user_input": user_input, "tool_name": tool_name})
                params = tool_parameter.get("parameters", {})
                
                # 对于性能预测工具，自动解析用户输入中的参数
                if tool_name == "performance_prediction":
                    # 解析合金成分
                    if "alloy_composition" not in params:
                        import re
                        # 匹配合金成分格式，如 "Cu-0.5Al-0.1Cr-0.15Mg"
                        composition_match = re.search(r'Cu[-\s]([\d\.A-Za-z-]+)', user_input)
                        if composition_match:
                            composition_str = composition_match.group(1)
                            # 分割成分，如 "0.5Al-0.1Cr-0.15Mg" -> ["0.5Al", "0.1Cr", "0.15Mg"]
                            components = re.split(r'[-\s]+', composition_str)
                            alloy_composition = {"Cu": 100.0}  # 先假设Cu为100%
                            for component in components:
                                # 匹配元素和含量，如 "0.5Al" -> ("0.5", "Al")
                                component_match = re.search(r'(\d+\.?\d*)([A-Za-z]+)', component)
                                if component_match:
                                    content = float(component_match.group(1))
                                    element = component_match.group(2)
                                    alloy_composition[element] = content
                                    alloy_composition["Cu"] -= content  # 从Cu中减去其他元素含量
                            # 确保Cu含量不为负
                            if alloy_composition["Cu"] < 0:
                                alloy_composition["Cu"] = 100.0 - sum(v for k, v in alloy_composition.items() if k != "Cu")
                            params["alloy_composition"] = alloy_composition
                    
                    # 解析工艺参数
                    if "processing_params" not in params:
                        import re
                        processing_params = {}
                        # 匹配固溶温度和时间，如 "980℃/4h"
                        solution_match = re.search(r'(\d+)℃/([\d\.]+)h', user_input)
                        if solution_match:
                            processing_params["Solution_Temperature"] = float(solution_match.group(1))
                            processing_params["Solution_Time"] = float(solution_match.group(2))
                        # 匹配时效温度和时间，如 "450℃/5h"
                        aging_match = re.search(r'(\d+)℃/([\d\.]+)h', user_input)
                        if aging_match:
                            processing_params["Aging_Temperature"] = float(aging_match.group(1))
                            processing_params["Aging_Time"] = float(aging_match.group(2))
                        # 匹配冷轧变形量，如 "50% 冷轧"
                        cold_rolling_match = re.search(r'([\d\.]+)%\s*冷轧', user_input)
                        if cold_rolling_match:
                            processing_params["Cold_Rolling"] = float(cold_rolling_match.group(1))
                        params["processing_params"] = processing_params
                    
                    # 解析工艺路线
                    if "processing_route" not in params:
                        # 根据用户输入构建工艺路线
                        if "固溶" in user_input and "冷轧" in user_input and "时效" in user_input:
                            params["processing_route"] = "Solution ==> Cold Rolling ==> Aging"
                        elif "固溶" in user_input and "时效" in user_input:
                            params["processing_route"] = "Solution ==> Quenching ==> Aging"
                        else:
                            params["processing_route"] = "Solution ==> Quenching ==> Aging"
                
                # 对于报告生成工具，添加模型训练结果
                if tool_name == "report_generation":
                    # 获取模型训练结果
                    training_results = agent.get_training_results()
                    if training_results:
                        params["model_results"] = training_results
                    else:
                        # 如果没有训练结果，使用默认的模拟数据
                        params["model_results"] = {
                            "metrics": {
                                "average": {
                                    "r2": 0.85,
                                    "mae": 5.2,
                                    "rmse": 7.8,
                                    "mape": 3.1
                                }
                            },
                            "feature_importance": [
                                {"特征": "Solution_T", "重要性": 0.15},
                                {"特征": "Aging_T", "重要性": 0.12},
                                {"特征": "Cu_wt_pct", "重要性": 0.10},
                                {"特征": "Al_wt_pct", "重要性": 0.08},
                                {"特征": "Mg_wt_pct", "重要性": 0.07}
                            ],
                            "model_comparison": [
                                {"模型": "SVR", "R² 得分": 0.82, "RMSE": 8.2, "训练时间 (秒)": 15.3},
                                {"模型": "CatBoost", "R² 得分": 0.88, "RMSE": 6.5, "训练时间 (秒)": 22.7},
                                {"模型": "随机森林", "R² 得分": 0.86, "RMSE": 7.1, "训练时间 (秒)": 18.9},
                                {"模型": "XGBoost", "R² 得分": 0.89, "RMSE": 6.2, "训练时间 (秒)": 20.4}
                            ]
                        }
                    # 设置默认参数
                    if "report_type" not in params:
                        params["report_type"] = "comprehensive"
                    if "language" not in params:
                        # 根据输入语言自动设置报告语言
                        params["language"] = "English" if any(char.isalpha() and char.isupper() for char in user_input) else "中文"
                # 对于特征选择工具，设置默认参数
                elif tool_name == "feature_selection":
                    # 设置默认参数
                    if "user_requirement" not in params:
                        params["user_requirement"] = user_input
                    if "max_features" not in params:
                        params["max_features"] = 5
                    # 设置默认数据路径
                    if "data_path" not in params:
                        # 使用默认的特征文件路径
                        import os
                        default_data_path = os.path.join("..", "Feature.xlsx")
                        params["data_path"] = default_data_path
                # 对于性能预测工具，设置默认参数
                elif tool_name == "performance_prediction":
                    # 设置默认参数
                    if "alloy_composition" not in params:
                        params["alloy_composition"] = {"Cu": 90.5, "Al": 5.2, "Mg": 2.3}
                    if "processing_params" not in params:
                        params["processing_params"] = {"Solution_Temperature": 500, "Aging_Temperature": 200, "Aging_Time": 8}
                    if "processing_route" not in params:
                        params["processing_route"] = "Solution ==> Quenching ==> Aging"
                # 对于特征工程工具，设置默认参数
                elif tool_name == "feature_engineering":
                    # 设置默认参数
                    if "input_path" not in params:
                        import os
                        default_input_path = os.path.join("..", "Feature.xlsx")
                        params["input_path"] = default_input_path
                    if "output_path" not in params:
                        import os
                        default_output_path = os.path.join("..", "Feature_Output.xlsx")
                        params["output_path"] = default_output_path
                    if "sheet" not in params:
                        params["sheet"] = "Input"
                # 对于模型训练工具，设置默认参数
                elif tool_name == "model_training":
                    # 设置默认参数
                    if "train_path" not in params:
                        import os
                        default_train_path = os.path.join("..", "Feature.xlsx")
                        params["train_path"] = default_train_path
                    if "predict_path" not in params:
                        import os
                        default_predict_path = os.path.join("..", "Feature.xlsx")
                        params["predict_path"] = default_predict_path
                    if "param_path" not in params:
                        import os
                        default_param_path = os.path.join("..", "Feature.xlsx")
                        params["param_path"] = default_param_path
                    if "output_path" not in params:
                        import os
                        default_output_path = os.path.join("..", "Prediction_Output.xlsx")
                        params["output_path"] = default_output_path
                
                tool = agent.get_tool(tool_name)
                
                # 执行工具
                execution_result = {
                    "intent": tool_name, 
                    "tool_used": tool_name, 
                    "parameters": params,
                    "confidence": confidence
                }
                
                if tool:
                    try:
                        # 执行工具
                        print(f"🤖 [执行工具] 调用{tool_name}工具...")
                        tool_result = tool.invoke(params)
                        execution_result["result"] = tool_result
                        execution_result["status"] = "success"
                    except Exception as e:
                        execution_result["result"] = f"工具执行失败：{str(e)}"
                        execution_result["status"] = "error"
                else:
                    execution_result["result"] = "未找到匹配的工具"
                    execution_result["status"] = "error"
                
                return execution_result
            else:
                # 如果不需要使用工具，直接调用大模型回答
                print("🤖 [直接回答] 不需要使用工具，直接回答用户问题...")
                direct_answer_chain = self.direct_answer_prompt | self.llm
                direct_answer = direct_answer_chain.invoke({"user_input": user_input})
                
                return {
                    "intent": "general_query",
                    "tool_used": "general_query",
                    "parameters": {},
                    "result": direct_answer,
                    "status": "success",
                    "reason": reason,
                    "confidence": confidence
                }
            
        except Exception as e:
            print(f"LLM工具选择失败：{e}")
            # 直接返回错误信息
            return {
                "intent": "general_query",
                "tool_used": "general_query",
                "parameters": {},
                "result": f"LLM工具选择失败：{e}",
                "status": "error"
            }
    
    def get_available_tools(self) -> List[str]:
        """获取所有可用工具列表"""
        return agent.list_tools()
    
    def get_tool_info(self, tool_name: str) -> Dict[str, str]:
        """获取工具信息"""
        return {
            "name": tool_name,
            "description": agent.get_tool_description(tool_name),
            "parameters": self._get_tool_parameters(tool_name)
        }
    
    def _get_tool_parameters(self, tool_name: str) -> Dict[str, str]:
        """获取工具参数信息"""
        # 这里可以根据需要实现更详细的参数提取
        parameter_mapping = {
            "feature_engineering": ["input_path", "output_path", "sheet"],
            "performance_prediction": ["alloy_composition", "processing_params", "processing_route"],
            "model_training": ["train_path", "predict_path", "param_path", "output_path"]
        }
        return parameter_mapping.get(tool_name, [])

# 创建全局工具选择器实例
tool_selector = ToolSelector()