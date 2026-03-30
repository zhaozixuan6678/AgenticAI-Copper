"""
Materials Science Dashboard Startup Script
"""

import os
import subprocess
import sys
import time

def start_dashboard():
    """Start the Streamlit dashboard"""
    print("Starting Materials Science Interactive Dashboard...")
    print("==============================================")
    
    # Set environment variable for headless mode
    env = os.environ.copy()
    env['STREAMLIT_SERVER_HEADLESS'] = '1'
    
    try:
        # Start Streamlit
        process = subprocess.Popen(
            [sys.executable, '-m', 'streamlit', 'run', 'app.py'],
            cwd=os.path.dirname(os.path.abspath(__file__)),
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        
        print(f"Dashboard started with PID: {process.pid}")
        print("Access the dashboard at: http://localhost:8501")
        print("Press Ctrl+C to stop the dashboard")
        
        # Wait for the process to complete
        process.wait()
        
    except KeyboardInterrupt:
        print("\nDashboard stopped by user.")
    except Exception as e:
        print(f"Error starting dashboard: {e}")

if __name__ == "__main__":
    start_dashboard()
