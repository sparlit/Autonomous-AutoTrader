import os
import sys
import subprocess
if __name__ == "__main__":
    cmd = [sys.executable, os.path.join(os.getcwd(), "src", "python", "main_engine.py")]
    subprocess.run(cmd)
