import sys
import os
import argparse
import subprocess
import asyncio
import logging
import psutil
import io
import compileall

# Ensure project root is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.python.hive.coordinator import HiveOrchestrator
from src.python.hive.security import CredentialManager

# 10001: Force UTF-8 encoding for Windows Console
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def setup():
    print("🌌 AAT V3.3.0 Institutional Setup")
    print("Step 1: Installing Python Dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        subprocess.check_call([sys.executable, "-m", "pip", "install", "maturin", "pywin32", "cryptography", "pandas", "psutil", "ujson", "aiosqlite", "fastapi", "uvicorn", "websockets", "dearpygui"])
    except Exception as e:
        print(f"Dependency installation failed: {e}")

    print("Step 2: Compiling Rust Institutional Kernels...")
    rust_dir = "src/rust_institutional_core"
    if os.path.exists(rust_dir):
        os.chdir(rust_dir)
        try:
            subprocess.check_call(["maturin", "develop", "--release"])
            print("✅ Rust Institutional Core installed via Maturin.")
        except Exception:
            try:
                subprocess.check_call(["cargo", "build", "--release"])
                print("✅ Rust Institutional Core compiled via Cargo.")
            except Exception as e:
                print(f"⚠️ Rust compilation failed: {e}")
        os.chdir("../..")
    else:
        print("⚠️ Rust directory not found.")

    print("Step 3: Pre-compiling Bytecode...")
    compileall.compile_dir('src/python', force=True)

    print("Step 4: Initializing Environment...")
    if not os.path.exists("logs"): os.makedirs("logs")

    print("\n✅ Setup Complete. Run 'python aat.py run' to start.")

def set_creds():
    print("🔐 AAT Credential Manager")
    account = input("Enter MT5 Account ID: ")
    password = input("Enter MT5 Password: ")
    server = input("Enter MT5 Server: ")

    vault = CredentialManager()
    vault.save_credentials(account, password, server)
    print("✅ Credentials encrypted and stored.")

def setup_os_optimization():
    p = psutil.Process(os.getpid())
    try:
        if psutil.cpu_count() > 0:
            p.cpu_affinity([0])
            logging.info("Supervisor pinned to CPU 0")
    except Exception as e:
        logging.warning(f"OS Optimization failed: {e}")

async def run():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - AAT_Supervisor - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(), logging.FileHandler("logs/aat_system.log")]
    )

    if not os.path.exists("logs"): os.makedirs("logs")

    print("🌌 Launching Autonomous AutoTrader: Phoenix Gauntlet V3.3.0")
    setup_os_optimization()

    vault = CredentialManager()
    creds = vault.load_credentials()
    if creds:
        logging.info(f"Vault unlocked for Account: {creds.get('account')}")
    else:
        logging.warning("Vault is empty. Manual login required in MT5 or use 'python aat.py set-creds'")

    orchestrator = HiveOrchestrator(credentials=creds)

    try:
        await orchestrator.run()
    except KeyboardInterrupt:
        logging.info("Initiating Graceful Shutdown...")
        orchestrator.stop()
        logging.info("Phoenix Gauntlet offline.")

def test():
    print("🧪 Running AAT Integration Test Suite...")
    test_dir = "archive/tests"
    if not os.path.exists(test_dir):
        print("❌ Test directory not found in archive.")
        return

    try:
        subprocess.check_call([sys.executable, "-m", "pytest", f"{test_dir}/python/test_ipc.py", f"{test_dir}/python/test_brains.py", f"{test_dir}/python/test_coordinator.py", f"{test_dir}/test_v3_3_merge.py"])
    except subprocess.CalledProcessError:
        print("❌ Tests failed.")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AAT Phoenix Gauntlet CLI")
    parser.add_argument("command", choices=["setup", "run", "set-creds", "test", "set-lot"], help="Command to execute")

    args = parser.parse_args()

    if args.command == "setup":
        setup()
    elif args.command == "run":
        asyncio.run(run())
    elif args.command == "set-creds":
        set_creds()
    elif args.command == "set-lot":
        import json
        lot = float(sys.argv[2]) if len(sys.argv) > 2 else 0.01
        path = "config/institutional_settings.json"
        if os.path.exists(path):
            with open(path, "r") as f: data = json.load(f)
            data["standard_lot_size"] = lot
            with open(path, "w") as f: json.dump(data, f, indent=4)
            print(f"✅ Lot size updated to {lot}")
    elif args.command == "test":
        test()
