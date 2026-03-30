import os
import subprocess

# 设置环境变量来跳过邮箱提示
os.environ['STREAMLIT_BROWSER_GATHER_USAGE_STATS'] = 'false'

# 运行Streamlit应用
subprocess.run(['python', '-m', 'streamlit', 'run', 'app.py'])
