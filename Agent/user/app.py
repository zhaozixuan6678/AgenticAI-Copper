"""
材料科学交互式仪表盘

面向铜合金性能预测与分析的专业UI。
专为材料科学研究人员设计，具有领域特定的可视化功能。
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 设置页面配置
st.set_page_config(
    page_title="材料科学交互式仪表盘",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 尝试导入现有的UI模块
try:
    from UI.agent_core import agent
    from UI.model_manager import is_model_available
    import_success = True
except ImportError as e:
    # 尝试备选导入路径
    try:
        from Agent.UI.agent_core import agent
        from Agent.UI.model_manager import is_model_available
        import_success = True
    except ImportError as e2:
        import_success = False
        import_error = str(e2)
        agent = None

# 显示导入结果
if import_success:
    st.success("成功导入智能代理模块！")
else:
    st.warning(f"警告：无法导入agent_core。使用模拟功能。错误: {import_error}")

# 材料科学主题的自定义CSS
st.markdown("""
<style>
    :root {
        --primary-color: #1a56db;
        --secondary-color: #0c418d;
        --accent-color: #2563eb;
        --success-color: #10b981;
        --warning-color: #f59e0b;
        --error-color: #ef4444;
        --background-color: #f9fafb;
        --card-bg: #ffffff;
        --text-primary: #1f2937;
        --text-secondary: #6b7280;
    }
    .main {
        background-color: var(--background-color);
    }
    .stApp > header {
        background-color: var(--primary-color);
    }
    .stSidebar {
        background-color: var(--card-bg);
    }
    .stButton>button {
        background-color: var(--primary-color);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 600;
    }
    .stButton>button:hover {
        background-color: var(--secondary-color);
        transform: translateY(-2px);
    }
    .metric-card {
        background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
        color: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 10px 0;
    }
    .metric-label {
        font-size: 1.1rem;
        opacity: 0.9;
        margin-bottom: 5px;
    }
    .section-header {
        color: var(--secondary-color);
        border-bottom: 3px solid var(--primary-color);
        padding-bottom: 10px;
        margin-top: 30px;
    }
