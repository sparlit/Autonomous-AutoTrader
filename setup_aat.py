import os
import sys
import subprocess
def setup():
    print("🛠️ AAT Production Setup")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
    rust_path = os.path.join("src", "rust")
    if os.path.exists(rust_path):
        print("🦀 Compiling Rust kernels...")
        subprocess.run(["maturin", "develop"], cwd=rust_path, check=True)
    print("✅ Setup complete.")
if __name__ == "__main__": setup()
