import subprocess
import os

# 确保当前目录是脚本所在目录
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# 运行Streamlit应用
print("启动材料科学交互式仪表盘...")
print("请稍候，正在加载应用...")

# 使用subprocess运行Streamlit，捕获输出
process = subprocess.Popen(
    ['python', '-m', 'streamlit', 'run', 'app.py'],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

# 实时输出
for line in process.stdout:
    print(line.strip())
    if "Local URL" in line:
        print("\n应用已成功启动！")
        print("请在浏览器中打开上述Local URL访问仪表盘。")

# 等待进程结束
process.wait()
