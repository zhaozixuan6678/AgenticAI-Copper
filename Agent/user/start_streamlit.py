import subprocess
import os

# 确保当前目录是脚本所在目录
os.chdir(os.path.dirname(os.path.abspath(__file__)))

print("启动材料科学交互式仪表盘...")
print("请稍候，正在加载应用...")

# 运行Streamlit应用，通过stdin提供空输入
process = subprocess.Popen(
    ['python', '-m', 'streamlit', 'run', 'app.py'],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

# 提供空输入跳过邮箱提示
output, error = process.communicate(input='\n', timeout=30)

# 打印输出
print(output)

if error:
    print("错误信息:")
    print(error)

print("\n应用启动完成！")
print("请在浏览器中打开Local URL访问仪表盘。")
