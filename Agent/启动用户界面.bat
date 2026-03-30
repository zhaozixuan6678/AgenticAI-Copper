@echo off
cls
echo ===============================================
echo 材料科学交互式仪表板一键启动
 echo ===============================================

echo 正在启动用户界面...
echo 应用将在新窗口中启动...
echo 启动完成后将自动打开浏览器...

REM 在新窗口中启动用户界面并设置环境变量
start cmd /k "cd user && set STREAMLIT_SERVER_HEADLESS=1 && echo 启动Streamlit应用... && echo 应用启动后，可以通过以下地址访问： && echo http://localhost:8501 && echo. && echo 按Ctrl+C可以停止应用 && python -m streamlit run app.py"

REM 等待应用启动
ping localhost -n 5 > nul

REM 自动打开浏览器
echo 正在打开浏览器...
start http://localhost:8501

echo 启动完成！
echo 浏览器已自动打开，正在访问应用...
pause