# 📖 User Guide: Trading with Autonomous AutoTrader (AAT)

This guide provides a step-by-step walkthrough for setting up, running, and trading with the AAT system.

## 🛠️ Step 1: Python Environment Setup

AAT requires Python 3.10+ and several high-performance libraries.

1. **Install Dependencies**:
   ```bash
   pip install pandas numpy pydantic ujson aiosqlite fastmcp mcp pytest-asyncio yfinance pyyaml
   ```

2. **Configuration**:
   - Check `config/main_config.json` to set your risk parameters (e.g., `risk_per_trade_pct`, `max_drawdown_pct`).
   - Add symbols you wish to trade in `config/symbols.json`.

---

## 🏗️ Step 2: MetaTrader 5 (MT5) Configuration

AAT uses a **Coordinator-Agent** model. The Python code is the Coordinator, and the MQL5 scripts are the Agents.

1. **Deploy MQL5 Files**:
   - Open MT5 and go to `File > Open Data Folder`.
   - Copy everything from `src/mql5/Experts/` to the `MQL5/Experts/` folder in your data directory.
   - Copy everything from `src/mql5/Include/` to the `MQL5/Include/` folder in your data directory.

2. **Terminal Settings**:
   - Go to `Tools > Options > Expert Advisors`.
   - ✅ **Allow algorithmic trading**.
   - ✅ **Allow DLL imports** (Required for the socket bridge).

3. **Attach Agents to Charts**:
   - **AAT_DataCollector**: Attach this to every symbol chart you want to trade (e.g., EURUSD M1). It sends data to the Python Brain.
   - **AAT_MasterExecutor**: Attach this to **ONLY ONE** chart. It listens for trade commands from the Python Brain and executes them.
   - **AAT_GlobalDashboard**: Attach this to a separate chart to monitor system health and risk telemetry in real-time.

---

## 🚀 Step 3: Running the App

### Mode A: Fully Autonomous Trading
Use this mode to let the system trade for you using its built-in SMC and VSA logic.

1. **Start the Engine**:
   ```bash
   python main_engine.py
   ```
2. The system will start listening for data from your MT5 DataCollectors. When a high-probability setup (SMC + VSA + Trend) is found, it will automatically send execution orders to your MasterExecutor.

### Mode B: AI-Assisted Trading (MCP)
Use this mode to interact with AAT using an AI assistant like Claude or Cursor.

1. **Start the MCP Server**:
   ```bash
   python mcp_engine.py
   ```
2. **Connect to Claude Desktop**:
   Add the configuration provided in the `README.md` to your `claude_desktop_config.json`.
3. **Trading with AI**:
   Ask Claude:
   - "What is my current account status?"
   - "Are there any active trades?"
   - "Buy 0.01 lots of GBPUSD with SL at 1.2500."

---

## 🛡️ How to Trade Safely

1. **Demo First**: Always run AAT on a demo account for at least 2 weeks to understand its behavior.
2. **The 1% Rule**: The system is hardcoded to risk a percentage of your equity per trade. Ensure your `main_config.json` reflects your risk tolerance.
3. **News Safety**: AAT will automatically VETO trades 30 minutes before and after high-impact news if they are listed in `config/news_schedule.json`.
4. **Drawdown Protection**: If your drawdown exceeds the limit set in configuration, the system will halt all trading until the next day or until reset.
5. **Failsafe**: If the Python Brain crashes, the MT5 Agents will enter "Failsafe Mode," moving stops to breakeven for any profitable trades.

---

**Happy Trading!**
*Remember: Capital preservation is the first priority.*
