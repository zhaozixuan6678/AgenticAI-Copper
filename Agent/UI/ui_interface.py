"""
LangChain智能代理用户界面
提供用户友好的交互体验
"""

import sys
from typing import Dict, Any
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from UI.tool_selector import tool_selector
except ImportError:
    from tool_selector import tool_selector

try:
    from UI.agent_core import agent
except ImportError:
    from agent_core import agent


class UIInterface:
    """用户界面类，提供命令行交互界面"""
    
    def __init__(self):
        self.tool_selector = tool_selector
        self.agent = agent
        self.mode = "agent"  # 固定为智能体模式
    
    def display_welcome(self):
        """显示欢迎信息"""
        print("=" * 60)
        print("         铜合金性能预测智能代理系统")
        print("=" * 60)
        print("当前模式：智能体模式")
        print("这是一个基于LangChain框架的智能代理系统，专门用于铜合金性能预测。")
        print("支持以下功能：")
        print("  • 特征工程：将原始数据转换为机器学习特征")
        print("  • 性能预测：预测硬度、电导率和综合性能指标")
        print("  • 模型训练：训练和优化预测模型")
        print()
        print("输入 'help' 查看帮助，输入 'quit' 或 'exit' 退出系统。")
        print("=" * 60)
    
    def display_help(self):
        """显示帮助信息"""
        print("\n=== 帮助信息 ===")
        print("1. 特征工程相关指令：")
        print("   • '执行特征工程，输入文件：Feature-Caculation.xlsx，输出文件：Feature_Output.xlsx'")
        print("   • '将原始数据转换为特征格式'")
        print()
        print("2. 性能预测相关指令：")
        print("   • '预测Cu-90.5Al-5.2Mg合金在500℃固溶+200℃时效8小时的性能'")
        print("   • '如果合金成分为Cu:90.5, Al:5.2, Mg:2.3，工艺为Solution ==> Quenching ==> Aging，预测性能'")
        print()
        print("3. 模型训练相关指令：")
        print("   • '训练性能预测模型，使用Feature.xlsx作为训练数据'")
        print("   • '优化模型参数'")
        print()
        print("4. 系统指令：")
        print("   • 'list tools' - 列出所有可用工具")
        print("   • 'help' - 显示此帮助信息")
        print("   • 'quit' 或 'exit' - 退出系统")
        print()
        print("5. 模式说明：")
        print("   • 智能体模式：增强的自然语言交互，支持文件上传和更多智能功能")
        print("=" * 60)
    
    def display_tools_list(self):
        """显示工具列表"""
        tools = self.agent.list_tools()
        print("\n=== 可用工具列表 ===")
        for i, tool_name in enumerate(tools, 1):
            description = self.agent.get_tool_description(tool_name)
            print(f"{i}. {tool_name}: {description}")
        print()
    
    def process_user_input(self, user_input: str) -> Dict[str, Any]:
        """处理用户输入并返回结果"""
        if not user_input.strip():
            return {"status": "error", "message": "请输入有效的指令"}
        
        # 处理系统指令
        user_input_lower = user_input.lower().strip()
        if user_input_lower in ["quit", "exit", "q"]:
            return {"status": "quit", "message": "再见！"}
        elif user_input_lower == "help":
            self.display_help()
            return {"status": "success", "message": "已显示帮助信息"}
        elif user_input_lower == "list tools":
            self.display_tools_list()
            return {"status": "success", "message": "已显示工具列表"}

        elif user_input_lower == "upload":
            # 文件上传功能
            return self._handle_file_upload()
        
        # 处理用户指令
        try:
            # 智能体模式：使用增强的处理方式
            print("🤖 [智能体模式] 正在处理您的指令...")
            result = self.tool_selector.select_and_execute(user_input)
            return result
        except Exception as e:
            return {"status": "error", "message": f"处理指令时发生错误：{str(e)}"}
    
    def _handle_file_upload(self) -> Dict[str, Any]:
        """处理文件上传功能"""
        print("\n📁 文件上传功能")
        print("请选择文件类型：")
        print("1. 训练数据文件 (.xlsx)")
        print("2. 预测数据文件 (.xlsx)")
        print("3. 参数配置文件 (.xlsx)")
        
        file_type = input("请输入文件类型编号：").strip()
        file_path = input("请输入文件路径：").strip()
        
        # 验证文件是否存在
        import os
        if not os.path.exists(file_path):
            return {"status": "error", "message": f"文件不存在：{file_path}"}
        
        # 验证文件扩展名
        if not file_path.endswith('.xlsx'):
            return {"status": "error", "message": "只支持 .xlsx 文件"}
        
        file_type_map = {
            "1": "训练数据文件",
            "2": "预测数据文件",
            "3": "参数配置文件"
        }
        
        file_type_name = file_type_map.get(file_type, "未知文件类型")
        print(f"\n✅ 成功上传{file_type_name}：{file_path}")
        
        # 返回上传结果
        return {
            "status": "success",
            "message": f"成功上传{file_type_name}：{file_path}",
            "file_path": file_path,
            "file_type": file_type_name
        }
    
    def format_result(self, result: Dict[str, Any]) -> str:
        """格式化结果输出"""
        if result.get("status") == "quit":
            return result.get("message", "")
        
        if result.get("status") == "error":
            return f"❌ 错误：{result.get('message', '未知错误')}\n"
        
        # 成功结果
        intent = result.get("intent", "unknown")
        tool_used = result.get("tool_used", "unknown")
        
        output = []
        output.append(f"✅ 意图识别：{intent}")
        output.append(f"🔧 使用工具：{tool_used}")
        
        if "parameters" in result and result["parameters"]:
            output.append("📊 输入参数：")
            for key, value in result["parameters"].items():
                output.append(f"   • {key}: {value}")
        
        if "result" in result:
            output.append("🎯 预测结果：")
            if isinstance(result["result"], dict):
                for key, value in result["result"].items():
                    output.append(f"   • {key}: {value}")
            else:
                output.append(f"   {result['result']}")
        
        return "\n".join(output) + "\n"
    
    def run_interactive_mode(self):
        """运行交互模式"""
        self.display_welcome()
        
        while True:
            try:
                # 智能体模式提示符
                prompt = "\n🤖 [智能体模式] 请输入您的指令："
                # 获取用户输入
                user_input = input(prompt).strip()
                
                # 处理用户输入
                result = self.process_user_input(user_input)
                
                # 格式化并显示结果
                if result.get("status") == "quit":
                    print(f"\n{result['message']}")
                    break
                
                formatted_result = self.format_result(result)
                print(formatted_result)
                
                # 如果是成功预测，询问是否继续
                if result.get("status") == "success" and "result" in result:
                    continue_prompt = input("是否继续？(y/n): ").strip().lower()
                    if continue_prompt in ["n", "no", "否"]:
                        print("\n👋 再见！感谢使用铜合金性能预测智能代理系统。")
                        break
                        
            except KeyboardInterrupt:
                print("\n\n👋 再见！感谢使用铜合金性能预测智能代理系统。")
                break
            except EOFError:
                print("\n\n👋 再见！感谢使用铜合金性能预测智能代理系统。")
                break
            except Exception as e:
                print(f"\n❌ 发生未预期的错误：{str(e)}")
                print("请重试或输入 'help' 获取帮助。")

# 创建全局UI实例
ui_interface = UIInterface()

# 主程序入口
if __name__ == "__main__":
    ui_interface.run_interactive_mode()
