# 🪟 Windows 11 PRO: Institutional Installation Guide

Follow these exact steps to deploy the **Autonomous AutoTrader (AAT) Phoenix Ascendant** on your Windows 11 machine.

---

## 🛠️ Step 1: System Prerequisites

Ensure you have the following installed. Run these commands in **PowerShell (Administrator)** to verify:

1. **Python 3.11** (Required for Orchestration):
   ```powershell
   python --version
   # Expected: Python 3.11.x
   ```
2. **Git**:
   ```powershell
   git --version
   ```
3. **Rust Toolchain** (Required for High-Performance Kernels):
   ```powershell
   rustc --version
   ```
   *If not installed, get it from [rustup.rs](https://rustup.rs/).*

---

## 🚀 Step 2: Environment Setup

Run these commands one-by-one in your terminal:

1. **Clone the Repository**:
   ```powershell
   git clone https://github.com/your-repo/Autonomous-AutoTrader.git
   cd Autonomous-AutoTrader
   ```
2. **Initialize Virtual Environment**:
   ```powershell
   python -m venv venv
   .\venv\Scripts\activate
   ```
3. **Install Core Dependencies**:
   ```powershell
   pip install -r requirements.txt
   pip install polars torch scikit-learn xgboost fastapi dearpygui maturin psutil fakeredis
   ```
4. **Compile Performance Kernels (Rust)**:
   ```powershell
   cd src/rust_institutional_core
   maturin develop
   cd ../..
   ```

---

## ⚙️ Step 3: Configuration

1. **Core Settings**: Open `config/main_config.json` and verify:
   ```json
   {
     "bridge": { "host": "127.0.0.1", "port": 5555 },
     "risk": { "daily_loss_limit_pct": 2.0, "max_drawdown_pct": 5.0 },
     "brains": { "consensus_threshold": 75.0 }
   }
   ```
2. **Symbols**: Add your symbols to `config/symbols.json`.

---

## 💹 Step 4: MetaTrader 5 Integration

### A. Deploy Expert Advisors
1. Open MT5.
2. Go to `File > Open Data Folder`.
3. Navigate to `MQL5\Experts\`.
4. Copy all files from the project's `src\mql5\Experts\` into that folder.
5. Navigate to `MQL5\Include\`.
6. Copy all files from the project's `src\mql5\Include\` into that folder.

### B. Compile in MetaEditor
1. Press `F4` in MT5 to open MetaEditor.
2. Find the files in the Navigator on the left.
3. **Right-click each `.mq5` file and select "Compile"**. Ensure 0 errors.

### C. Terminal Configuration
1. In MT5, go to `Tools > Options > Expert Advisors`.
2. ✅ Check **Allow Algorithmic Trading**.
3. ✅ Check **Allow DLL imports**.

---

## 🏃 Step 5: Execution Sequence

You must start the components in this exact order:

1. **Start the Python Brain**:
   ```powershell
   ..\venv\Scripts\python main_engine.py
   ```
   *Wait for: "🌌 Phoenix Ascendant Orchestrator Online."*

2. **Attach MT5 Agents**:
   - Drag `AAT_DataCollector` onto every chart you want to trade.
   - Drag `AAT_MasterExecutor` onto **ONE** chart (any symbol).
   - Drag `AAT_GlobalDashboard` onto a separate blank chart.

---

## 📊 Monitoring
- The **Desktop Dashboard** will open automatically.
- The **Web Dashboard** is available at `http://127.0.0.1:8000`.

**Institutional Support**: Jules (God Mode)