</style>
""", unsafe_allow_html=True)

# 模式选择 - 固定为智能体模式
if 'mode' not in st.session_state:
    st.session_state.mode = 'agent'  # 固定为智能体模式

# 语言选择
if 'language' not in st.session_state:
    st.session_state.language = 'zh'

# 语言选择器
st.sidebar.markdown("<h3 style='color: var(--secondary-color);'>🌐 语言选择</h3>", unsafe_allow_html=True)
language = st.sidebar.selectbox("选择语言", ["中文", "English"], index=0)
st.session_state.language = 'zh' if language == "中文" else 'en'

# 显示智能体模式信息
if st.session_state.language == 'zh':
    st.sidebar.info("智能体模式：支持自然语言对话，依然可以上传数据")
else:
    st.sidebar.info("Agent Mode: Supports natural language dialogue, still can upload data")

# 根据语言设置标题
if st.session_state.language == 'zh':
    st.title("🤖 铜合金性能预测智能体")
    st.markdown("""
    **面向铜合金多目标性能-成分工艺协同优化-自主工作流（硬度 / 电导率 / Q3–Euclidean）**
    
    请在下方输入您的指令，例如：
    - "预测 Cu-0.5Al-0.1Cr-0.15Mg 合金在 980℃/4h 固溶 + 50% 冷轧 + 450℃/5h 时效条件下的性能"
    - "基于三步特征筛选策略（相关性分析、递归特征消除与穷举组合优化）进行特征筛选分析"
    - "从刚才测试的几组成分-工艺组合中推荐兼顾高强度与高导电性的最优成分–工艺组合"
    """)
else:
    st.title("🤖 Agent for Copper Alloy Optimization")
    st.markdown("""
    **Autonomous workflow for multi-objective prediction**
    
    Please enter your commands below, for example:
    - "Predict the performance of Cu-0.5Al-0.1Cr-0.15Mg alloy at 980℃/4h Solution + 50% Cold rolling + 450℃/5h Aging"
    - "Identify key features governing hardness, conductivity, and Q3–Euclidean"
    - "Generate a multi-objective optimization report for Cu-Cr-Zr alloys"
    """)

# Excel文件上传和导出功能
if st.session_state.language == 'zh':
    st.sidebar.markdown("<h3 style='color: var(--secondary-color);'>📁 数据管理</h3>", unsafe_allow_html=True)
else:
    st.sidebar.markdown("<h3 style='color: var(--secondary-color);'>📁 Data Management</h3>", unsafe_allow_html=True)

# 初始化会话状态
if 'uploaded_file_path' not in st.session_state:
    st.session_state.uploaded_file_path = None
if 'show_delete_success' not in st.session_state:
    st.session_state.show_delete_success = False

# 处理删除成功后的显示
if st.session_state.show_delete_success:
    if st.session_state.language == 'zh':
        st.sidebar.success("已删除上传的文件")
    else:
        st.sidebar.success("Uploaded file deleted")
    st.session_state.show_delete_success = False

# 文件上传处理
if st.session_state.language == 'zh':
    uploaded_file = st.sidebar.file_uploader("上传Excel文件", type=["xlsx", "xls"])
else:
    uploaded_file = st.sidebar.file_uploader("Upload Excel file", type=["xlsx", "xls"])

if uploaded_file is not None:
    try:
        # 保存上传的文件
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp:
            tmp.write(uploaded_file.getvalue())
            st.session_state.uploaded_file_path = tmp.name
        
        uploaded_df = pd.read_excel(uploaded_file)
        if st.session_state.language == 'zh':
            st.sidebar.success("文件上传成功！")
            st.sidebar.write(f"上传的数据包含 {len(uploaded_df)} 行和 {len(uploaded_df.columns)} 列")
            st.sidebar.write("数据预览:")
        else:
            st.sidebar.success("File uploaded successfully!")
            st.sidebar.write(f"Uploaded data contains {len(uploaded_df)} rows and {len(uploaded_df.columns)} columns")
            st.sidebar.write("Data preview:")
        st.sidebar.dataframe(uploaded_df.head())
        
        # 使用上传的数据替换默认数据
        df = uploaded_df
    except Exception as e:
        if st.session_state.language == 'zh':
            st.sidebar.error(f"文件读取失败: {e}")
        else:
            st.sidebar.error(f"File reading failed: {e}")

# 显示已上传的文件信息
if st.session_state.uploaded_file_path:
    # 显示文件信息
    if st.session_state.language == 'zh':
        st.sidebar.info(f"已上传文件: {os.path.basename(st.session_state.uploaded_file_path)}")
        if st.sidebar.button("删除已上传文件", key="delete_file"):
            if os.path.exists(st.session_state.uploaded_file_path):
                os.remove(st.session_state.uploaded_file_path)
            # 清除会话状态
            st.session_state.uploaded_file_path = None
            # 设置删除成功标志
            st.session_state.show_delete_success = True
            # 重新运行以更新界面
            st.rerun()
    else:
        st.sidebar.info(f"Uploaded file: {os.path.basename(st.session_state.uploaded_file_path)}")
        if st.sidebar.button("Delete uploaded file", key="delete_file"):
            if os.path.exists(st.session_state.uploaded_file_path):
                os.remove(st.session_state.uploaded_file_path)
            # 清除会话状态
            st.session_state.uploaded_file_path = None
            # 设置删除成功标志
            st.session_state.show_delete_success = True
            # 重新运行以更新界面
            st.rerun()

# 数据导出
if st.session_state.language == 'zh':
    if st.sidebar.button("导出数据为Excel"):
        try:
            import io
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='合金数据')
            output.seek(0)
            
            st.sidebar.download_button(
                label="下载Excel文件",
                data=output,
                file_name="合金数据.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        except Exception as e:
            st.sidebar.error(f"导出失败: {e}")
else:
    if st.sidebar.button("Export data as Excel"):
        try:
            import io
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Alloy Data')
            output.seek(0)
            
            st.sidebar.download_button(
                label="Download Excel file",
                data=output,
                file_name="Alloy_Data.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        except Exception as e:
            st.sidebar.error(f"Export failed: {e}")

# 智能体模式的实现
if st.session_state.mode == 'agent':
    # 加载示例数据用于可视化
    @st.cache_data
    def load_sample_data():
        # Generate realistic copper alloy data
        np.random.seed(42)
        n_samples = 100
        
        # Alloy composition (wt.%)
        cu = np.random.normal(85, 5, n_samples)
        al = np.random.normal(5, 2, n_samples)
        mg = np.random.normal(2.5, 1, n_samples)
        zn = np.random.normal(1, 0.5, n_samples)
        sn = np.random.normal(0.5, 0.2, n_samples)
        
        # Process parameters
        solution_temp = np.random.normal(500, 50, n_samples)
        quench_rate = np.random.normal(100, 20, n_samples)
        aging_temp = np.random.normal(200, 30, n_samples)
        aging_time = np.random.normal(8, 4, n_samples)
        
        # Performance metrics (simulated)
        hardness = 150 + 0.8*cu + 2.5*al + 3.2*mg + 0.5*solution_temp - 0.3*aging_time + np.random.normal(0, 10, n_samples)
        ec = 45 - 0.2*cu + 1.2*al + 0.8*mg + 0.1*solution_temp + 0.2*aging_temp + np.random.normal(0, 5, n_samples)
        q3 = 0.7 + 0.002*hardness + 0.001*ec + np.random.normal(0, 0.05, n_samples)
        
        df = pd.DataFrame({
            'Cu_wt_pct': cu,
            'Al_wt_pct': al,
            'Mg_wt_pct': mg,
            'Zn_wt_pct': zn,
            'Sn_wt_pct': sn,
            'Solution_Temp_C': solution_temp,
            'Quench_Rate_C_s': quench_rate,
            'Aging_Temp_C': aging_temp,
            'Aging_Time_h': aging_time,
            'Hardness_HV': hardness,
            'EC_IACS_pct': ec,
            'Q3_Euclidean': q3
        })
        
        return df
    
    df = load_sample_data()
    
    # 初始化会话状态
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'user_input' not in st.session_state:
        st.session_state.user_input = ""
    
    # 显示聊天历史
    st.markdown("<div style='background-color: #f0f2f5; border-radius: 10px; padding: 20px; margin-bottom: 20px;'>", unsafe_allow_html=True)
    for message in st.session_state.chat_history:
        if message['role'] == 'user':
            st.markdown(f"<div style='display: flex; margin-bottom: 15px;'><div style='flex: 1;'></div><div style='max-width: 70%; background-color: #dcf8c6; border-radius: 18px 18px 4px 18px; padding: 12px 16px; box-shadow: 0 1px 0.5px rgba(0,0,0,0.13);'><div style='font-weight: 600; color: #333; margin-bottom: 4px;'>You</div><div style='color: #333;'>{message['content']}</div></div></div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div style='display: flex; margin-bottom: 15px;'><div style='max-width: 70%; background-color: #ffffff; border-radius: 18px 18px 18px 4px; padding: 12px 16px; box-shadow: 0 1px 0.5px rgba(0,0,0,0.13);'><div style='font-weight: 600; color: #1a56db; margin-bottom: 4px;'>Alloy Design Assistant</div><div style='color: #333;'>{message['content']}</div></div><div style='flex: 1;'></div></div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # 输入区域
    col1, col2 = st.columns([4, 1])
    with col1:
        user_input = st.text_input("Describe your alloy design task:", value=st.session_state.user_input, key="agent_input", placeholder="E.g. Please predict the properties of Cu-90.5Al-5.2Mg Alloys")
    with col2:
        submit_button = st.button("Send", key="agent_submit", use_container_width=True)
    
    # 提交按钮处理
    if submit_button:
        if user_input.strip():
            # 添加用户消息到历史
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            
            # 显示加载状态
            with st.spinner("Thinking ..."):
                try:
                    # 尝试导入工具选择器
                    from UI.tool_selector import tool_selector
                    
                    # 处理用户输入
                    result = tool_selector.select_and_execute(user_input)
                    
                    # 格式化结果
                    if result.get("status") == "success":
                        response = ""
                        if "intent" in result:
                            response += f"Intent Detection: {result['intent']}\n"
                        if "tool_used" in result:
                            response += f"Selected Tool: {result['tool_used']}\n"
                        if "parameters" in result and result["parameters"]:
                            response += "Input Parameters:\n"
                            for key, value in result["parameters"].items():
                                if key != "model_results":  # 不显示模型结果，因为会很长
                                    response += f"  - {key}: {value}\n"
                        if "result" in result:
                            response += "Prediction Results:\n"
                            if isinstance(result["result"], dict):
                                if "report" in result["result"]:
                                    # 对于报告生成工具，直接显示报告内容
                                    report = result["result"]["report"]
                                    # 检查report是否是AIMessage对象
                                    if hasattr(report, 'content'):
                                        response = report.content
                                    else:
                                        response = report
                                else:
                                    for key, value in result["result"].items():
                                        response += f"  - {key}: {value}\n"
                            else:
                                response += f"  {result['result']}\n"
                    else:
                        response = f"Error: {result.get('result', 'Fail')}"
                except Exception as e:
                    response = f"Error: {str(e)}"
            
            # 添加助手消息到历史
            st.session_state.chat_history.append({"role": "assistant", "content": response})
            
            # 清空输入框
            st.session_state.user_input = ""
            
            # 重新运行以更新界面
            st.rerun()
    
    # 分析用户指令并生成相关的可视化数据
    def generate_relevant_visualization(user_input, df):
        # 简单的关键词匹配来确定用户的意图
        user_input_lower = user_input.lower()
        
        # 显示分析结果
        st.markdown("<h2 class='section-header'>📊 Data visualization</h2>", unsafe_allow_html=True)
        
        # 关键指标卡片 - 只显示与当前分析相关的指标
        if '硬度' in user_input_lower or 'hardness' in user_input_lower:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"<div class='metric-card'><div class='metric-label'>Average Hardness </div><div class='metric-value'>{df['Hardness_HV'].mean():.1f} HV</div></div>", unsafe_allow_html=True)
            with col2:
                st.markdown(f"<div class='metric-card'><div class='metric-label'>硬度标准差</div><div class='metric-value'>{df['Hardness_HV'].std():.1f} HV</div></div>", unsafe_allow_html=True)
        elif '电导率' in user_input_lower or 'conductivity' in user_input_lower or 'ec' in user_input_lower:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"<div class='metric-card'><div class='metric-label'>Conductivity</div><div class='metric-value'>{df['EC_IACS_pct'].mean():.1f}%</div></div>", unsafe_allow_html=True)
            with col2:
                st.markdown(f"<div class='metric-card'><div class='metric-label'>电导率标准差</div><div class='metric-value'>{df['EC_IACS_pct'].std():.1f}%</div></div>", unsafe_allow_html=True)
        elif '成分' in user_input_lower or 'composition' in user_input_lower or 'alloy' in user_input_lower:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"<div class='metric-card'><div class='metric-label'>平均铜含量</div><div class='metric-value'>{df['Cu_wt_pct'].mean():.1f}%</div></div>", unsafe_allow_html=True)
            with col2:
                st.markdown(f"<div class='metric-card'><div class='metric-label'>平均铝含量</div><div class='metric-value'>{df['Al_wt_pct'].mean():.1f}%</div></div>", unsafe_allow_html=True)
            with col3:
                st.markdown(f"<div class='metric-card'><div class='metric-label'>平均镁含量</div><div class='metric-value'>{df['Mg_wt_pct'].mean():.1f}%</div></div>", unsafe_allow_html=True)
        elif '工艺' in user_input_lower or 'process' in user_input_lower or 'heat' in user_input_lower:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"<div class='metric-card'><div class='metric-label'>平均固溶温度</div><div class='metric-value'>{df['Solution_Temp_C'].mean():.0f}°C</div></div>", unsafe_allow_html=True)
            with col2:
                st.markdown(f"<div class='metric-card'><div class='metric-label'>平均时效温度</div><div class='metric-value'>{df['Aging_Temp_C'].mean():.0f}°C</div></div>", unsafe_allow_html=True)
            with col3:
                st.markdown(f"<div class='metric-card'><div class='metric-label'>平均时效时间</div><div class='metric-value'>{df['Aging_Time_h'].mean():.1f}h</div></div>", unsafe_allow_html=True)
        elif '预测' in user_input_lower or 'predict' in user_input_lower or 'performance' in user_input_lower:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"<div class='metric-card'><div class='metric-label'>平均硬度</div><div class='metric-value'>{df['Hardness_HV'].mean():.1f} HV</div></div>", unsafe_allow_html=True)
            with col2:
                st.markdown(f"<div class='metric-card'><div class='metric-label'>平均电导率</div><div class='metric-value'>{df['EC_IACS_pct'].mean():.1f}%</div></div>", unsafe_allow_html=True)
            with col3:
                st.markdown(f"<div class='metric-card'><div class='metric-label'>平均Q3得分</div><div class='metric-value'>{df['Q3_Euclidean'].mean():.3f}</div></div>", unsafe_allow_html=True)
        
        # 根据用户指令选择合适的可视化
        if '硬度' in user_input_lower or 'hardness' in user_input_lower:
            # 硬度相关的可视化
            st.markdown("<h3 style='color: var(--secondary-color); margin-top: 30px;'>硬度分析</h3>", unsafe_allow_html=True)
            
            # 硬度分布
            fig_hardness = px.histogram(df, x='Hardness_HV', title='硬度分布', color_discrete_sequence=['#1a56db'])
            st.plotly_chart(fig_hardness, use_container_width=True)
            
            # 硬度与其他因素的关系
            fig_hardness_relation = make_subplots(
                rows=2, cols=2,
                subplot_titles=("硬度 vs 铜含量", "硬度 vs 铝含量", 
                              "硬度 vs 镁含量", "硬度 vs 固溶温度"),
                specs=[[{"type": "scatter"}, {"type": "scatter"}],
                       [{"type": "scatter"}, {"type": "scatter"}]]
            )
            
            fig_hardness_relation.add_trace(
                go.Scatter(x=df['Cu_wt_pct'], y=df['Hardness_HV'], mode='markers', name='铜含量'),
                row=1, col=1
            )
            fig_hardness_relation.add_trace(
                go.Scatter(x=df['Al_wt_pct'], y=df['Hardness_HV'], mode='markers', name='铝含量'),
                row=1, col=2
            )
            fig_hardness_relation.add_trace(
                go.Scatter(x=df['Mg_wt_pct'], y=df['Hardness_HV'], mode='markers', name='镁含量'),
                row=2, col=1
            )
            fig_hardness_relation.add_trace(
                go.Scatter(x=df['Solution_Temp_C'], y=df['Hardness_HV'], mode='markers', name='固溶温度'),
                row=2, col=2
            )
            
            fig_hardness_relation.update_layout(height=600, title_text="硬度与各因素的关系")
            st.plotly_chart(fig_hardness_relation, use_container_width=True)
            
        elif '电导率' in user_input_lower or 'conductivity' in user_input_lower or 'ec' in user_input_lower:
            # 电导率相关的可视化
            st.markdown("<h3 style='color: var(--secondary-color); margin-top: 30px;'>电导率分析</h3>", unsafe_allow_html=True)
            
            # 电导率分布
            fig_ec = px.histogram(df, x='EC_IACS_pct', title='电导率分布', color_discrete_sequence=['#0c418d'])
            st.plotly_chart(fig_ec, use_container_width=True)
            
            # 电导率与其他因素的关系
            fig_ec_relation = make_subplots(
                rows=2, cols=2,
                subplot_titles=("电导率 vs 铜含量", "电导率 vs 铝含量", 
                              "电导率 vs 镁含量", "电导率 vs 时效温度"),
                specs=[[{"type": "scatter"}, {"type": "scatter"}],
                       [{"type": "scatter"}, {"type": "scatter"}]]
            )
            
            fig_ec_relation.add_trace(
                go.Scatter(x=df['Cu_wt_pct'], y=df['EC_IACS_pct'], mode='markers', name='铜含量'),
                row=1, col=1
            )
            fig_ec_relation.add_trace(
                go.Scatter(x=df['Al_wt_pct'], y=df['EC_IACS_pct'], mode='markers', name='铝含量'),
                row=1, col=2
            )
            fig_ec_relation.add_trace(
                go.Scatter(x=df['Mg_wt_pct'], y=df['EC_IACS_pct'], mode='markers', name='镁含量'),
                row=2, col=1
            )
            fig_ec_relation.add_trace(
                go.Scatter(x=df['Aging_Temp_C'], y=df['EC_IACS_pct'], mode='markers', name='时效温度'),
                row=2, col=2
            )
            
            fig_ec_relation.update_layout(height=600, title_text="电导率与各因素的关系")
            st.plotly_chart(fig_ec_relation, use_container_width=True)
            
        elif '成分' in user_input_lower or 'composition' in user_input_lower or 'alloy' in user_input_lower:
            # 合金成分相关的可视化
            st.markdown("<h3 style='color: var(--secondary-color); margin-top: 30px;'>合金成分分析</h3>", unsafe_allow_html=True)
            
            # 成分雷达图
            avg_comp = df[['Cu_wt_pct', 'Al_wt_pct', 'Mg_wt_pct', 'Zn_wt_pct', 'Sn_wt_pct']].mean()
            
            fig_radar = go.Figure(data=go.Scatterpolar(
                r=[avg_comp['Cu_wt_pct'], avg_comp['Al_wt_pct'], avg_comp['Mg_wt_pct'], 
                   avg_comp['Zn_wt_pct'], avg_comp['Sn_wt_pct']],
                theta=['铜', '铝', '镁', '锌', '锡'],
                fill='toself',
                name='平均成分'
            ))
            
            fig_radar.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, max(avg_comp)*1.2]
                    )
                ),
                showlegend=True,
                title="平均成分分布"
            )
            st.plotly_chart(fig_radar, use_container_width=True)
            
            # 成分散点图
            fig_composition = px.scatter_matrix(
                df,
                dimensions=['Cu_wt_pct', 'Al_wt_pct', 'Mg_wt_pct', 'Zn_wt_pct'],
                color='Hardness_HV',
                color_continuous_scale='Viridis',
                title="成分关系矩阵"
            )
            st.plotly_chart(fig_composition, use_container_width=True)
            
        elif '工艺' in user_input_lower or 'process' in user_input_lower or 'heat' in user_input_lower:
            # 工艺参数相关的可视化
            st.markdown("<h3 style='color: var(--secondary-color); margin-top: 30px;'>工艺参数分析</h3>", unsafe_allow_html=True)
            
            # 工艺参数与性能的关系
            fig_process = make_subplots(
                rows=2, cols=2,
                subplot_titles=("固溶温度 vs 硬度", "时效温度 vs 硬度", 
                              "时效时间 vs 硬度", "淬火速率 vs 硬度"),
                specs=[[{"type": "scatter"}, {"type": "scatter"}],
                       [{"type": "scatter"}, {"type": "scatter"}]]
            )
            
            fig_process.add_trace(
                go.Scatter(x=df['Solution_Temp_C'], y=df['Hardness_HV'], mode='markers', name='固溶温度'),
                row=1, col=1
            )
            fig_process.add_trace(
                go.Scatter(x=df['Aging_Temp_C'], y=df['Hardness_HV'], mode='markers', name='时效温度'),
                row=1, col=2
            )
            fig_process.add_trace(
                go.Scatter(x=df['Aging_Time_h'], y=df['Hardness_HV'], mode='markers', name='时效时间'),
                row=2, col=1
            )
            fig_process.add_trace(
                go.Scatter(x=df['Quench_Rate_C_s'], y=df['Hardness_HV'], mode='markers', name='淬火速率'),
                row=2, col=2
            )
            
            fig_process.update_layout(height=600, title_text="工艺参数对硬度的影响")
            st.plotly_chart(fig_process, use_container_width=True)
            
        elif '预测' in user_input_lower or 'predict' in user_input_lower or 'performance' in user_input_lower:
            # 性能预测相关的可视化
            st.markdown("<h3 style='color: var(--secondary-color); margin-top: 30px;'>性能预测分析</h3>", unsafe_allow_html=True)
            
            # 3D成分-性能关系
            fig_3d = px.scatter_3d(
                df, x='Cu_wt_pct', y='Al_wt_pct', z='Mg_wt_pct', 
                color='Hardness_HV', size='Hardness_HV',
                color_continuous_scale='Viridis',
                title="3D成分-性能关系",
                labels={'Cu_wt_pct': '铜 (重量%)', 'Al_wt_pct': '铝 (重量%)', 'Mg_wt_pct': '镁 (重量%)'}
            )
            st.plotly_chart(fig_3d, use_container_width=True)
            
            # 性能相关性热图
            corr_matrix = df[['Hardness_HV', 'EC_IACS_pct', 'Q3_Euclidean']].corr()
            fig_heatmap = px.imshow(
                corr_matrix, 
                text_auto='.2f',
                color_continuous_scale='RdBu_r',
                title="性能指标相关性热图"
            )
            st.plotly_chart(fig_heatmap, use_container_width=True)
            
        else:
            # 默认可视化
            st.markdown("<h3 style='color: var(--secondary-color); margin-top: 30px;'>性能分布</h3>", unsafe_allow_html=True)
            
            # 创建子图
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=("硬度分布", "电导率分布", 
                              "Q3得分分布", "成分相关性"),
                specs=[[{"type": "histogram"}, {"type": "histogram"}],
                       [{"type": "histogram"}, {"type": "scatter"}]]
            )
            
            # 硬度直方图
            fig.add_trace(
                go.Histogram(x=df['Hardness_HV'], name='硬度', marker_color='#1a56db'),
                row=1, col=1
            )
            
            # 电导率直方图
            fig.add_trace(
                go.Histogram(x=df['EC_IACS_pct'], name='电导率', marker_color='#0c418d'),
                row=1, col=2
            )
            
            # Q3直方图
            fig.add_trace(
                go.Histogram(x=df['Q3_Euclidean'], name='Q3得分', marker_color='#2563eb'),
                row=2, col=1
            )
            
            # 成分散点图
            fig.add_trace(
                go.Scatter(x=df['Cu_wt_pct'], y=df['Al_wt_pct'], mode='markers', 
                          marker=dict(size=8, color=df['Hardness_HV'], colorscale='Viridis', showscale=True),
                          name='铜 vs 铝'),
                row=2, col=2
            )
            
            fig.update_layout(height=600, showlegend=False, title_text="材料性能分析")
            st.plotly_chart(fig, use_container_width=True)
        
        # 最近预测表格
        st.markdown("<h3 style='color: var(--secondary-color); margin-top: 30px;'>最近预测</h3>", unsafe_allow_html=True)
        recent_df = df.head(10).copy()
        recent_df['Prediction_ID'] = [f'P{i+1:03d}' for i in range(len(recent_df))]
        recent_df = recent_df[['Prediction_ID', 'Cu_wt_pct', 'Al_wt_pct', 'Mg_wt_pct', 
                              'Solution_Temp_C', 'Aging_Temp_C', 'Hardness_HV', 'EC_IACS_pct', 'Q3_Euclidean']]
        st.dataframe(recent_df.style.format({
            'Cu_wt_pct': '{:.1f}',
            'Al_wt_pct': '{:.1f}',
            'Mg_wt_pct': '{:.1f}',
            'Solution_Temp_C': '{:.0f}',
            'Aging_Temp_C': '{:.0f}',
            'Hardness_HV': '{:.1f}',
            'EC_IACS_pct': '{:.1f}',
            'Q3_Euclidean': '{:.3f}'
        }), use_container_width=True)
    
    # 只有当有聊天历史时才显示可视化数据
    if len(st.session_state.chat_history) > 0:
        # 获取用户最后一条指令
        user_input = ""
        for message in reversed(st.session_state.chat_history):
            if message['role'] == 'user':
                user_input = message['content']
                break
        
        # 生成与用户指令相关的可视化
        generate_relevant_visualization(user_input, df)
    
    # 清除历史按钮
    st.markdown("<div style='margin-top: 15px; text-align: center;'>", unsafe_allow_html=True)
    if st.button("清除聊天历史", key="clear_history", type="secondary"):
        st.session_state.chat_history = []
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("<p style='text-align: center; color: var(--text-secondary);'>材料科学交互式仪表盘 v1.0 | 为铜合金研究设计</p>", unsafe_allow_html=True)
