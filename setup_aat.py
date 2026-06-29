import os
import subprocess
import sys

def setup():
    print("🌌 AAT V3.3.0 Institutional Setup")
    print("Step 1: Installing Python Dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    except Exception as e:
        print(f"Dependency installation failed: {e}")

    print("Step 2: Compiling Rust Institutional Kernels...")
    rust_dir = "src/rust_institutional_core"
    if os.path.exists(rust_dir):
        os.chdir(rust_dir)
        try:
            # Try maturin first for Python linking
            subprocess.check_call(["maturin", "develop"])
            print("✅ Rust Institutional Core installed via Maturin.")
        except Exception:
            try:
                # Fallback to standard cargo build
                subprocess.check_call(["cargo", "build", "--release"])
                print("✅ Rust Institutional Core compiled via Cargo.")
            except Exception as e:
                print(f"⚠️ Rust compilation failed: {e}")
        os.chdir("../..")
    else:
        print("⚠️ Rust directory not found.")

    print("Step 3: Initializing Environment...")
    if not os.path.exists("logs"): os.makedirs("logs")

    print("✅ Setup Complete. Run 'python main_engine.py' or 'python run_aat.py' to start.")

if __name__ == "__main__":
    setup()
