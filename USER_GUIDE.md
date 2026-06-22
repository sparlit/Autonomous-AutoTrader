# 📖 Institutional User Guide: Phoenix Ascendant (V2.3.0)

Welcome to the definitive guide for running the **Autonomous AutoTrader (AAT)**. This system is designed for **Defensive Alpha**, prioritizing capital preservation through multi-process consensus and rigorous risk management.

---

## 🛠️ 1. Installation & Setup

For a detailed Windows 11 PRO step-by-step guide, please refer to [INSTALL_WINDOWS.md](INSTALL_WINDOWS.md).

### A. Prerequisites
- **OS**: Windows 10/11 (Recommended for MT5) or Linux (for Brain-only hosting).
- **Python**: 3.10 or 3.11 (3.13+ for free-threaded builds if supported).
- **Rust**: Latest stable toolchain (required for performance kernels).
- **MetaTrader 5**: Installed and logged into a demo or live account.
- **Git**: For repository management.

### B. Environment Preparation
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-repo/Autonomous-AutoTrader.git
   cd Autonomous-AutoTrader
   ```
2. **Setup Python Virtual Environment**:
   ```powershell
   python -m venv venv
   .\venv\Scripts\activate
   ```
3. **Install Core Dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install polars torch scikit-learn xgboost fastapi dearpygui maturin
   ```
4. **Compile Performance Kernels**:
   ```bash
   cd src/rust_core && maturin develop
   cd ../rust_heavy && maturin develop
   cd ../..
   ```

---

## ⚙️ 2. Configuration

### A. System Configuration (`config/main_config.json`)
Adjust the core system parameters before launching:
- **`bridge`**: Set the `host` (default `127.0.0.1`) and `port` (default `5555`).
- **`risk`**:
  - `daily_loss_limit_pct`: Max % loss before shutdown (default 2.0).
  - `max_drawdown_pct`: Absolute drawdown limit (default 5.0).
  - `risk_per_trade_pct`: Risk per individual setup (default 1.0).
- **`brains`**: `consensus_threshold` (default 0.7) determines required strategy agreement.

### B. Symbol Selection (`config/symbols.json`)
Define the list of symbols you wish to monitor. Ensure they are available in your MT5 Market Watch.

---

## 🚀 3. Execution Sequence

### Step 1: Start the Python "Brain"
Launch the orchestrator first to listen for incoming agent connections:

python main_engine.py

*Wait for the message: `🌌 Phoenix Ascendant Orchestrator Online.`*

### Step 2: MetaTrader 5 Integration
1. **Copy Files**:
   - Copy all files from `src/mql5/Experts/` to your MT5 `MQL5/Experts/` folder.
   - Copy all files from `src/mql5/Include/` to your MT5 `MQL5/Include/` folder.
2. **Compile**: Open MetaEditor (F4 in MT5), find the copied files, and click **Compile** for each.
3. **Terminal Settings**:
   - `Tools > Options > Expert Advisors`.
   - ✅ **Allow DLL imports**.
   - ✅ **Allow Algorithmic Trading**.

### Step 3: Attach MT5 Agents
1. **The Sensor (`AAT_DataCollector`)**: Drag this onto every chart you want to trade (e.g., EURUSD, GBPUSD).
2. **The Actuator (`AAT_MasterExecutor`)**: Drag this onto **exactly one** chart. This EA handles all order execution.
3. **The Monitor (`AAT_GlobalDashboard`)**: Drag this onto a separate chart for localized visual telemetry.

---

## 📊 4. Monitoring & Management

### Triple-Dashboard Interface
1. **Native Desktop**: Automatic popup via Dear PyGui when `main_engine.py` starts.
2. **Web Interface**: Accessible via `http://localhost:8000` (FastAPI).
3. **MT5 Overlay**: Real-time CCanvas rendering on the Dashboard chart.

### MCP Interaction
AAT supports the **Model Context Protocol**. Use an MCP-compatible client to:
- `get_system_status`: Real-time health and equity report.
- `emergency_stop`: Immediate closure of all positions and system freeze.
- `adjust_risk`: Change risk parameters on the fly.

---

## 🛡️ 5. Safety Protocols
- **4-Hour Cooldown**: Automatically triggered after any realized loss to prevent revenge trading.
- **Heartbeat Failsafe**: MT5 agents will move Stop-Loss to Breakeven if the connection to Python is lost for > 30 seconds.
- **SYNC Protocol**: Every time an agent connects, it reconciles MT5 tickets with the persistent Python ledger.

**Built with 💻 and ☕ by Jules (God Mode)**
*Trade responsibly. Consistency is the only Holy Grail.*
