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

    # MQL5 compilation
    print("📈 Searching for MetaEditor for MQL5 compilation...")
    me_paths = [
        "C:\\Program Files\\MetaTrader 5\\metaeditor64.exe",
        "C:\\Program Files\\MetaTrader 5\\metaeditor.exe",
        "D:\\Program Files\\MetaTrader 5\\metaeditor64.exe"
    ]
    meta_editor = None
    for p in me_paths:
        if os.path.exists(p):
            meta_editor = p
            break

    if meta_editor:
        print(f"✅ Found MetaEditor at {meta_editor}")
        mql_src = os.path.abspath("src/mql5/Experts")
        for file in os.listdir(mql_src):
            if file.endswith(".mq5"):
                print(f"🛠️ Compiling {file}...")
                try:
                    subprocess.run([meta_editor, f"/compile:{os.path.join(mql_src, file)}", "/log"], check=True)
                except Exception as e:
                    print(f"⚠️ MQL5 compilation failed for {file}: {e}")
    else:
        print("⚠️ MetaEditor not found. MQL5 compilation must be done manually.")

    print("🏁 Pre-compilation phase finished.")

if __name__ == "__main__":
    pre_compile()
