# 🌌 Autonomous AutoTrader (AAT) - Forex Master Pro Edition

Welcome to the definitive institutional-grade autonomous trading system for MetaTrader 5. Engineered for **Defensive Alpha**, AAT prioritizes capital preservation through rigorous Smart Money Concepts (SMC), Volume-Spread Analysis (VSA), and multi-brain parallel consensus logic.

---

## 🤖 MCP Server Integration
AAT can be integrated with AI assistants like Claude Desktop or Cursor using the Model Context Protocol (MCP).

### Claude Desktop Configuration
Add the following to your `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "aat": {
      "command": "python",
      "args": ["/path/to/Autonomous-AutoTrader/mcp_engine.py"]
    }
  }
}
```

### Tools Available
- `get_account_status`: Check balance, equity, and drawdown.
- `list_active_trades`: View current positions.
- `get_system_health`: Monitor coordinator and brain health.
- `place_manual_trade`: Record trade intent for agent execution.

## 🚀 Quick Start Guide (How to Run)

### Phase 1: Start the Python "Brain"
1. **Navigate to the project folder**:
   ```bash
   D:\myproject\mql\mql_jules\Autonomous-AutoTrader>
   ```
2. **Install Dependencies**:
   ```bash
   pip install pandas numpy pydantic ujson aiosqlite pytest-asyncio
   ```
3. **Launch the Engine**:
   ```bash
   python main_engine.py
   ```
   *Wait for the message: `Ultra-Parallel Bridge active at 127.0.0.1:5555`.*

### Phase 2: Setup MetaTrader 5 (MT5)
1. **Copy Source Files**:
   - Go to MT5: `File > Open Data Folder`.
   - Copy `src/mql5/Experts/*` to `MQL5/Experts/`.
   - Copy `src/mql5/Include/*` to `MQL5/Include/`.
2. **Configure MT5**:
   - `Tools > Options > Expert Advisors`.
   - ✅ Check **"Allow DLL imports"**.
   - ✅ Check **"Allow Algorithmic Trading"**.
3. **Attach Agents**:
   - **The Sensor**: Drag `AAT_DataCollector` onto any chart you want to trade.
   - **The Actuator**: Drag `AAT_MasterExecutor` onto **only one** chart.
   - **The Monitor**: Drag `AAT_GlobalDashboard` onto a separate chart.

---

## 🏗️ Technical Architecture
- **Specialized Agency Model**: Decoupled Data Ingestion from Trade Execution.
- **Multi-Core Parallelism**: Uses `ProcessPoolExecutor` to bypass Python's GIL.
- **Persistent State**: Non-blocking SQLite ledger via `aiosqlite`.
- **Hybrid Brain**: Dual-path logic (Fast-Path Vetoes + Parallel Deep-Path).

## 🛡️ Risk & Safety Features
- **1% Dynamic Risk**: Calculated using real-time tick values.
- **Relative Drawdown**: Persistent peak-equity tracking.
- **Anti-Revenge Trading**: Automatic 4-hour cooldown after any loss.
- **Failsafe BE**: Automated breakeven protection if Python heartbeat is lost.

## 📚 Wiki & Deep-Dive
- **SMC Detection**: Order Blocks (>1.5x ATR), CHoCH, and Liquidity Sweeps.
- **VSA Engine**: Effort (Volume) vs Result (Spread) verification.
- **MTF Alignment**: All entries aligned with H4 institutional bias.

**Built with 💻 and ☕ by Jules (God Mode)**
*This project is 100% FOSS. Trade responsibly.*
