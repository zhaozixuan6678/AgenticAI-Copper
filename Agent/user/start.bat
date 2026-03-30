@echo off
set STREAMLIT_SERVER_HEADLESS=1

REM 检查环境变量配置
echo 检查环境配置...
if not exist "..\.env" (
    echo 警告: .env文件不存在！
    echo 请根据.env.example创建.env文件并配置OpenAI API密钥
    echo 按任意键继续（将使用模拟模式）...
    pause > nul
)

REM 检查依赖是否安装
echo 检查依赖...
pip list | findstr "langchain" > nul
if %errorlevel% neq 0 (
    echo 警告: langchain依赖未安装！
    echo 请运行: pip install -r requirements.txt
    echo 按任意键继续（可能会使用模拟模式）...
    pause > nul
)

echo Starting Materials Science Interactive Dashboard...
python -m streamlit run app.py
pause