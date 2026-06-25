import compileall
import subprocess
import os
import sys

def pre_compile():
    print("🚀 Starting Pre-compilation Phase...")

    # Python compilation
    print("📦 Compiling Python bytecode...")
    compileall.compile_dir('src/python', force=True)
    print("✅ Python compilation complete.")

    # Rust compilation
    rust_dir = 'src/rust_institutional_core'
    if os.path.exists(rust_dir):
        print(f"🦀 Compiling Rust Institutional Core in {rust_dir}...")
        try:
            # Check if cargo is available
            subprocess.run(['cargo', '--version'], check=True, capture_output=True)
            subprocess.run(['cargo', 'build', '--release'], cwd=rust_dir, check=True)
            print("✅ Rust compilation complete.")
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f"⚠️ Rust compilation skipped or failed: {e}")
    else:
        print("⚠️ Rust directory not found. Skipping.")

    print("🏁 Pre-compilation phase finished.")

if __name__ == "__main__":
    pre_compile()
