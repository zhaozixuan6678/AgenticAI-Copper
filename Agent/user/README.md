# 材料科学交互式仪表盘使用说明

## 环境要求

- Python 3.9+  
- pip 20.0+
- 操作系统：Windows 10/11、macOS、Linux

## 安装步骤

### 1. 克隆或下载项目

将项目文件下载到本地目录，确保目录结构完整。

### 2. 安装依赖

打开命令行终端，进入项目的 `Agent/user` 目录，执行以下命令：

```bash
pip install -r requirements.txt
```

这将安装所有必要的依赖包，包括：
- streamlit (Web界面)
- plotly (数据可视化)
- pandas (数据处理)
- numpy (数值计算)
- scikit-learn (机器学习)
- catboost (梯度提升模型)
- langchain (智能代理)
- python-dotenv (环境变量管理)

### 3. 配置环境变量

1. 复制 `.env.example` 文件为 `.env`
2. 编辑 `.env` 文件，填写您的 OpenAI API 密钥：

```
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_API_BASE=https://openrouter.ai/api/v1
```

> 注意：如果没有API密钥，系统会自动切换到模拟模式，仍然可以使用基本功能。

## 运行方法

### 方法一：使用启动脚本

在 `Agent/user` 目录下，双击运行 `start.bat` 文件。

### 方法二：手动运行

打开命令行终端，进入 `Agent/user` 目录，执行以下命令：

```bash
python -m streamlit run app.py
```

### 访问界面

运行成功后，打开浏览器访问终端中显示的本地地址，通常是 `http://localhost:8501`。

## 功能说明

### 智能代理模式
- 支持自然语言对话，可直接输入问题或指令
- 提供铜合金性能预测功能
- 支持特征选择和分析
- 生成详细的分析报告

### 数据管理
- 支持上传Excel文件进行分析
- 可导出分析结果为Excel文件
- 提供数据可视化功能

### 可视化分析
- 硬度分析（分布、与其他因素的关系）
- 电导率分析
- 合金成分分析
- 工艺参数分析
- 性能预测分析

## 故障排除

### 常见问题

1. **导入失败，使用模拟模式**
   - 检查Python路径设置
   - 确保所有依赖已正确安装
   - 检查.env文件配置

2. **模型文件缺失**
   - 确保 `UI/models/` 目录下存在以下文件：
     - hardness_model.pkl
     - ec_model.pkl
     - q3_model.pkl

3. **API密钥错误**
   - 检查.env文件中的API密钥是否正确
   - 确保网络连接正常

4. **依赖安装失败**
   - 尝试使用 `pip install --upgrade pip` 升级pip
   - 对于特定依赖的安装问题，可以单独安装：
     ```bash
     pip install langchain langchain-core langchain-community
     ```

### 模拟模式说明

当以下情况发生时，系统会自动切换到模拟模式：
- 智能代理模块导入失败
- 模型文件不存在
- API密钥未配置或无效

在模拟模式下，系统会使用预设的算法生成模拟结果，仍然可以使用基本的预测和分析功能。

## 项目结构

```
Agent/
├── UI/              # 智能代理核心模块
│   ├── models/      # 模型文件
│   ├── agent_core.py    # 智能代理核心
│   ├── model_manager.py # 模型管理
│   └── feature_transformer.py # 特征转换
├── user/            # 用户界面
│   ├── app.py       # 主应用
│   ├── requirements.txt # 依赖文件
│   └── start.bat    # 启动脚本
├── feature_engineering_fixed.py # 特征工程
├── .env             # 环境变量配置
└── .env.example     # 环境变量模板
```

## 技术支持

如果遇到问题，请检查以下几点：
1. 确保Python版本符合要求
2. 所有依赖已正确安装
3. 环境变量配置正确
4. 模型文件存在且完整

如果问题仍然存在，请联系技术支持。

## 版本信息

- 版本：v1.0
- 发布日期：2026-03-20
- 适用范围：铜合金性能预测与分析
