import os
import subprocess
import sys

def setup():
    print("🌌 AAT V3.3.0 Institutional Setup")
    print("Step 1: Installing Python Dependencies...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

    print("Step 2: Compiling Rust Institutional Kernels...")
    os.chdir("src/rust")
    subprocess.check_call(["cargo", "build", "--release"])
    os.chdir("../..")

    print("Step 3: Initializing Environment...")
    if not os.path.exists("logs"): os.makedirs("logs")

    print("✅ Setup Complete. Run 'python run_aat.py' to start.")

if __name__ == "__main__":
    setup()
