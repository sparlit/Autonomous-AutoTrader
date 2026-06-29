# AAT Phase 1: Chart Analyst & AutoTrader Handover

## 🚀 System Architecture
The system uses a **Multi-Brain Coordinator/Agent** model:
- **Hive Coordinator (Python)**: Manages specialized brains and risk.
- **SMC Analyst**: Detects Order Blocks, CHoCH, and Fair Value Gaps.
- **Consensus Engine**: Implements the "3 of 4" confluence rule (Trend, Momentum, Structure, Volatility).
- **Risk Manager**: Handles session filters (London/NY), news safety, and daily trade limits.
- **MT5 Agent**: Pushes MTF data to Python and executes trades with visual feedback.

## 🛠 Features Implemented
- **SMC Integration**: Automatic detection of institutional zones.
- **Visual Feedback**: Detected Order Blocks are drawn directly on your MT5 chart as rectangles.
- **Multi-Brain Processing**: Parallel analysis of HTF trend, LTF triggers, and global consensus.
- **Risk Hardening**: Trade rejection based on session, news (placeholder), and overtrading rules.

## 📋 How to Run
1. **Python Side**:
   ```bash
   pip install pandas numpy pydantic ujson pytest-asyncio
   python src/python/hive/coordinator.py
   ```
2. **MT5 Side**:
   - Compile `src/mql5/Experts/AAT_TradeExecutor.mq5`.
   - Attach to your desired chart (e.g., EURUSD).
   - Ensure "Allow DLL imports" is enabled.

## 🧪 Verification
Run the python test suite:
```bash
python -m pytest tests/python/test_aat_system.py
```
